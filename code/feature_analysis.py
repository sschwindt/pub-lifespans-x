# !/usr/bin/python
# Desc.: Provides classes
import sys, os
# add folder containing package routines to the system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import classes_mapper as cm
import classes_features as cf
import functions_global as fg
import classes_analysis as ca
import logging

def analysis_call(*args):

    try:
        parameter_name = args[0]
        feature = args[1]
        feature_analysis = args [2]

        ## invoke design raster creation
        if parameter_name == "ds_compare_slopes":
            feature_analysis.design_energy_slope()
        if parameter_name == "ds_filter":
            feature_analysis.design_filter(feature.threshold_Dmaxf)
        if parameter_name == "ds_stable_grains":
            feature_analysis.design_stable_grains(feature.threshold_taux)
        if parameter_name == "ds_wood":
            feature_analysis.design_wood()
        if parameter_name == "sidech":
            feature_analysis.design_side_channel()

        ## invoke lifespan raster creation
        if parameter_name == "d2w":
            feature_analysis.analyse_d2w(feature.threshold_d2w_low, feature.threshold_d2w_up)
        if parameter_name == "det":
            feature_analysis.analyse_det(feature.threshold_det_low, feature.threshold_det_up)
        if parameter_name == "Fr":
            feature_analysis.analyse_Fr(feature.threshold_Fr)
        if parameter_name == "fill":
            feature_analysis.analyse_fill(feature.threshold_fill)
        if parameter_name == "fine_grains":
            feature_analysis.analyse_fine_grains(feature.threshold_taux, feature.threshold_Dmaxf)
        if parameter_name == "h":
            feature_analysis.analyse_h(feature.threshold_h)
        if parameter_name == "mobile_grains":
            feature_analysis.analyse_mobile_grains(feature.threshold_taux)
        if parameter_name == "mu":
            feature_analysis.analyse_mu(feature.mu_bad, feature.mu_good, feature.mu_method)
        if parameter_name == "scour":
            feature_analysis.analyse_scour(feature.threshold_scour)
        if parameter_name == "taux":
            feature_analysis.analyse_taux(feature.threshold_taux)
        if parameter_name == "tcd":
            feature_analysis.analyse_tcd(feature.threshold_fill, feature.threshold_scour)
        if parameter_name == "u":
            feature_analysis.analyse_u(feature.threshold_u)
        return(feature_analysis)

    except:
        print("Call ERROR: Function analysis_call received bad arguments.")

def analysis(feature, condition, habitat):
    try:
        logger = logging.getLogger("feature_analysis")
        logger.info("----- ----- ----- ----- ----- ----- ----- ----- -----")
        logger.info("Analyzing " + feature.name)
        logger.info("----- ----- ----- ----- ----- ----- ----- ----- -----")
        try:
            fg.clean_dir(os.getcwd()+"\\.cache\\")  # ensure that the cache is empty
            pass
        except:
            logger.info("ERROR: .cache folder in use.")

        ## instantiate GIS Analysis Object
        feature_analysis = ca.ArcPyAnalysis(condition, habitat) # this is where arcpy comes into play...

        ## assign analysis specific parameters if applies
        try:
            inverse_tcd = feature.inverse_tcd
            logger.info("   >> Inverse tcd analysis")
        except:
            inverse_tcd = False
        feature_analysis.verify_inverse_tcd(inverse_tcd)
        try:
            freq = feature.threshold_freq
            logger.info("   >> Customary frequency threshold = " + str(freq))
        except:
            freq = 0
        feature_analysis.verify_threshold_freq(freq)
        try:
            sf = feature.sf
            logger.info("   >> Customary safety factor (SF) = " + str(sf))
        except:
            sf = 1.0
        feature_analysis.verify_sf(sf)

        ## call parameter analysis
        for par in feature.parameter_list:
            try:
                logger.info("   >> Calling parameter analysis (" + par + ").")
                feature_analysis = analysis_call(par, feature, feature_analysis)
            except:
                logger.info("Error: Failed calling " + par + " analysis of " + feature.name + ".")

        if feature_analysis.habitat_matching:
            feature_analysis.join_with_habitat()

        feature_analysis.save_manager(feature.ds, feature.lf, feature.shortname)

    except:
        print("Call ERROR: Function analysis received bad arguments.")

