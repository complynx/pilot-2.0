"""
This is the main entrance point.
"""
from pilot import PilotInterface
import sys
from common import signalling


def signal_receiver(sig, frame):
    if pilot is not None:
        pilot.signal_receiver(sig, frame)

if __name__ == "__main__":
    pilot = PilotInterface()
    pilot.setup_arguments(sys.argv)
    signalling.signal_all_setup(signal_receiver)
    pilot.run()
