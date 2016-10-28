from common.switchable_sig import SwitchableWithSignals
from common.signalslot import Signal
from common.async_decorator import async
import tempfile
import shutil


class SlotWorkerDefault(SwitchableWithSignals):
    payload_finished = Signal()
    files_pushed = Signal()
    files_fetched = Signal()
    folder = None
    job = None
    empty = Signal()

    def set_job(self, job):
        self.job = job
        job.finished.connect(self.job_finished)

    def job_finished(self):
        self.job = None
        self.cleanup()
        self.empty()

    def create_folder(self):
        self.folder = tempfile.mkdtemp("", "slot_folder", '.')
        pass

    def cleanup(self):
        if self.folder:
            shutil.rmtree(self.folder)

    @async
    def push_files(self, files):
        [shutil.move(fn, self.folder) for fn in files]
        self.files_pushed()

    @async
    def fetch_files(self, files):
        self.files_fetched()

    @async
    def run_payload(self, script="", env=None, **kwargs):
        pass

    def run(self):
        self.job.start()