def layout_maker(condition, *args):
    # prepares layout of all available rasters in OutputRasters/condition folder
    # *args[0] = optional: alternative path for input rasters
    fn_full = os.path.join(os.getcwd(), "mxd_logfile.log")
    if os.path.isfile(fn_full):
        try:
            os.remove(fn_full)
            print("Overwriting old mxd_logfile.log")
        except:
            print("WARNING: Old mxd_logfile is locked.")
    try:
        mapper = cm.Mapper(condition, args[0])
        print("Alternative raster input directory provided:")
        print(args[0])
    except:
        mapper = cm.Mapper(condition)
    mapper.prepare_layout()
    mapper.stop_logging("layout")
    if not (mapper.error):
        fg.open_folder(mapper.output_mxd_dir)

def map_maker(condition, *args):
    # maps all available layouts (.mxd files) in OutputMaps/condition/Layouts folder
    # *args[0] = optional: alternative path for input layouts
    fn_full = os.path.join(os.getcwd(), "map_logfile.log")
    if os.path.isfile(fn_full):
        try:
            os.remove(fn_full)
            print("Overwriting old map_logfile.log")
        except:
            print("WARNING: Old map_logfile is locked.")
    mapper = cm.Mapper(condition)
    try:
        mapper.make_pdf_maps(args[0])
        print("Alternative layout input directory provided:")
        print(args[0])
    except:
        mapper.make_pdf_maps()

    mapper.stop_logging()
    if not(mapper.error):
        fg.open_folder(mapper.output_dir)


def raster_maker(condition, *args):
    feature_list = ["Backwater", "Bermsetback", "ELJ", "Finesediment", "Grading",
                    "Gravel", "Plantings", "Riprap", "Sidecavity", "Sidechannel"]
    if not(args):
        mapping = False
        habitat_analysis = False
    else:
        try:
            if args[0].__len__() > 0:
                feature_list = args[0]
        except:
            pass
        try:
            mapping = args[1]
            print("Integrated mapping (layout creation) activated.")
        except:
            mapping = False
            print("Integrated mapping deactivated.")
        try:
            habitat_analysis = args[2]
            print("Matching physical feature stability analysis with habitat enhancement relevance.")
        except:
            print("Physical feature stability analysis only.")

    logfilenames = ["error.log", "rasterlogfile.log", "logfile.log"]
    for fn in logfilenames:
        fn_full = os.path.join(os.getcwd(), fn)
        if os.path.isfile(fn_full):
            try:
                os.remove(fn_full)
                print("Overwriting old logfiles (" + fn + ").")
            except:
                print("WARNING: Old logfiles are locked.")

    ## start logging
    logger = logging.getLogger("feature_analysis")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(message)s")

    # create console handler and set level to info
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    # create error file handler and set level to error
    err_handler = logging.FileHandler(os.path.join(os.getcwd(), logfilenames[0]), "w", encoding=None, delay="true")
    err_handler.setLevel(logging.ERROR)
    err_handler.setFormatter(formatter)
    logger.addHandler(err_handler)
    # create debug file handler and set level to debug
    debug_handler = logging.FileHandler(os.path.join(os.getcwd(), logfilenames[1]), "w")
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)
    logger.addHandler(debug_handler)
    logger.info("feature_analysis.raster_maker initiated with feature list = " + str(feature_list))

    # set environment settings
    temp_path = os.getcwd()+"\\.cache\\"
    fg.chk_dir(temp_path)
    out_dir = os.path.dirname(os.path.realpath(__file__)) + "\\OutputRasters\\" + condition + "\\"
    fg.chk_dir(out_dir)
    fg.clean_dir(out_dir)

    for f in feature_list:
        feature = cf.RestorationFeature(f) # instantiate object containing all restoration feature attributes

        if not(feature.sub):
            analysis(feature, condition, habitat_analysis)
        else:
            for sf in feature.sub_list:
                sub_feature =  cf.RestorationFeature(f, sf)
                analysis(sub_feature, condition, habitat_analysis)
    try:
        fg.rm_dir(temp_path)  # dump cache after feature analysis
    except:
        logger.info("WARNING: Package could not remove .cache folder.")



    ## stop logging and release logfile
    for handler in logger.handlers:
        handler.close()
        logger.removeHandler(handler)


    if mapping:
        layout_maker(condition)

    return


if __name__ == "__main__":

    ## query condition
    condition = str(input('Enter the condition (shape: >> XXXX, e.g., >> 2008 ) \n>> '))

    ## launch raster maker for lifespan and design rasters
    try:
        ## try query feature_list
        feature_list = list(input(
            'Enter the condition (no mandatory; do not forget brackets! - example: >> ["Featurename1", "Featurename2"]) \n>> '))
        raster_maker(condition, feature_list)
    except:
        raster_maker(condition)

