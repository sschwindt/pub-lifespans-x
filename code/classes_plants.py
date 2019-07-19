# !/usr/bin/python
# Desc.: Provides classes
import sys, os

# import own functions -- make sure that all *.py files are in the same folder
sys.path.append(os.path.dirname(os.path.abspath(__file__))) # add this folder to the system path

class BoxElder():
    # This is the BoxElder class.
    # __call__()

    def __init__(self):
        self.parameter_list = ["h", "taux", "d2w"] # governs analysis HIERARCHY!
        self.threshold_d2w_low = 3  # ft
        self.threshold_d2w_up = 6   # ft
        self.threshold_h = 1        # dummy value to access everything larger than zero
        self.threshold_taux = 0.047 # (--)
    def __call__(self):
        pass


class Cottonwood():
    # This is the Cottonwood class.
    # __call__()

    def __init__(self):
        self.parameter_list = ["h", "u", "tcd", "d2w"] # governs analysis HIERARCHY!
        self.threshold_d2w_low = 5          # ft
        self.threshold_d2w_up = 10          # ft
        self.threshold_fill = 0.8 * 1.4 * 6 # ft if stem height = 1.4 ft (i.e. cutting height of 7 ft) over 6 years
        self.threshold_h = 1.5 * 1.4        # ft if stem length = 1.4 ft (i.e. cutting height of 7 ft)
        self.threshold_scour = 0.1 * 0.8 * 7 * 6# ft if root length = 5.6 ft (i.e. cutting height of 7 ft) over 6 years
        self.threshold_u = 3.0              # fps
    def __call__(self):
        pass

class WhiteAlder():
    # This is the Willow class.
    # __call__()

    def __init__(self):
        self.parameter_list = ["mobile_grains", "scour", "d2w"] # governs analysis HIERARCHY!

        self.threshold_d2w_low = 1  # ft
        self.threshold_d2w_up = 5   # ft
        self.threshold_scour = 6    # ft * 6 yrs
        self.threshold_taux = 0.047 # (--) for grain mobility
    def __call__(self):
        pass

class Willow():
    # This is the Willow class.
    # __call__()

    def __init__(self):
        self.parameter_list = ["h", "taux", "scour", "d2w"] # governs analysis HIERARCHY!
        self.threshold_d2w_low = 3      # ft
        self.threshold_d2w_up = 5       # ft
        self.threshold_h = 1.4 + 0.7    # ft if stem length = 1.4 ft (i.e. cutting height of 7 ft)
        self.threshold_scour = 0.1 * 0.8 * 7 * 6  # ft * 6years
        self.threshold_taux = 0.1       # (--)
    def __call__(self):
        pass





