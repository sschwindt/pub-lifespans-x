# !/usr/bin/python
# Desc.: Provides classes
import logging
from classes_plants import *

# import own functions -- make sure that all *.py files are in the same folder



class Backwater():
    # This is the Backwater feature class.
    # __call__()

    def __init__(self):
        self.ds = False # needed to identify if design map applies
        self.lf = True  # needed to identify if lifespan map applies
        self.mu_bad = []
        self.mu_good = ["agriplain", "backswamp", "mining pit", "pond", "pool", "slackwater", "swale"]
        self.mu_method = 1  # 0 = apply mu_bad list and 1 = apply mu_good list
        self.parameter_list = ["u", "mobile_grains", "tcd", "mu"]  # governs analysis HIERARCHY!
        self.threshold_fill = 0.1*6 # (ft)
        self.threshold_freq = 4.7   # (years)
        self.threshold_scour = 0.1*6# (ft)
        self.threshold_taux = 0.047 # (--) if too low, needed
        self.threshold_u = 0.1      # (fps)
    def __call__(self):
        pass

class ELJ():
    # This is the ELJ feature class.
    # __call__()
    def __init__(self):
        self.ds = True # needed to identify if design map applies
        self.lf = True  # needed to identify if lifespan map applies
        self.mu_bad = ["tributary channel", "tributary delta"]
        self.mu_good = ["riffle", "riffle transition", "pool", "floodplain", "island floodplain", "lateral bar",
                        "medial bar", "run"]
        self.mu_method = 0          # 0 = apply mu_bad list and 1 = apply mu_good list
        self.parameter_list = ["h", "Fr", "mu", "ds_wood"]  # governs analysis HIERARCHY!
        self.threshold_Fr = 1       # (--) critical flow condition
        self.threshold_freq = 20.0   # (yrs) for design map acccording to ruiz-villanueva et al. (2016)
        self.threshold_h = 1.7 * 2  # (ft) if log diameter = 2 ft, cFi. USACE and HDR (2017)

    def __call__(self):
        pass



class Finesediment():
    # This is the Finesediment feature class.
    # __call__()

    def __init__(self):
        # IDEA: only makes sense where plantings may require this?
        self.ds = True  # needed to identify if design map applies
        self.lf = True  # needed to identify if lifespan map applies
        self.parameter_list = ["taux", "fine_grains", "tcd", "d2w", "ds_filter"]  # governs analysis HIERARCHY!
        self.threshold_d2w_low = 1  # (ft)
        self.threshold_d2w_up = 10  # (ft)
        self.threshold_Dmaxf = 0.08 # (in) maximum grain size for "fines"
        self.threshold_fill = 0.8 * 1.4 * 6  # (ft) max fill of Cottonwood
        self.threshold_scour = 6    # (ft) max scour for WhiteAlder
        self.threshold_taux = 0.03  # (--)
    def __call__(self):
        pass

class Grading():
    # This is the Bar and Floodplain lowering feature class.
    # __call__()

    def __init__(self):
        self.ds = False # needed to identify if design map applies
        self.lf = True  # needed to identify if lifespan map applies
        self.inverse_tcd = True     # if True: inverse use of tcd thresholds
        self.parameter_list = ["mobile_grains", "taux", "scour", "d2w"]  # governs analysis HIERARCHY!
        self.threshold_d2w_low = 7  # (ft) USACE and HDR 2016
        self.threshold_d2w_up = 12  # (ft) USACE and HDR 2016
        self.threshold_freq = 4.7   # (years)
        self.threshold_scour = 0.1*6# (ft) scour too low for terrain change
        self.threshold_taux = 0.047 # (--) if too low, needed
    def __call__(self):
        pass

class Gravel():
    # This is the Sediment replenishment feature class.
    # __call__()

    def __init__(self):
        self.ds = True  # needed to identify if design map applies
        self.lf = True  # needed to identify if lifespan map applies
        self.parameter_list = ["mobile_grains", "scour", "ds_stable_grains"]  # governs analysis HIERARCHY!
        self.threshold_freq = 1.0
        self.threshold_scour = 6    # (ft) scour too low for terrain change
        self.threshold_taux = 0.047 # (--) if too low, needed
    def __call__(self):
        pass


class Plantings(Cottonwood, BoxElder, Willow, WhiteAlder):
    # This is the Vegetation Plantings feature class.
    # __call__()

    def __init__(self, species):
        #if type(species == "tuple"):
        #    species = species[0]
        # logger = logging.getLogger("feature_analysis")
        # logger.info("* *  * *   * *   * *   * *   * *   * *   * *   * *")
        # logger.info("> Subfeature: "+species)
        # logger.info("* *  * *   * *   * *   * *   * *   * *   * *   * *")
        self.lf = True  # needed to identify if lifespan map applies
        self.ds = False # needed to identify if design map applies
        if species == 'boxelder':
            BoxElder.__init__(self)
        if species == 'cottonwood':
            Cottonwood.__init__(self)
        if species == 'whitealder':
            WhiteAlder.__init__(self)
        if species == 'willow':
            Willow.__init__(self)
    def __call__(self):
        pass

