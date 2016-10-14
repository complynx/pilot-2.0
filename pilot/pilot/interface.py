from switchables import Switchable, Interface
import sys
import os
import argparse
import pipes
from core.common import LoggingContext
import logging


class PilotAbstract(Switchable):
    argv = []
    unresolved_arguments = []
    argument_parser = None
    info = {'user_agent': 'Pilot/2.0'}
    args = None
    log = None

    def __init__(self, interface, previous=None):
        Switchable.__init__(self, interface, previous)
        if previous is None:
            self.init()
        else:
            self.copy_previous(previous)
        self.setup_argparser()

        if previous is not None and previous.args is not None:
            self.setup_arguments(self.argv)

    def print_initial_information(self):
        """
        Pilot is initialized somehow, this initialization needs to be print out for information.
        :return:
        """
        log = self.log
        if self.args is not None:
            log.info("Pilot is running.")
            log.info("Started with: %s" % " ".join(pipes.quote(x) for x in self.argv))
        log.info("User-Agent: " + self.info['user_agent'])
        log.info("Node name: " + self.info['node_name'])
        log.info("Pilot ID: " + self.info['pilot_id'])

        log.info("Pilot is started from %s" % self.info['pilot_dir'])
        log.info("Current working directory is %s" % os.getcwd())

        req_file = os.path.join(self.info['pilot_dir'], "..", "tools", "pip-requires")
        if os.path.isfile(req_file):
            log.info("Printing requirements versions...")
            with LoggingContext(logging.getLogger(), logging.INFO):  # removes debug messages of pip
                try:
                    import pip
                    requirements = pip.req.parse_requirements(req_file, session=False)
                    for req in requirements:
                        log.info("%s (%s)" % (req.name, req.installed_version))
                except TypeError:
                    log.warn("Outdated version of PIP? Have you set up your environment properly? Skipping module info"
                             "test...")
                    log.warn("Pilot may crash at any time, be aware. And I can't provide you with module information,"
                             "probably the crash is caused by some unsupported module version.")

    def __switch__(self):
        Switchable.__switch__(self)

    def __switched__(self):
        Switchable.__switched__(self)

    def init(self):
        import __main__
        import socket
        import platform
        self.info['startup_dir'] = os.path.abspath(os.getcwd())
        self.info['pilot_dir'] = os.path.dirname(os.path.abspath(__main__.__file__))
        self.info['user_agent'] += " (Python %s; %s %s; rv:alpha) pilot/daniel" % \
                                   (sys.version.split(" ")[0],
                                    platform.system(), platform.machine())
        self.info['node_name'] = socket.gethostbyaddr(socket.gethostname())[0]
        if "_CONDOR_SLOT" in os.environ:
            self.info['node_name'] = os.environ.get("_CONDOR_SLOT", '') + "@" + self.info['node_name']

        self.info['pilot_id'] = self.info['node_name'] + (":%d" % os.getpid())
        self.log = logging.getLogger('pilot')

    def copy_previous(self, previous):
        for i in ['info', 'argv', 'log']:
            setattr(self, i, getattr(previous, i))

    def userproxy_file_standard_path(self):
        base = None
        try:
            base = '/tmp/x509up_u%s' % str(os.getuid())
        except AttributeError:
            # Wow, not UNIX. Nevermind, skip.
            pass

        return os.environ.get('X509_USER_PROXY', base)

    def setup_argparser(self):
        qdata = os.path.join(self.info['startup_dir'], "queuedata.json")
        qdata = qdata if os.path.isfile(qdata) else None
        import logging.config

        self.argument_parser = argparse.ArgumentParser(description="This is pilot.")

        self.argument_parser.add_argument("--logconf", type=logging.config.fileConfig,
                                          default=os.path.join(self.info['pilot_dir'], "loggers.ini"),
                                          help="specify logger parameters file", metavar="path/to/loggers.ini")
        self.argument_parser.add_argument("--cacert", default=self.userproxy_file_standard_path(),
                                          type=lambda x: x if os.path.isfile(x) else None,
                                          help="specify CA certificate or path for your transactions to server",
                                          metavar="path/to/your/certificate")
        self.argument_parser.add_argument("--capath", default=os.environ.get('X509_CERT_DIR',
                                                                             '/etc/grid-security/certificates'),
                                          help="specify CA path for certificates",
                                          metavar="path/to/certificates/")
        self.argument_parser.add_argument("--pandaserver", default="pandaserver.cern.ch",
                                          help="Panda server web address.",
                                          metavar="panda.example.com")
        self.argument_parser.add_argument("--jobserver", default="aipanda007.cern.ch",
                                          help="Panda job server web address.",
                                          metavar="pandajob.example.com")
        self.argument_parser.add_argument("--pandaserver_port", default=25085,
                                          type=int,
                                          help="Panda server port.",
                                          metavar="PORT")
        self.argument_parser.add_argument("--jobserver_port", default=25443,
                                          type=int,
                                          help="Panda job server port.",
                                          metavar="PORT")
        self.argument_parser.add_argument("--queuedata", default=qdata,
                                          type=lambda x: x if os.path.isfile(x) else qdata,
                                          help="Preset queuedata file.",
                                          metavar="path/to/queuedata.json")
        self.argument_parser.add_argument("--queue", default='',
                                          help="Queue name",
                                          metavar="QUEUE_NAME")
        self.argument_parser.add_argument("--loglevel", default=None,
                                          choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                                          help="Set logging level",
                                          metavar="LVL")
        self.argument_parser.add_argument("--job_tag", default='prod',
                                          help="Job type tag. Eg. test, user, prod, etc...",
                                          metavar="tag")
        self.argument_parser.add_argument("--job_description", default=None,
                                          type=lambda x: x if os.path.isfile(x) else None,
                                          help="Job description file, preloaded from server. The contents must be JSON",
                                          metavar="tag")
        self.argument_parser.add_argument("--no_job_update", action='store_true',
                                          help="Disable job server updates")
        self.argument_parser.add_argument("--simulate_rucio", action='store_true',
                                          help="Disable rucio, just simulate")

    def setup_arguments(self, argv):
        self.argv = argv
        self.args, self.unresolved_arguments = self.argument_parser.parse_known_args(self.argv)
        if self.args.loglevel is not None:
            self.log.setLevel(getattr(logging, self.args.loglevel))

    def run(self):
        self.print_initial_information()


class PilotInterface(Interface):
    def __init__(self):
        Interface.__init__(self, PilotAbstract)
