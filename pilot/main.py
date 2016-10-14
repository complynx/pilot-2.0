"""
This is the main entrance point.
"""
from pilot.interface import PilotInterface
import sys


if __name__ == "__main__":
    pilot = PilotInterface()
    pilot.setup_arguments(sys.argv)
    pilot.run()