class Riprap():
    # This is the Riprap feature class.
    # __call__()

    def __init__(self):
        self.ds = True  # needed to identify if design map applies
        self.lf = True  # needed to identify if lifespan map applies
        self.parameter_list = ["taux", "scour", "ds_stable_grains"]
        self.sf = 1.3   # (--) safety factor
        self.threshold_freq = 20.0  # float(years) return period required for resistance-allowed: 1.2,2.5,4.7,12.7,20.0
        self.threshold_scour = 6    # (ft) more than one ft per year
        self.threshold_taux = 0.047 # (--)
    def __call__(self):
        pass

class Sidecavity():
    # This is the Sidecavity feature class.
    # __call__()

    def __init__(self):
        self.ds = True  # needed to identify if design map applies
        self.lf = False # needed to identify if lifespan map applies

        self.inverse_tcd = True  # if True: inverse use of tcd thresholds
        self.mu_bad = []
        self.mu_good = ["bank", "cutbank", "lateral bar", "spur dike", "tailings"]
        self.mu_method = 1  # 0 = apply mu_bad list and 1 = apply mu_good list
        self.parameter_list = ["tcd", "mu"]
        self.threshold_fill = 6 # (ft) only less than 1 ft per year is good for sidecavity (sedimentation!)
        self.threshold_scour = 100 # (ft) dummy value: fill inaccurate for sidecavities
    def __call__(self):
        pass

class Sidechannel():
    # This is the Sidechannel feature class.
    # __call__()

    def __init__(self):
        self.ds = False  # needed to identify if design map applies
        self.lf = True # needed to identify if lifespan map applies
        self.inverse_tcd = True  # if True: inverse use of tcd thresholds
        self.parameter_list = ["taux", "fill", "sidech"]#, "ds_compare_slopes"]
        self.threshold_taux = 0.047
        self.threshold_fill = 6 # (ft) corresponds to less than 1 ft per year

    def __call__(self):
        pass


class Widen():
    # This is the Berm setback / widening feature class.
    # __call__()
    def __init__(self):
        self.ds = True     # needed to identify if design map applies
        self.lf = False    # needed to identify if lifespan map applies
        # self.inverse_tcd = False  # if True: inverse use of tcd thresholds
        self.mu_bad = []
        self.mu_good = ["lateral bar", "levee", "spur dike"]
        self.mu_method = 1  # 0 = apply mu_bad list and 1 = apply mu_good list
        self.parameter_list = ["mu", "det"]  # governs analysis HIERARCHY!
        self.threshold_det_low = 20     # (ft)
        self.threshold_det_up = 75      # (ft)
        # self.threshold_fill = 0.1 * 6   # (ft/year)
        # self.threshold_scour = 0.1 * 6  # (ft/year)
        # self.threshold_taux = 0.047     # (--)
    def __call__(self):
        pass


## ---- Basic Classes ----
class RestorationFeature(Backwater, ELJ, Finesediment, Grading, Gravel, Plantings, Riprap,
                          Sidecavity, Sidechannel, Widen):
    # This class inherits from all above feature classes.
    # __call__()
    # Instantiate an object by: features = RestorationFeatures()

    def __init__(self, feature_name, *sub_feature):

        if feature_name == "Backwater" and not(sub_feature):
            Backwater.__init__(self)
            self.feature = Backwater()
            self.sub = False
            self.name = feature_name
            self.shortname = "backwtr"

        if feature_name == "Bermsetback" and not(sub_feature):
            Widen.__init__(self)
            self.feature = Widen()
            self.sub = False
            self.name = feature_name
            self.shortname = "widen"

        if feature_name == "Grading" and not(sub_feature):
            Grading.__init__(self)
            self.feature = Grading()
            self.sub = False
            self.name = feature_name
            self.shortname = "grade"

        if feature_name == "ELJ" and not(sub_feature):
            ELJ.__init__(self)
            self.feature = ELJ()
            self.sub = False
            self.name = feature_name
            self.shortname = "elj"

        if feature_name == "Finesediment" and not(sub_feature):
            Finesediment.__init__(self)
            self.feature = Backwater()
            self.sub = False
            self.name = feature_name
            self.shortname = "finesed"

        if feature_name == "Gravel" and not(sub_feature):
            Gravel.__init__(self)
            self.feature = Backwater()
            self.sub = False
            self.name = feature_name
            self.shortname = "gravelaug"

        if feature_name == "Plantings" and not(sub_feature):
            self.sub = True
            self.sub_list = ["cottonwood", "boxelder", "willow", "whitealder"]
            self.name = feature_name

        if feature_name == "Plantings" and sub_feature:
            if type(sub_feature == "tuple"):
                sub_feature = sub_feature[0]
            Plantings.__init__(self,sub_feature)
            self.name = "Plantings_" + str(sub_feature)
            self.shortname = "plant_" + sub_feature[0] + sub_feature[1] + sub_feature[2]

        if feature_name == "Riprap" and not(sub_feature):
            Riprap.__init__(self)
            self.feature = Riprap()
            self.sub = False
            self.name = feature_name
            self.shortname = "riprap"

        if feature_name == "Sidecavity" and not(sub_feature):
            Sidecavity.__init__(self)
            self.feature = Sidecavity()
            self.sub = False
            self.name = feature_name
            self.shortname = "sidecav"

        if feature_name == "Sidechannel" and not(sub_feature):
            Sidechannel.__init__(self)
            self.feature = Sidechannel()
            self.sub = False
            self.name = feature_name
            self.shortname = "sidechan"


    def __call__(self):
        pass



