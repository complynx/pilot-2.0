"""
This is the main entrance point.
"""
from pilot import Pilot
import sys

if __name__ == "__main__":
    pilot = Pilot(sys.argv)
    pilot.start()
    pilot.join()
