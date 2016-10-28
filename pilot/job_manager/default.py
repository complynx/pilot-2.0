from common.switchable_sig import SwitchableWithSignals
from common.signalslot import Signal
from common.async_decorator import async
import logging


class JobManagerDefault(SwitchableWithSignals):
    definition = None
    communicator = None
    queue = None
    state_changed = Signal()
    started = Signal()
    finished = Signal()
    log = logging.getLogger('job.class')
    __definition_aliases = {
        'id': 'job_id'
    }
    __state = "sent"

    def __getattr__(self, item):
        """
        Reflection of description values into Job instance properties if they are not shadowed.
        If there is no own property with corresponding name, the value of Description is used.
        Params and return described in __getattr__ interface.
        """
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            if self.definition is not None:
                if item in self.__definition_aliases:
                    return self.definition[self.__definition_aliases[item]]
                if item in self.definition:
                    return self.definition[item]
            raise

    def __setattr__(self, key, value):
        """
        Reflection of description values into Job instance properties if they are not shadowed.
        If there is no own property with corresponding name, the value of Description is set.
        Params and return described in __setattr__ interface.
        """
        try:
            object.__getattribute__(self, key)
            object.__setattr__(self, key, value)
        except AttributeError:
            if self.definition is not None:
                if key in self.__definition_aliases:
                    self.definition[self.__definition_aliases[key]] = value
                elif key in self.definition:
                    self.definition[key] = value
                return
            object.__setattr__(self, key, value)

    def setup(self, definition, queue):
        self.definition = definition
        self.log = logging.getLogger('job.%d' % self.id)
        self.queue = queue
        self.communicator = queue.communicator
        self.communicator.got_job_state.connect(self.interface.got_state_from_server)
        self.state_changed.connect(self.communicator.send_job_state)

    def got_state_from_server(self, state_info):
        if self.id == state_info['job_id']:
            self.log.info(state_info)

    def __repr__(self):
        return "<job.{job_id} ({label}) {home_package} ({state})>".format(state=self.state, **self.definition)

    @property
    def state(self):
        """
        :return: Last job state
        """
        return self.__state

    @state.setter
    def state(self, value):
        """
        Sets new state and updates server.

        :param value: new job state.
        """
        if value != self.__state:
            self.log.info("Setting job state of job %s to %s" % (self.id, value))
            self.__state = value
            self.state_changed.async(self.interface)

    def stage_in(self):
        """
        Stages in files using Rucio.
        """
        self.state = 'stagein'

    def stage_out(self):
        """
        Stages out files using Rucio.
        """
        self.state = 'stageout'
        # self.prepare_log()

    def payload_run(self):
        """
        Runs payload.
        """
        self.state = 'running'

        self.state = "holding"

    @async
    def start(self):
        self.started.async()
        self.state = 'starting'

        self.stage_in()
        self.payload_run()
        self.stage_out()

        self.state = 'finished'
        self.finished.async()
