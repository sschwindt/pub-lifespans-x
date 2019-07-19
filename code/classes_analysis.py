#!/usr/bin/python
# Filename: functions_analyse.py

from classes_parameters import *
from classes_read_inp import *
import arcpy
import os, logging
from arcpy.sa import * #good for raster processing

class ArcPyAnalysis():
    # This is class requires arcpy
    # analysis functions make lifespan rasters
    # design functions make design parameter raster
    # __call__()

    def __init__(self, condition, habitat_analysis):
        self.raster_info_lf = ""
        self.condition = str(condition)
        self.cache = os.path.dirname(os.path.realpath(__file__)) + "\\.cache\\"
        self.output = os.path.dirname(os.path.realpath(__file__)) + "\\OutputRasters\\" + self.condition + "\\"
        self.raster_dict_ds = {}
        self.raster_info_lf = "init"
        self.raster_dict_lf = {}
        self.habitat_matching = habitat_analysis

        self.g = 9.81 / 0.3047992   # (ft/s2) gravity acceleration
        self.m2ft = 1.0             # ft/m = 0.347992 if output is metric or = 1.0 if output is U.S. customary
        self.n = 0.0473934 / 1.49   # (s/ft^(1/3)) global Manning's n where k =1.49 converts to US customary
        self.rho_w = 1.937          # slug/ft^3
        self.s = 2.68               # (--) relative grain density (ratio of rho_s and rho_w)
        self.info = Info()
        self.lifespans = self.info.lifespan_read()   # definition of lifespans in years from input_definitions.inp
        self.logger = logging.getLogger("feature_analysis")


    def analyse_d2w(self, threshold_low, threshold_up):
        try:
            arcpy.CheckOutExtension('Spatial')  # check out license
            arcpy.gp.overwriteOutput = True
            arcpy.env.workspace = self.cache #os.path.dirname(os.path.realpath(__file__)) + "\\Input\\" + self.condition + "\\"
            self.logger.info("      >>> Analyzing depth to groundwater.")
            d2w = WaterTable(self.condition)

            if not(self.raster_dict_lf.items().__len__() > 0):
                ## routine to override noData pixels if required.
                temp_d2w = Con((IsNull(d2w.raster) == 1), (IsNull(d2w.raster) * 0), d2w.raster)
                d2w.raster = temp_d2w

            self.ras_d2w = Con(((d2w.raster >= threshold_low) & (d2w.raster <= threshold_up)), 1.0)

            if self.verify_raster_info():
                self.logger.info("            based on raster: " + self.raster_info_lf)
                temp_ras_base = Con((IsNull(self.raster_dict_lf[self.raster_info_lf]) == 1),
                               (IsNull(self.raster_dict_lf[self.raster_info_lf]) * 0),
                               self.raster_dict_lf[self.raster_info_lf])
                temp_ras_d2w = Con((IsNull(self.ras_d2w) == 1), (IsNull(self.ras_d2w) * 0), self.ras_d2w)
                ras_d2w_new = Con(((temp_ras_d2w == 1.0) & (temp_ras_base > 0)), temp_ras_base)
                self.ras_d2w = ras_d2w_new
            self.raster_info_lf = "ras_d2w"
            self.raster_dict_lf.update({"ras_d2w": self.ras_d2w})

            arcpy.CheckInExtension('Spatial')
        except arcpy.ExecuteError:
            self.logger.info("ExecuteERROR: (arcpy) in d2w.")
            self.logger.info(arcpy.GetMessages(2))
            arcpy.AddError(arcpy.GetMessages(2))
        except Exception as e:
            self.logger.info("ExceptionERROR: (arcpy) in d2w.")
            self.logger.info(e.args[0])
            arcpy.AddError(e.args[0])
        except:
            self.logger.info("ERROR: (arcpy) in d2w.")
            self.logger.info(arcpy.GetMessages())

    def analyse_det(self, threshold_low, threshold_up):
        try:
            arcpy.CheckOutExtension('Spatial')  # check out license
            arcpy.gp.overwriteOutput = True
            arcpy.env.workspace = self.cache #os.path.dirname(os.path.realpath(__file__)) + "\\Input\\" + self.condition + "\\"
            self.logger.info("      >>> Analyzing detrended DEM.")
            det = DEMdet(self.condition)

            if not(self.raster_dict_lf.items().__len__() > 0):
                ## routine to override noData pixels if required.
                temp_det = Con((IsNull(det.raster) == 1), (IsNull(det.raster) * 0), det.raster)
                det.raster = temp_det

            self.ras_det = Con(((det.raster >= threshold_low) & (det.raster <= threshold_up)), 1)

            if self.verify_raster_info():
                self.logger.info("            based on raster: " + self.raster_info_lf)
                ## make temp_ras without noData pixels --> det is inclusive!
                temp_ras = Con((IsNull(self.raster_dict_lf[self.raster_info_lf]) == 1),
                               (IsNull(self.raster_dict_lf[self.raster_info_lf]) * 0),
                                self.raster_dict_lf[self.raster_info_lf])
                ## compare temp_ras with raster_dict but use self.ras_... values if condition is True
                # special case det: usage of logical OR instead of AND (only application is Widen)
                ras_det_new = Con(((self.ras_det == 1) | (temp_ras > 0)), 1.0)
                self.ras_det = ras_det_new
            self.raster_info_lf = "ras_det"
            self.raster_dict_lf.update({self.raster_info_lf: self.ras_det})

            arcpy.CheckInExtension('Spatial')
        except arcpy.ExecuteError:
            self.logger.info("ExecuteERROR: (arcpy) in DEMdet.")
            self.logger.info(arcpy.GetMessages(2))
            arcpy.AddError(arcpy.GetMessages(2))
        except Exception as e:
            self.logger.info("ExceptionERROR: (arcpy) in DEMdet.")
            self.logger.info(e.args[0])
            arcpy.AddError(e.args[0])
        except:
            self.logger.info("ERROR: (arcpy) in DEMdet.")
            self.logger.info(arcpy.GetMessages())

    def analyse_fill(self, threshold_fill):
        try:
            arcpy.CheckOutExtension('Spatial')  # check out license
            arcpy.gp.overwriteOutput = True
            arcpy.env.workspace = self.cache
            self.logger.info("      >>> Analyzing tcd (fill only).")
            dod = DoD(self.condition)

            if not(self.raster_dict_lf.items().__len__() > 0):
                ## routine to override noData pixels if required.
                temp_fill = Con((IsNull(dod.raster_fill) == 1), (IsNull(dod.raster_fill) * 0), dod.raster_fill)
                dod.raster_fill = temp_fill

            if not(self.inverse_tcd):
                self.ras_tcd = Con((dod.raster_fill >= threshold_fill), 1.0, 0)
            else:
                self.ras_tcd = Con((dod.raster_fill < threshold_fill), 1.0)

            if self.verify_raster_info():
                self.logger.info("            based on raster: " + self.raster_info_lf)
                ## make temp_ras without noData pixels
                if not (self.inverse_tcd):
                    temp_ras = Con((IsNull(self.ras_tcd) == 1), (IsNull(self.ras_tcd) * 20), self.ras_tcd)
                    ## compare temp_ras with raster_dict but use self.ras_... values if condition is True
                    ras_tcd_new = Con((temp_ras == 1.0), self.ras_tcd, self.raster_dict_lf[self.raster_info_lf])
                else:
                    ras_tcd_new = Con(((self.ras_tcd == 1.0) &
                                       (self.raster_dict_lf[self.raster_info_lf] > self.threshold_freq)),
                                        self.raster_dict_lf[self.raster_info_lf])
                self.ras_tcd = ras_tcd_new

            self.raster_info_lf = "ras_tcd"
            self.raster_dict_lf.update({self.raster_info_lf: self.ras_tcd})
            arcpy.CheckInExtension('Spatial')
        except arcpy.ExecuteError:
            self.logger.info("ExecuteERROR: (arcpy) in tcd.")
            self.logger.info(arcpy.GetMessages(2))
            arcpy.AddError(arcpy.GetMessages(2))
        except Exception as e:
            self.logger.info("ExceptionERROR: (arcpy) in tcd.")
            self.logger.info(e.args[0])
            arcpy.AddError(e.args[0])
        except:
            self.logger.info("ERROR: (arcpy) in tcd.")
            self.logger.info(arcpy.GetMessages())

    def analyse_fine_grains(self, threshold_taux, Dmaxf):
        try:
            arcpy.CheckOutExtension('Spatial')  # check out license
            arcpy.gp.overwriteOutput = True
            arcpy.env.workspace = self.cache
            self.logger.info("      >>> Analyzing fine grain stability (Dcr).")
            h = FlowDepth(self.condition)
            u = FlowVelocity(self.condition)

            Dmaxf = Dmaxf / 12 # convert inches to feet
            Dmean = GrainSizes(self.condition)  # (ft)
            D85_fines = 0.25 * Dmean.raster / 5 # (ft) 0.25 for D15(coarse), 5 for fine conversion

            Dcr_raster_list = []
            for i in range(0, h.raster_names.__len__()):
                if arcpy.Exists(u.rasters[i]) and arcpy.Exists(h.rasters[i]):
                    __ras__ = (Square(u.rasters[i] * self.n) / ((self.s - 1) *
                                                                threshold_taux * Power(h.rasters[i], (1 / 3))))
                    Dcr_raster_list.append(__ras__)
                else:
                    Dcr_raster_list.append("")

            self.ras_Dcf = self.compare_raster_set(Dcr_raster_list, D85_fines)

            if self.verify_raster_info():
                self.logger.info("            based on raster: " + self.raster_info_lf)
                ## make temp_ras without noData pixels
                temp_ras_base = Con((IsNull(self.raster_dict_lf[self.raster_info_lf]) == 1),
                                    (IsNull(self.raster_dict_lf[self.raster_info_lf]) * 0),
                                    self.raster_dict_lf[self.raster_info_lf])
                temp_ras_dcf = Con((IsNull(self.ras_Dcf) == 1), (IsNull(self.ras_Dcf) * 20.0), self.ras_Dcf)
                ## compare temp_ras with raster_dict but use self.ras_... values if condition is True
                ras_Dcr_new = Con(((temp_ras_dcf < temp_ras_base) & (temp_ras_dcf > 0)),
                                  temp_ras_dcf, self.raster_dict_lf[self.raster_info_lf])
                self.ras_Dcr = ras_Dcr_new

            ## eliminate pixels where "fines" are not "fine"
            ras_exclude = Con((D85_fines < Dmaxf), self.ras_Dcf)
            self.ras_Dcf = ras_exclude

            ## update lf dictionnary
            self.raster_info_lf = "ras_Dcf"
            self.raster_dict_lf.update({self.raster_info_lf: self.ras_Dcf})
            arcpy.CheckInExtension('Spatial')
        except arcpy.ExecuteError:
            self.logger.info("ExecuteERROR: (arcpy) in fine sediment stability.")
            self.logger.info(arcpy.GetMessages(2))
            arcpy.AddError(arcpy.GetMessages(2))
        except Exception as e:
            self.logger.info("ExceptionERROR: (arcpy) in fine sediment stability.")
            self.logger.info(e.args[0])
            arcpy.AddError(e.args[0])
        except:
            self.logger.info("ERROR: (arcpy) in fine sediment stability.")
            self.logger.info(arcpy.GetMessages())

    def analyse_Fr(self, threshold_Fr):
        try:
            arcpy.CheckOutExtension('Spatial')  # check out license
            arcpy.gp.overwriteOutput = True
            arcpy.env.workspace = self.cache
            self.logger.info("      >>> Analyzing Froude number.")
            h = FlowDepth(self.condition)
            u = FlowVelocity(self.condition)

            Fr_raster_list = []
            for i in range(0, h.raster_names.__len__()):
                if arcpy.Exists(u.rasters[i]) and arcpy.Exists(h.rasters[i]):
                    __ras__ = u.rasters[i] / SquareRoot(self.g * h.rasters[i])
                    Fr_raster_list.append(__ras__)
                else:
                    Fr_raster_list.append("")

            self.ras_Fr = self.compare_raster_set(Fr_raster_list, threshold_Fr)

            if self.verify_raster_info():
                self.logger.info("            based on raster: " + self.raster_info_lf)
                temp_ras_base = Con((IsNull(self.raster_dict_lf[self.raster_info_lf]) == 1),
                                    (IsNull(self.raster_dict_lf[self.raster_info_lf]) * 0),
                                    self.raster_dict_lf[self.raster_info_lf])
                temp_ras_Fr = Con((IsNull(self.ras_Fr) == 1), (IsNull(self.ras_Fr) * 20.0), self.ras_Fr)
                ras_Fr_new = Con((temp_ras_Fr < temp_ras_base), temp_ras_Fr, self.raster_dict_lf[self.raster_info_lf])
                self.ras_Fr = ras_Fr_new

            ## update lf dictionnary
            self.raster_info_lf = "ras_Fr"
            self.raster_dict_lf.update({self.raster_info_lf: self.ras_Fr})
            arcpy.CheckInExtension('Spatial')
        except arcpy.ExecuteError:
            self.logger.info("ExecuteERROR: (arcpy) in Froude.")
            self.logger.info(arcpy.GetMessages(2))
            arcpy.AddError(arcpy.GetMessages(2))

        except Exception as e:
            self.logger.info("ExceptionERROR: (arcpy) in Froude.")
            self.logger.info(e.args[0])
            arcpy.AddError(e.args[0])

        except:
            self.logger.info("ERROR: (arcpy) in Froude.")
            self.logger.info(arcpy.GetMessages())

    def analyse_h(self, threshold_h):
        try:
            arcpy.CheckOutExtension('Spatial')  # check out license
            arcpy.gp.overwriteOutput = True
            arcpy.env.workspace = self.cache
            self.logger.info("      >>> Analyzing hyd (h only).")

            h = FlowDepth(self.condition)
            self.ras_dth = self.compare_raster_set(h.rasters,threshold_h)

            self.raster_info_lf = "ras_dth"
            self.raster_dict_lf.update({self.raster_info_lf: self.ras_dth})

            arcpy.CheckInExtension('Spatial')
        except arcpy.ExecuteError:
            self.logger.info("ExecuteERROR: (arcpy) in h.")
            self.logger.info(arcpy.GetMessages(2))
            arcpy.AddError(arcpy.GetMessages(2))
        except Exception as e:
            self.logger.info("ExceptionERROR: (arcpy) in h.")
            self.logger.info(e.args[0])
            arcpy.AddError(e.args[0])
        except:
            self.logger.info("ERROR: (arcpy) in h.")
            self.logger.info(arcpy.GetMessages())



    def analyse_mobile_grains(self, threshold_taux):
        try:
            arcpy.CheckOutExtension('Spatial')  # check out license
            arcpy.gp.overwriteOutput = True
            arcpy.env.workspace = self.cache
            self.logger.info("      >>> Analyzing Dcr (mobile grains).")
            h = FlowDepth(self.condition)
            u = FlowVelocity(self.condition)
            Dmean = GrainSizes(self.condition) # in ft

            Dcr_raster_list = []
            for i in range(0, h.raster_names.__len__()):
                if arcpy.Exists(u.rasters[i]) and arcpy.Exists(h.rasters[i]):
                    __ras__ = (Square(u.rasters[i] * self.n) / ((self.s - 1) *
                                                                threshold_taux * Power(h.rasters[i], (1 / 3))))
                    Dcr_raster_list.append(__ras__)
                else:
                    Dcr_raster_list.append("")

            self.ras_Dcr = self.compare_raster_set(Dcr_raster_list, Dmean.raster)

            if not(self.threshold_freq == 0.0):
                temp_ras = Con((self.ras_Dcr > self.threshold_freq), self.ras_Dcr)
                self.ras_Dcr = temp_ras

            if self.verify_raster_info():
                self.logger.info("            based on raster: " + self.raster_info_lf)
                temp_ras_Dcr = Con((IsNull(self.ras_Dcr) == 1), (IsNull(self.ras_Dcr) * 0), self.ras_Dcr)
                temp_ras_base = Con((IsNull(self.raster_dict_lf[self.raster_info_lf]) == 1),
                                  (IsNull(self.raster_dict_lf[self.raster_info_lf]) * 0),
                                  self.raster_dict_lf[self.raster_info_lf])
                ras_Dcr_new = Con(((temp_ras_Dcr < temp_ras_base) & (temp_ras_Dcr > 0)),
                                   self.ras_Dcr, self.raster_dict_lf[self.raster_info_lf])
                self.ras_Dcr = ras_Dcr_new

            self.raster_info_lf = "ras_Dcr"
            self.raster_dict_lf.update({self.raster_info_lf: self.ras_Dcr})
            arcpy.CheckInExtension('Spatial')

        except arcpy.ExecuteError:
            self.logger.info("ExecuteERROR: (arcpy) in grain mobility (Dcr lifespan).")
            self.logger.info(arcpy.GetMessages(2))
            arcpy.AddError(arcpy.GetMessages(2))

        except Exception as e:
            self.logger.info("ExceptionERROR: (arcpy) in grain mobility (Dcr lifespan).")
            self.logger.info(e.args[0])
            arcpy.AddError(e.args[0])

        except:
            self.logger.info("ERROR: (arcpy) in grain mobility (Dcr lifespan).")
            self.logger.info(arcpy.GetMessages())

    def analyse_mu(self, mu_bad, mu_good, method):
        try:
            arcpy.CheckOutExtension('Spatial')  # check out license
            arcpy.gp.overwriteOutput = True
            arcpy.env.workspace = self.cache
            self.logger.info("      >>> Analyzing morphologic units.")
            mu = MU(self.condition)  # thresholds are

            if method == 0:
                self.logger.info("          MU: using exclusive method.")
                try:
                    # self.ras_mu = Con(~(mu.raster == mu.mu_dict[mu_bad[0]]), 1) # initial condition
                    temp_dict = {}
                    for morph_unit in mu_bad:
                        temp_dict.update({morph_unit: Con((mu.raster == mu.mu_dict[morph_unit]), 1.0, 0)})
                    self.ras_mu = CellStatistics(temp_dict.values(), "SUM", "DATA")
                    temp_ras = Con((self.ras_mu >= 1), 0, 1.0)
                    self.ras_mu = temp_ras

                except:
                    self.logger.info("ERROR: Could not assign MU raster.")
            if method == 1:
                self.logger.info("          MU: using inclusive method.")
                try:
                    temp_dict = {}
                    for morph_unit in mu_good:
                        temp_dict.update({morph_unit: Con((mu.raster == mu.mu_dict[morph_unit]), 1.0, 0)})
                    self.ras_mu = CellStatistics(temp_dict.values(), "SUM", "DATA")
                    temp_ras = Con((self.ras_mu >= 1), 1.0, 0)
                    self.ras_mu = temp_ras
                except:
                    self.logger.info("ERROR: Could not assign MU raster.")
                    try:
                        self.logger.info("        -- mu_good: " + str(mu_good))
                    except:
                        self.logger.info("        -- bad mu_good list assignment.")
                    try:
                        self.logger.info("        -- method: " + str(method))
                    except:
                        self.logger.info("        -- bad method assignment.")

            if self.verify_raster_info():
                self.logger.info("            based on raster: " + self.raster_info_lf)
                ## make temp_ras without noData pixels for both ras_mu and ras_dict
                temp_ras_mu = Con((IsNull(self.ras_mu) == 1), (IsNull(self.ras_mu) * 0), self.ras_mu)
                temp_ras_di = Con((IsNull(self.raster_dict_lf[self.raster_info_lf]) == 1),
                               (IsNull(self.raster_dict_lf[self.raster_info_lf]) * 0),
                                self.raster_dict_lf[self.raster_info_lf])
                ## compare temp_ras with raster_dict but use self.ras_... values if condition is True
                ras_mu_new = Con(((temp_ras_mu == 1.0) & (temp_ras_di > 0)), temp_ras_di)
                self.ras_mu = ras_mu_new
            self.raster_info_lf = "ras_mu"
            self.raster_dict_lf.update({"ras_mu": self.ras_mu})

            arcpy.CheckInExtension('Spatial')
        except arcpy.ExecuteError:
            self.logger.info("ExecuteERROR: (arcpy) in MU.")
            self.logger.info(arcpy.GetMessages(2))
            arcpy.AddError(arcpy.GetMessages(2))

        except Exception as e:
            self.logger.info("ExceptionERROR: (arcpy) in MU.")
            self.logger.info(e.args[0])
            arcpy.AddError(e.args[0])

        except:
            self.logger.info("ERROR: (arcpy) in MU.")
            self.logger.info(arcpy.GetMessages())

    def analyse_scour(self, threshold_scour):

        try:
            arcpy.CheckOutExtension('Spatial')  # check out license
            arcpy.gp.overwriteOutput = True
            arcpy.env.workspace = self.cache
            self.logger.info("      >>> Analyzing tcd (scour only) ...")

            dod = DoD(self.condition)
            if not(self.raster_dict_lf.items().__len__() > 0):
                ## routine to override noData pixels if required.
                temp_scour = Con((IsNull(dod.raster_scour) == 1), (IsNull(dod.raster_scour) * 0), dod.raster_scour)
                dod.raster_scour = temp_scour

            if not (self.inverse_tcd):
                self.ras_tcd = Con((dod.raster_scour >= threshold_scour), 1.0, 0)
            else:
                self.ras_tcd = Con((dod.raster_scour < threshold_scour), 1.0)

            if self.verify_raster_info():
                self.logger.info("            based on raster: " + self.raster_info_lf)
                ## make temp_ras without noData pixels
                if not (self.inverse_tcd):
                    temp_ras = Con((IsNull(self.ras_tcd) == 1), (IsNull(self.ras_tcd) * 20), self.ras_tcd)
                    ## compare temp_ras with raster_dict but use self.ras_... values if condition is True
                    ras_tcd_new = Con((temp_ras == 1.0), self.ras_tcd, self.raster_dict_lf[self.raster_info_lf])
                else:
                    ras_tcd_new = Con(((self.ras_tcd == 1.0) &
                                       (self.raster_dict_lf[self.raster_info_lf] > self.threshold_freq)),
                                        self.raster_dict_lf[self.raster_info_lf])
                self.ras_tcd = ras_tcd_new

            self.raster_info_lf = "ras_tcd"
            self.raster_dict_lf.update({self.raster_info_lf: self.ras_tcd})
            arcpy.CheckInExtension('Spatial')
        except arcpy.ExecuteError:
            self.logger.info("ExecuteERROR: (arcpy) in tcd-scour.")
            self.logger.info(arcpy.GetMessages(2))
            arcpy.AddError(arcpy.GetMessages(2))
        except Exception as e:
            self.logger.info("ExceptionERROR: (arcpy) in tcd-scour.")
            self.logger.info(e.args[0])
            arcpy.AddError(e.args[0])
        except:
            self.logger.info("ERROR: (arcpy) in tcd-scour.")
            self.logger.info(arcpy.GetMessages())



    def analyse_taux(self, threshold_taux):
        try:
            arcpy.CheckOutExtension('Spatial')  # check out license
            arcpy.gp.overwriteOutput = True
            arcpy.env.workspace = self.cache
            self.logger.info("      >>> Analyzing taux.")
            ##Copy last RasterDataset to OutputRasters folder
            h = FlowDepth(self.condition)  # thresholds are
            u = FlowVelocity(self.condition)
            grains = GrainSizes(self.condition)

            tx_raster_list = []
            for i in range(0, h.raster_names.__len__()):
                if arcpy.Exists(u.rasters[i]) and arcpy.Exists(h.rasters[i]):
                    __ras__ = (self.rho_w * Square(u.rasters[i] / (5.75 * Log10(12.2 * h.rasters[i] /
                              (2 * 2.2 * grains.raster * self.m2ft))))) / (self.rho_w * self.g * (self.s - 1) *
                                                                           grains.raster * self.m2ft)
                    tx_raster_list.append(__ras__)
                else:
                    tx_raster_list.append("")

            self.ras_taux = self.compare_raster_set(tx_raster_list, threshold_taux)


            if self.verify_raster_info():
                self.logger.info("            based on raster: " + self.raster_info_lf)
                ## make temp_ras without noData pixels
                temp_ras_base = Con((IsNull(self.raster_dict_lf[self.raster_info_lf]) == 1),
                                  (IsNull(self.raster_dict_lf[self.raster_info_lf]) * 0),
                                  self.raster_dict_lf[self.raster_info_lf])
                temp_ras_tx = Con((IsNull(self.ras_taux) == 1), (IsNull(self.ras_taux) * 20), self.ras_taux)
                ## compare temp_ras with raster_dict but use self.ras_... values if condition is True
                ras_taux_new = Con((temp_ras_tx < temp_ras_base),
                                   self.ras_taux, self.raster_dict_lf[self.raster_info_lf])
                self.ras_taux = ras_taux_new

            self.raster_info_lf = "ras_taux"
            self.raster_dict_lf.update({"ras_taux": self.ras_taux})
            arcpy.CheckInExtension('Spatial')
        except arcpy.ExecuteError:
            self.logger.info("ExecuteERROR: (arcpy) in taux.")
            self.logger.info(arcpy.GetMessages(2))
            arcpy.AddError(arcpy.GetMessages(2))
        except Exception as e:
            self.logger.info("ExceptionERROR: (arcpy) in taux.")
            self.logger.info(e.args[0])
            arcpy.AddError(e.args[0])
        except:
            self.logger.info("ERROR: (arcpy) in taux.")
            self.logger.info(arcpy.GetMessages())

    def analyse_tcd(self, threshold_fill, threshold_scour):
        try:
            arcpy.CheckOutExtension('Spatial')  # check out license
            arcpy.gp.overwriteOutput = True
            arcpy.env.workspace = self.cache
            self.logger.info("      >>> Analyzing tcd (fill and scour).")
            dod = DoD(self.condition)

            if not(self.raster_dict_lf.items().__len__() > 0):
                ## routine to override noData pixels -- applies when raster_dict_lf is still empty
                temp_fill = Con((IsNull(dod.raster_fill) == 1), (IsNull(dod.raster_fill) * 0), dod.raster_fill)
                dod.raster_fill = temp_fill
                temp_scour = Con((IsNull(dod.raster_scour) == 1), (IsNull(dod.raster_scour) * 0), dod.raster_scour)
                dod.raster_scour = temp_scour

            if not(self.inverse_tcd):
                self.ras_tcd = Con(((dod.raster_fill >= threshold_fill) | (dod.raster_scour >= threshold_scour)), 1.0, 0)
            else:
                self.ras_tcd = Con(((dod.raster_fill < threshold_fill) | (dod.raster_scour < threshold_scour)), 1.0, 0)

            if self.verify_raster_info():
                self.logger.info("            based on raster: " + self.raster_info_lf)
                ## make temp_ras without noData pixels
                temp_ras = Con((IsNull(self.ras_tcd) == 1), (IsNull(self.ras_tcd) * 20), self.ras_tcd)
                ## compare temp_ras with raster_dict but use self.ras_... values if condition is True
                ras_tcd_new = Con((temp_ras == 1.0), self.ras_tcd, self.raster_dict_lf[self.raster_info_lf])
                self.ras_tcd = ras_tcd_new

            self.raster_info_lf = "ras_tcd"
            self.raster_dict_lf.update({self.raster_info_lf: self.ras_tcd})

            arcpy.CheckInExtension('Spatial')
        except arcpy.ExecuteError:
            self.logger.info("ExecuteERROR: (arcpy) in tcd.")
            self.logger.info(arcpy.GetMessages(2))
            arcpy.AddError(arcpy.GetMessages(2))
        except Exception as e:
            self.logger.info("ExceptionERROR: (arcpy) in tcd.")
            self.logger.info(e.args[0])
            arcpy.AddError(e.args[0])
        except:
            self.logger.info("ERROR: (arcpy) in tcd.")
            self.logger.info(arcpy.GetMessages())

    def analyse_u(self, threshold_u):
        try:
            arcpy.CheckOutExtension('Spatial')  # check out license
            arcpy.gp.overwriteOutput = True
            arcpy.env.workspace = self.cache
            self.logger.info("      >>> Analyzing vel (u only).")

            u = FlowVelocity(self.condition)
            self.ras_vel = self.compare_raster_set(u.rasters, threshold_u)

            if self.verify_raster_info():
                self.logger.info("            based on raster: " + self.raster_info_lf)
                ## make temp_ras without noData pixels
                temp_ras_u = Con((IsNull(self.ras_vel) == 1), (IsNull(self.ras_vel) * 0), self.ras_vel)
                temp_ras_base = Con((IsNull(self.raster_dict_lf[self.raster_info_lf]) == 1),
                                  (IsNull(self.raster_dict_lf[self.raster_info_lf]) * 0),
                                  self.raster_dict_lf[self.raster_info_lf])
                ## compare temp_ras with raster_dict but use self.ras_... values if condition is True
                ras_vel_new = Con(((temp_ras_u < temp_ras_base) & (temp_ras_u > 0)), self.ras_vel,
                                  self.raster_dict_lf[self.raster_info_lf])
                self.ras_vel = ras_vel_new

            self.raster_info_lf = "ras_vel"
            self.raster_dict_lf.update({self.raster_info_lf: self.ras_vel})
            arcpy.CheckInExtension('Spatial')
        except arcpy.ExecuteError:
            self.logger.info("ExecuteERROR: (arcpy) in u.")
            self.logger.info(arcpy.GetMessages(2))
            arcpy.AddError(arcpy.GetMessages(2))
        except Exception as e:
            self.logger.info("ExceptionERROR: (arcpy) in u.")
            self.logger.info(e.args[0])
            arcpy.AddError(e.args[0])
        except:
            self.logger.info("ERROR: (arcpy) in u.")
            self.logger.info(arcpy.GetMessages())


    def compare_raster_set(self, raster_set, threshold):
        ## raster_set: object containing one or more rasters
        ## threshold: float with threshold or raster with thresholds
        ## COMPLEX FUNCTION - change only if you know exactly what you are doing!

        if arcpy.Exists(raster_set[0]):
            ras_00 = Con((raster_set[0] >= threshold), self.lifespans[0])
            if arcpy.Exists(raster_set[1]):
                ## given raster_set[0] exists
                ras_01 = Con(((raster_set[1] >= threshold) &
                              (~(raster_set[0] >= threshold))), self.lifespans[1])
                if arcpy.Exists(raster_set[2]):
                    ## given raster_set[0] and [1] exist
                    ras_02 = Con(((raster_set[2] >= threshold) &
                                  (~((raster_set[1] >= threshold) |
                                     (raster_set[0] >= threshold)))), self.lifespans[2])
                    if arcpy.Exists(raster_set[3]):
                        ## given raster_set[0], [1] and [2] exist
                        ras_03 = Con(((raster_set[3] >= threshold) &
                                      (~((raster_set[2] >= threshold) |
                                         (raster_set[1] >= threshold) |
                                         (raster_set[0] >= threshold)))), self.lifespans[3])
                        if arcpy.Exists(raster_set[4]):
                            ## given raster_set[0], [1], [2] and [3] exist
                            ras_04 = Con(((raster_set[4] >= threshold) &
                                          (~((raster_set[3] >= threshold) |
                                             (raster_set[2] >= threshold) |
                                             (raster_set[1] >= threshold) |
                                             (raster_set[0] >= threshold)))), self.lifespans[4])
                            if arcpy.Exists(raster_set[5]):
                                ## given raster_set[0], [1], [2], [3] and [4] exist
                                ras_05 = Con(((raster_set[5] >= threshold) &
                                              (~((raster_set[4] >= threshold) |
                                                 (raster_set[3] >= threshold) |
                                                 (raster_set[2] >= threshold) |
                                                 (raster_set[1] >= threshold) |
                                                 (raster_set[0] >= threshold)))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02, ras_03, ras_04, ras_05], "SUM",
                                                          "DATA")
                            else:
                                ## only raster_set [4], [3], [2], [1] and [0] exist
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02, ras_03, ras_04], "SUM", "DATA")
                        else:
                            ## raster_set [3], [2], [1] and [0] exist but not [4]
                            if arcpy.Exists(raster_set[5]):
                                ## given raster_set[0], [1], [2], [3] and [5] exist
                                ras_04 = Con(((raster_set[5] >= threshold) &
                                              (~((raster_set[3] >= threshold) |
                                                 (raster_set[2] >= threshold) |
                                                 (raster_set[1] >= threshold) |
                                                 (raster_set[0] >= threshold)))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02, ras_03, ras_04], "SUM", "DATA")
                            else:
                                ## only raster_set [3], [2], [1] and [0] exist
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02, ras_03], "SUM", "DATA")
                    else:
                        ## raster_set [2], [1] and [0] exist but not [3]
                        if arcpy.Exists(raster_set[4]):
                            ## given raster_set[0], [1], [2] and [4] exist
                            ras_03 = Con(((raster_set[4] >= threshold) &
                                          (~((raster_set[2] >= threshold) |
                                             (raster_set[1] >= threshold) |
                                             (raster_set[0] >= threshold)))), self.lifespans[4])
                            if arcpy.Exists(raster_set[5]):
                                ## raster_set[0], [1], [2], [4] and [5] exist
                                ras_04 = Con(((raster_set[5] >= threshold) &
                                              (~((raster_set[4] >= threshold) |
                                                 (raster_set[2] >= threshold) |
                                                 (raster_set[1] >= threshold) |
                                                 (raster_set[0] >= threshold)))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02, ras_03, ras_04], "SUM", "DATA")
                            else:
                                ## only raster_set[0], [1], [2] and [4] exist
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02, ras_03], "SUM", "DATA")
                        else:
                            ## only raster_set [2], [1] and [0] exist
                            if arcpy.Exists(raster_set[5]):
                                ## raster_set[0], [1], [2] and [5] exist
                                ras_03 = Con(((raster_set[5] >= threshold) &
                                              (~((raster_set[2] >= threshold) |
                                                 (raster_set[1] >= threshold) |
                                                 (raster_set[0] >= threshold)))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02, ras_03], "SUM", "DATA")
                            else:
                                ## only raster_set[0], [1], [2] exist
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02], "SUM", "DATA")
                else:
                    ## raster_set[1] and [0] exist but not [2]
                    if arcpy.Exists(raster_set[3]):
                        ## raster_set[0], [1] and [3] exist
                        ras_02 = Con(((raster_set[3] >= threshold) &
                                      (~((raster_set[1] >= threshold) |
                                         (raster_set[0] >= threshold)))), self.lifespans[3])
                        if arcpy.Exists(raster_set[4]):
                            ## raster_set[0], [1], [3] and [4] exist
                            ras_03 = Con(((raster_set[4] >= threshold) &
                                          (~((raster_set[3] >= threshold) |
                                             (raster_set[1] >= threshold) |
                                             (raster_set[0] >= threshold)))), self.lifespans[4])
                            if arcpy.Exists(raster_set[5]):
                                ## raster_set[0], [1], [3], [4] and [5] exist
                                ras_04 = Con(((raster_set[5] >= threshold) &
                                              (~((raster_set[4] >= threshold) |
                                                 (raster_set[3] >= threshold) |
                                                 (raster_set[1] >= threshold) |
                                                 (raster_set[0] >= threshold)))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02, ras_03, ras_04], "SUM", "DATA")
                            else:
                                ## only raster_set[0], [1], [3] and [4] exist
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02, ras_03], "SUM", "DATA")
                        else:
                            ## only raster_set[0], [1] and [3] exist
                            if arcpy.Exists(raster_set[5]):
                                ## raster_set[0], [1], [3] and [5] exist
                                ras_03 = Con(((raster_set[5] >= threshold) &
                                              (~((raster_set[3] >= threshold) |
                                                 (raster_set[1] >= threshold) |
                                                 (raster_set[0] >= threshold)))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02, ras_03], "SUM", "DATA")
                            else:
                                ## only raster_set[0], [1] and [3] exist
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02], "SUM", "DATA")
                    else:
                        ## only raster_set [1] and [0] exist, not[2], [3]
                        if arcpy.Exists(raster_set[4]):
                            ## raster_set[0], [1] and [4] exist
                            ras_02 = Con(((raster_set[4] >= threshold) &
                                          (~((raster_set[1] >= threshold) |
                                             (raster_set[0] >= threshold)))), self.lifespans[4])
                            if arcpy.Exists(raster_set[5]):
                                ## raster_set[0], [1], [4] and [5] exist
                                ras_03 = Con(((raster_set[5] >= threshold) &
                                              (~((raster_set[4] >= threshold) |
                                                 (raster_set[1] >= threshold) |
                                                 (raster_set[0] >= threshold)))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02, ras_03], "SUM", "DATA")
                            else:
                                ## only raster_set [4], [1] and [0] exist
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02], "SUM", "DATA")
                        else:
                            if arcpy.Exists(raster_set[5]):
                                ## raster_set[0], [1] and [5] exist
                                ras_02 = Con(((raster_set[5] >= threshold) &
                                              (~((raster_set[1] >= threshold) |
                                                 (raster_set[0] >= threshold)))), self.lifespans[5])
                            else:
                                ## only raster_set [1] and [0] exist
                                ras_stat = CellStatistics([ras_00, ras_01], "SUM", "DATA")
            else:
                ## raster_set[0] exists raster_set[1] does not exist
                if arcpy.Exists(raster_set[2]):
                    ## raster_set[0] and [2] exist
                    ras_01 = Con(((raster_set[2] >= threshold) &
                                  (~(raster_set[0] >= threshold))), self.lifespans[2])
                    if arcpy.Exists(raster_set[3]):
                        ## given raster_set[0], [2] and [3] exist
                        ras_02 = Con(((raster_set[3] >= threshold) &
                                      (~((raster_set[2] >= threshold) |
                                         (raster_set[0] >= threshold)))), self.lifespans[3])
                        if arcpy.Exists(raster_set[4]):
                            ## raster_set[0], [2], [3] and [4] exist
                            ras_03 = Con(((raster_set[4] >= threshold) &
                                          (~((raster_set[3] >= threshold) |
                                             (raster_set[2] >= threshold) |
                                             (raster_set[0] >= threshold)))), self.lifespans[4])
                            if arcpy.Exists(raster_set[5]):
                                ## given raster_set[0], [2], [3], [4] and [5] exist
                                ras_04 = Con(((raster_set[5] >= threshold) &
                                              (~((raster_set[4] >= threshold) |
                                                 (raster_set[3] >= threshold) |
                                                 (raster_set[2] >= threshold) |
                                                 (raster_set[0] >= threshold)))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02, ras_03, ras_04], "SUM", "DATA")
                            else:
                                ## raster_set[1] and [5] do not exist
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02, ras_03], "SUM", "DATA")
                        else:
                            ## raster_set[0], [2], [3] and [4] exist only
                            ras_stat = CellStatistics([ras_00, ras_01], "SUM", "DATA")

                    else:
                        ## raster_set[0], [2] and [4] exist
                        ras_02 = Con(((raster_set[4] >= threshold) &
                                      (~((raster_set[2] >= threshold) |
                                         (raster_set[0] >= threshold)))), self.lifespans[4])
                        if arcpy.Exists(raster_set[5]):
                            ## raster_set[0], [2], [4] and [5] exist
                            ras_03 = Con(((raster_set[5] >= threshold) &
                                          (~((raster_set[4] >= threshold) |
                                             (raster_set[2] >= threshold) |
                                             (raster_set[0] >= threshold)))), self.lifespans[5])
                            ras_stat = CellStatistics([ras_00, ras_01, ras_02, ras_03], "SUM", "DATA")
                        else:
                            ## raster_set[1], [3] and [5] do not exist
                            ras_stat = CellStatistics([ras_00, ras_01, ras_02], "SUM", "DATA")

                else:
                    if arcpy.Exists(raster_set[3]):
                        ## given raster_set[0] and [3] exist
                        ras_01 = Con(((raster_set[3] >= threshold) &
                                      (~(raster_set[0] >= threshold))), self.lifespans[3])
                        if arcpy.Exists(raster_set[4]):
                            ## raster_set[0], [3] and [4] exist
                            ras_02 = Con(((raster_set[4] >= threshold) &
                                          (~((raster_set[3] >= threshold) |
                                             (raster_set[0] >= threshold)))), self.lifespans[4])
                            if arcpy.Exists(raster_set[5]):
                                ## raster_set[0], [3], [4] and [5] exist
                                ras_03 = Con(((raster_set[5] >= threshold) &
                                              (~((raster_set[4] >= threshold) |
                                                 (raster_set[3] >= threshold) |
                                                 (raster_set[0] >= threshold)))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02, ras_03], "SUM", "DATA")
                            else:
                                ## raster_set[0], [3] and [4] exist only
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02], "SUM", "DATA")
                        else:
                            ## raster_set[0], [3] and [5] exist
                            if arcpy.Exists(raster_set[5]):
                                ras_02 = Con(((raster_set[5] >= threshold) &
                                              (~(raster_set[0] >= threshold))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02], "SUM", "DATA")
                            else:
                                ## raster_set[0], [3] exist only
                                ras_stat = CellStatistics([ras_00, ras_01], "SUM", "DATA")
                    else:
                        if arcpy.Exists(raster_set[4]):
                            ## raster_set[0] and [4] exist
                            ras_01 = Con(((raster_set[4] >= threshold) &
                                          (~(raster_set[0] >= threshold))), self.lifespans[4])
                            if arcpy.Exists(raster_set[5]):
                                ## given raster_set[0], [4] and [5] exist
                                ras_02 = Con(((raster_set[5] >= threshold) &
                                              (~((raster_set[4] >= threshold) |
                                                 (raster_set[0] >= threshold)))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02], "SUM", "DATA")
                            else:
                                ## raster_set[0] and [4] exist only
                                ras_stat = CellStatistics([ras_00, ras_01], "SUM", "DATA")
                        else:
                            if arcpy.Exists(raster_set[5]):
                                ## given raster_set[0] and [5] exist
                                ras_01 = Con(((raster_set[5] >= threshold) &
                                              (~(raster_set[0] >= threshold))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01], "SUM", "DATA")
                            else:
                                ## only ras_stat[0] exists
                                ras_stat = CellStatistics([ras_00], "SUM", "DATA")

        else:
            # raster_set[0] does not exist
            if arcpy.Exists(raster_set[1]):
                ras_00 = Con((raster_set[1] >= threshold), self.lifespans[1])  # added for BoxElder survival
                if arcpy.Exists(raster_set[2]):
                    ## raster_set[1] and [2] exist
                    ras_01 = Con(((raster_set[2] >= threshold) &
                                  (~(raster_set[1] >= threshold))), self.lifespans[2])
                    if arcpy.Exists(raster_set[3]):
                        ## raster_set[1], [2] and [3] exist
                        ras_02 = Con(((raster_set[3] >= threshold) &
                                      (~((raster_set[2] >= threshold) |
                                         (raster_set[1] >= threshold)))), self.lifespans[3])
                        if arcpy.Exists(raster_set[4]):
                            ## raster_set[1], [2], [3] and [4] exist
                            ras_03 = Con(((raster_set[4] >= threshold) &
                                          (~((raster_set[3] >= threshold) |
                                             (raster_set[2] >= threshold) |
                                             (raster_set[1] >= threshold)))), self.lifespans[4])
                            if arcpy.Exists(raster_set[5]):
                                ## raster_set[1], [2], [3], [4] and [5] exist
                                ras_04 = Con(((raster_set[5] >= threshold) &
                                              (~((raster_set[4] >= threshold) |
                                                 (raster_set[3] >= threshold) |
                                                 (raster_set[2] >= threshold) |
                                                 (raster_set[1] >= threshold)))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02, ras_03, ras_04], "SUM", "DATA")
                            else:
                                ## raster_set[1], [2], [3], [4] exist only
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02, ras_03], "SUM", "DATA")
                        else:
                            if arcpy.Exists(raster_set[5]):
                                ## raster_set[1], [2], [3] and [5] exist
                                ras_03 = Con(((raster_set[5] >= threshold) &
                                              (~((raster_set[3] >= threshold) |
                                                 (raster_set[2] >= threshold) |
                                                 (raster_set[1] >= threshold)))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02, ras_03], "SUM", "DATA")
                            else:
                                ## raster_set[1], [2], [3], [5] exist
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02], "SUM", "DATA")

                    else:
                        if arcpy.Exists(raster_set[4]):
                            ## raster_set[1], [2] and [4] exist
                            ras_02 = Con(((raster_set[4] >= threshold) &
                                          (~((raster_set[2] >= threshold) |
                                             (raster_set[1] >= threshold)))), self.lifespans[4])
                            if arcpy.Exists(raster_set[5]):
                                ## raster_set[1], [2], [4] and [5] exist
                                ras_03 = Con(((raster_set[5] >= threshold) &
                                              (~((raster_set[4] >= threshold) |
                                                 (raster_set[2] >= threshold) |
                                                 (raster_set[1] >= threshold)))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02, ras_03], "SUM", "DATA")
                            else:
                                ## raster_set[1], [2] and [4] exist
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02], "SUM", "DATA")
                        else:
                            if arcpy.Exists(raster_set[5]):
                                ## raster_set[1], [2] and [5] exist
                                ras_02 = Con(((raster_set[5] >= threshold) &
                                              (~((raster_set[3] >= threshold) |
                                                 (raster_set[2] >= threshold) |
                                                 (raster_set[1] >= threshold)))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02], "SUM", "DATA")
                            else:
                                ## raster_set[1], [2] exist only
                                ras_stat = CellStatistics([ras_00, ras_01], "SUM", "DATA")

                else:
                    ## raster_set [2] and [0] do not exist
                    if arcpy.Exists(raster_set[3]):
                        ## raster_set[3] and [1] exist
                        ras_01 = Con(((raster_set[3] >= threshold) &
                                      (~(raster_set[1] >= threshold))), self.lifespans[3])
                        if arcpy.Exists(raster_set[4]):
                            ## raster_set[4], [3] and [1] exist
                            ras_02 = Con(((raster_set[4] >= threshold) &
                                          (~((raster_set[3] >= threshold) |
                                             (raster_set[1] >= threshold)))), self.lifespans[4])
                            if arcpy.Exists(raster_set[5]):
                                ## raster_set[5], [4], [3] and [1] exist
                                ras_03 = Con(((raster_set[5] >= threshold) &
                                              (~((raster_set[4] >= threshold) |
                                                 (raster_set[3] >= threshold) |
                                                 (raster_set[1] >= threshold)))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02, ras_03], "SUM", "DATA")
                            else:
                                ## raster_set[4], [3] and [1] exist
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02], "SUM", "DATA")
                        else:
                            if arcpy.Exists(raster_set[5]):
                                ## raster_set[5], [3] and [1] exist
                                ras_02 = Con(((raster_set[5] >= threshold) &
                                              (~((raster_set[3] >= threshold) |
                                                 (raster_set[1] >= threshold)))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02], "SUM", "DATA")
                            else:
                                ## raster_set [3] and [1] exist only
                                ras_stat = CellStatistics([ras_00, ras_01], "SUM", "DATA")
                    else:
                        if arcpy.Exists(raster_set[4]):
                            ## raster_set[4] and [1] exist
                            ras_01 = Con(((raster_set[4] >= threshold) &
                                          (~(raster_set[1] >= threshold))), self.lifespans[4])
                            if arcpy.Exists(raster_set[5]):
                                ## raster_set[5], [4] and [1] exist
                                ras_02 = Con(((raster_set[5] >= threshold) &
                                              (~((raster_set[4] >= threshold) |
                                                 (raster_set[1] >= threshold)))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02], "SUM", "DATA")
                            else:
                                ## raster_set[4] and [1] exist only
                                ras_stat = CellStatistics([ras_00, ras_01,], "SUM", "DATA")
                        else:
                            ## raster_set[5] and [1] exist
                            if arcpy.Exists(raster_set[5]):
                                ras_01 = Con(((raster_set[5] >= threshold) &
                                              (~(raster_set[1] >= threshold))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01], "SUM", "DATA")
                            else:
                                ## raster_set[1] exists only
                                ras_stat = CellStatistics([ras_00], "SUM", "DATA")

            else:
                # raster_set[0] and [1] do not exist
                if arcpy.Exists(raster_set[2]):
                    ras_00 = Con((raster_set[2] >= threshold), self.lifespans[2])  # added for BoxElder survival
                    if arcpy.Exists(raster_set[3]):
                        ## raster_set[2] and [3] exist
                        ras_01 = Con(((raster_set[3] >= threshold) &
                                      (~(raster_set[2] >= threshold))), self.lifespans[3])
                        if arcpy.Exists(raster_set[4]):
                            ## raster_set[2], [3] and [4] exist
                            ras_02 = Con(((raster_set[4] >= threshold) &
                                          (~((raster_set[3] >= threshold) |
                                             (raster_set[2] >= threshold)))), self.lifespans[4])
                            if arcpy.Exists(raster_set[5]):
                                ## raster_set[2], [3], [4] and [5] exist
                                ras_03 = Con(((raster_set[5] >= threshold) &
                                              (~((raster_set[4] >= threshold) |
                                                 (raster_set[3] >= threshold) |
                                                 (raster_set[2] >= threshold)))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02, ras_03], "SUM", "DATA")
                        else:
                            if arcpy.Exists(raster_set[5]):
                                ## raster_set[2], [3] and [5] exist
                                ras_02 = Con(((raster_set[5] >= threshold) &
                                              (~((raster_set[3] >= threshold) |
                                                 (raster_set[2] >= threshold)))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02], "SUM", "DATA")
                            else:
                                ## raster_set[2], [3] exist only
                                ras_stat = CellStatistics([ras_00, ras_01], "SUM", "DATA")

                    else:
                        if arcpy.Exists(raster_set[4]):
                            ## raster_set[2] and [4] exist
                            ras_01 = Con(((raster_set[4] >= threshold) &
                                          (~(raster_set[2] >= threshold))), self.lifespans[4])
                            if arcpy.Exists(raster_set[5]):
                                ## raster_set[2], [4] and [5] exist
                                ras_02 = Con(((raster_set[5] >= threshold) &
                                              (~((raster_set[4] >= threshold) |
                                                 (raster_set[2] >= threshold)))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02], "SUM", "DATA")
                            else:
                                ## raster_set[2], [4] exist only
                                ras_stat = CellStatistics([ras_00, ras_01], "SUM", "DATA")
                        else:
                            if arcpy.Exists(raster_set[5]):
                                ## raster_set[2] and [5] exist
                                ras_01 = Con(((raster_set[5] >= threshold) &
                                              (~(raster_set[2] >= threshold))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01], "SUM", "DATA")
                            else:
                                ## raster_set[2] exists only
                                ras_stat = CellStatistics([ras_00], "SUM", "DATA")

                else:
                    # raster_set[0], [1] and [2] do not exist
                    if arcpy.Exists(raster_set[3]):
                        ras_00 = Con((raster_set[3] >= threshold), self.lifespans[3])  # added for BoxElder survival
                        if arcpy.Exists(raster_set[4]):
                            ## raster_set[3] and [4] exist
                            ras_01 = Con(((raster_set[4] >= threshold) &
                                          (~(raster_set[3] >= threshold))), self.lifespans[4])
                            if arcpy.Exists(raster_set[5]):
                                ## raster_set[3], [4] and [5] exist
                                ras_02 = Con(((raster_set[5] >= threshold) &
                                              (~((raster_set[4] >= threshold) |
                                                 (raster_set[3] >= threshold)))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01, ras_02], "SUM", "DATA")
                            else:
                                ras_stat = CellStatistics([ras_00, ras_01], "SUM", "DATA")
                        else:
                            if arcpy.Exists(raster_set[5]):
                                ## raster_set[3] and [5] exist
                                ras_01 = Con(((raster_set[5] >= threshold) &
                                              (~(raster_set[3] >= threshold))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01], "SUM", "DATA")
                            else:
                                ## raster_set[3] exists only
                                ras_stat = CellStatistics([ras_00], "SUM", "DATA")
                    else:
                        # raster_set[0], [1], [2] and [3] do not exist
                        if arcpy.Exists(raster_set[4]):
                            ras_00 = Con((raster_set[4] >= threshold), self.lifespans[4])  # added for BoxElder survival
                            if arcpy.Exists(raster_set[5]):
                                ## raster_set[4] and [5] exist
                                ras_01 = Con(((raster_set[5] >= threshold) &
                                              (~(raster_set[4] >= threshold))), self.lifespans[5])
                                ras_stat = CellStatistics([ras_00, ras_01], "SUM", "DATA")
                            else:
                                ## raster_set[4] exists only
                                ras_stat = CellStatistics([ras_00], "SUM", "DATA")
                        else:
                            # raster_set[0], [1], [2], [3] and [4] do not exist
                            if arcpy.Exists(raster_set[5]):
                                ras_00 = Con((raster_set[5] >= threshold),
                                             self.lifespans[5])  # added for BoxElder survival
                                ras_stat = CellStatistics([ras_00], "SUM", "DATA")

        if "ras_stat" in locals():
            return(ras_stat)
        else:
            self.logger.info("ERROR: Insufficient data. Check raster consistency and add more flows(?).")


    def design_filter(self, Dmaxf):
        ## Returns minimum filter grain sizes for fine sediment
        try:
            arcpy.CheckOutExtension('Spatial')  # check out license
            arcpy.gp.overwriteOutput = True
            arcpy.env.workspace = self.cache
            self.logger.info("      >>> Designing filter stability.")
            Dmean = GrainSizes(self.condition)  # in ft
            ras_D15c = Dmean.raster * 0.25 * 12 # factor 0.25 from approximation of 2008 map (cFi Excel) and 12 in/ft
            self.ras_D15 = ras_D15c / 20
            self.ras_D85 = ras_D15c / 5
            temp_D15 = Con((self.ras_D85 < Dmaxf), self.ras_D15)
            temp_D85 = Con((self.ras_D85 < Dmaxf), self.ras_D85)
            self.ras_D15 = temp_D15
            self.ras_D85 = temp_D85
            self.raster_dict_ds.update({"ras_D15": self.ras_D15})
            self.raster_dict_ds.update({"ras_D85": self.ras_D85})
            arcpy.CheckInExtension('Spatial')
        except arcpy.ExecuteError:
            self.logger.info("ExecuteERROR: (arcpy) in filter stability.")
            self.logger.info(arcpy.GetMessages(2))
            arcpy.AddError(arcpy.GetMessages(2))
        except Exception as e:
            self.logger.info("ExceptionERROR: (arcpy) in filter stability.")
            self.logger.info(e.args[0])
            arcpy.AddError(e.args[0])
        except:
            self.logger.info("ERROR: (arcpy) in filter stability.")
            self.logger.info(arcpy.GetMessages())

    def design_slopes(self):
        ## Returns minimum filter grain sizes for fine sediment
        try:
            arcpy.CheckOutExtension('Spatial')  # check out license
            arcpy.gp.overwriteOutput = True
            arcpy.env.workspace = self.cache
            self.logger.info("      >>> Comparing energy slope with terrain slope.")
            dem = DEM(self.condition)       # in ft a.s.l.
            h = FlowDepth(self.condition)   # (ft)
            u = FlowVelocity(self.condition)# (fps)
            outMeasurement = "PERCENT_RISE"
            zFactor = 1.0
            egl_dict = {}
            Se_dict = {}
            cSe_dict = {}

            S0 = (Slope(dem.raster, outMeasurement, zFactor))/100 # (--)


            if (h.raster_names.__len__() >= u.raster_names.__len__()):
                self.logger.info("      >>> Module successfully launched - please wait ...")
                for ras_no in range(0, h.raster_names.__len__()):
                    ## compute energetic level
                    egl_dict.update(
                        {ras_no: dem.raster + h.rasters[ras_no] + (Square(u.rasters[ras_no]) / (2 * self.g))})
                    ## uncomment the following line to use minimum energy slope instead
                    # egl_dict.update({ras_no: dem.raster + 1.5 * Power((((Square(h.rasters[ras_no]) *
                    #                                                    (Square(u.rasters[ras_no]))) / self.g)), (1/3))})
                    ## compute energy slope Se
                    Se_dict.update({ras_no: (Slope(egl_dict[ras_no], outMeasurement, zFactor))/100})
                    ## result = compare Se and S0 (Se / S0)
                    ras_name = "cSe_" + h.raster_names[ras_no][1:4]
                    cSe_dict.update({ras_name: Con(~(((Se_dict[ras_no] / S0) == 1) | ((Se_dict[ras_no] / S0) < 0)),
                                                   (Se_dict[ras_no] / S0))})
                    # cSe_dict.update({ras_name: Con(~(((Se_dict[ras_no] / S0) == 1)),
                    #                                (Se_dict[ras_no]))})
                    self.raster_dict_ds.update({ras_name: cSe_dict[ras_name]})

            arcpy.CheckInExtension('Spatial')
        except arcpy.ExecuteError:
            self.logger.info("ExecuteERROR: (arcpy) in slope comparison.")
            self.logger.info(arcpy.GetMessages(2))
            arcpy.AddError(arcpy.GetMessages(2))
        except Exception as e:
            self.logger.info("ExceptionERROR: (arcpy) in slope comparison.")
            self.logger.info(e.args[0])
            arcpy.AddError(e.args[0])
        except:
            self.logger.info("ERROR: (arcpy) in slope comparison.")
            self.logger.info(arcpy.GetMessages())

    def design_side_channel(self):

        try:
            arcpy.CheckOutExtension('Spatial')  # check out license
            arcpy.gp.overwriteOutput = True
            arcpy.env.workspace = self.cache
            self.logger.info("      >>> Applying side channel delineation ...")

            self.sch = SideChannelDelineation(self.condition)
            ## routine to override noData pixels if required.
            if arcpy.Exists(self.sch.raster):
                self.ras_sch = Con((IsNull(self.sch.raster) == 1), (IsNull(self.sch.raster) * 0), self.sch.raster)
                remap = RemapValue([[0, 0], [1, 200], [2, 127], [3, 47], [4, 25], [5, 12], [6, 9]])
                reclass = Reclassify(self.ras_sch, "VALUE", remap, "DATA")

                if self.verify_raster_info():
                    self.logger.info("            based on raster: " + self.raster_info_lf)
                    ## apply delineation to existing rasters and make low-relevance areas (6) to lf smaller one (div 7)
                    ras_sch_new = Con((self.ras_sch > 0), Con((self.ras_sch == 6), (reclass / 10.0),
                                                              Con(~(IsNull(self.raster_dict_lf[self.raster_info_lf])),
                                                                  self.raster_dict_lf[self.raster_info_lf], (reclass / 10.0))))
                else:
                    ras_sch_new = reclass
                self.ras_sch = ras_sch_new

            self.raster_info_lf = "ras_sch"
            self.raster_dict_lf.update({self.raster_info_lf: self.ras_sch})
            arcpy.CheckInExtension('Spatial')
        except arcpy.ExecuteError:
            self.logger.info("ExecuteERROR: (arcpy) in side channel delineation.")
            self.logger.info(arcpy.GetMessages(2))
            arcpy.AddError(arcpy.GetMessages(2))
        except Exception as e:
            self.logger.info("ExceptionERROR: (arcpy) in side channel delineation.")
            self.logger.info(e.args[0])
            arcpy.AddError(e.args[0])
        except:
            self.logger.info("ERROR: (arcpy) in side channel delineation.")
            self.logger.info(arcpy.GetMessages())

    def design_stable_grains(self, threshold_taux):
        ## Returns stable grain size in inches
        try:
            arcpy.CheckOutExtension('Spatial')  # check out license
            arcpy.gp.overwriteOutput = True
            arcpy.env.workspace = self.cache
            self.logger.info("      >>> Calculating stable grain sizes (spatial).")
            h = FlowDepth(self.condition)
            u = FlowVelocity(self.condition)

            self.logger.info("             -- mobility frequency = " + str(self.threshold_freq) + " years")

            try:
                i = self.lifespans.index(self.threshold_freq)
            except:
                i = 0
                self.logger.info("WARNING Design map: Could not assign frequency threshold. Using default (annual flood).")

            self.ras_Dst = (Square(u.rasters[i] * self.n) / ((self.s - 1) * threshold_taux *
                                                              Power(h.rasters[i], (1 / 3)))) * 12 * self.sf

                ## test an alternative using arcpy s Slope function:
                # outMeasurement = "PERCENT_RISE"
                # zFactor = 1.0
                # dem = DEM(self.condition)
                # ras_energy = dem.raster + h.rasters[5] + Square(u.rasters[5]) / (2 * self.g)
                # ras_Se = (Slope(ras_energy, outMeasurement, zFactor))/100
                # self.ras_DSe = (h.rasters[5] * ras_Se / ((self.s - 1) * threshold_taux )) * 12
                # self.raster_dict_ds.update({"ras_DSe": self.ras_DSe})

            temp_ras = Con(self.ras_Dst < 300, self.ras_Dst) # eliminate outliers at structures (PowerHouse, Sills)
            self.ras_Dst = temp_ras
            self.raster_dict_ds.update({"ras_Dst": self.ras_Dst})

            arcpy.CheckInExtension('Spatial')
        except arcpy.ExecuteError:
            self.logger.info("ExecuteERROR: (arcpy) in Dst.")
            self.logger.info(arcpy.GetMessages(2))
            arcpy.AddError(arcpy.GetMessages(2))

        except Exception as e:
            self.logger.info("ExceptionERROR: (arcpy) in Dst.")
            self.logger.info(e.args[0])
            arcpy.AddError(e.args[0])

        except:
            self.logger.info("ERROR: (arcpy) in Dst.")
            self.logger.info(arcpy.GetMessages())

    def design_wood(self):
        ## Returns stable grain size in inches
        try:
            arcpy.CheckOutExtension('Spatial')  # check out license
            arcpy.gp.overwriteOutput = True
            arcpy.env.workspace = self.cache
            self.logger.info("      >>> Calculating stable log diameter (spatial).")
            h = FlowDepth(self.condition)
            try:
                i = self.lifespans.index(self.threshold_freq)
            except:
                i = 0
                self.logger.info("WARNING Design map: Could not assign frequency threshold. Using default (annual flood).")

            ## assumption: probability of motion = 0
            self.ras_Dw = 0.32/0.18 * h.rasters[i] * 12 #(inches)

            temp_ras = Con(self.ras_Dw < 300, self.ras_Dw)  # eliminate outliers at structures (PowerHouse, Sills)
            self.ras_Dw = temp_ras
            self.raster_dict_ds.update({"ras_Dw": self.ras_Dw})

        except arcpy.ExecuteError:
            self.logger.info("ExecuteERROR: (arcpy) in Design Wood Dw.")
            self.logger.info(arcpy.GetMessages(2))
            arcpy.AddError(arcpy.GetMessages(2))

        except Exception as e:
            self.logger.info("ExceptionERROR: (arcpy) in Design Wood Dw.")
            self.logger.info(e.args[0])
            arcpy.AddError(e.args[0])

        except:
            self.logger.info("ERROR: (arcpy) in Design Wood Dw.")
            self.logger.info(arcpy.GetMessages())

    def join_with_habitat(self):
        try:
            arcpy.CheckOutExtension('Spatial')  # check out license
            arcpy.gp.overwriteOutput = True
            arcpy.env.workspace = self.cache
            self.logger.info("   >> Matching with cHSI raster.")
            precision = 10.0 * self.m2ft  # match points in a radius of 400 feet

            chsi = CHSI(self.condition)
            self.logger.info("           processing takes time ...")
            ## create point feature from relevant chsi points only
            points_chsi = arcpy.RasterToPoint_conversion(Con(((chsi.raster > 0) & (chsi.raster < 0.5)),
                                                             chsi.raster), self.cache + "chsi_points.shp")


            if self.verify_raster_info() and (self.raster_dict_lf.__len__() > 0):
                self.logger.info("            lifespan raster: " + self.raster_info_lf)
                ## limit base_raster to relevant areas only
                ras_base = Con((self.raster_dict_lf[self.raster_info_lf] > 0),
                                    self.raster_dict_lf[self.raster_info_lf])
                points_base = arcpy.RasterToPoint_conversion(ras_base, self.cache + "lf_points.shp")

                base_join = arcpy.SpatialJoin_analysis(target_features=points_chsi, join_features=points_base,
                                                       out_feature_class=arcpy.FeatureSet,
                                                       join_operation='JOIN_ONE_TO_MANY',
                                                       match_option='WITHIN_A_DISTANCE',
                                                       search_radius=precision)
                # base_join = arcpy.SpatialJoin_analysis(points_chsi, points_base,
                #                                        arcpy.FeatureSet, '', '', '',
                #                                        'CLOSEST', precision, 'Distance')


                # self.logger.info("These are base_joins fields:")
                # self.logger.info(str(arcpy.ListFields(base_join)))
                ras_new = arcpy.PointToRaster_conversion(base_join, "grid_cod_1", self.cache + "lf_habitat")

                ## compare temp_ras with raster_dict but use self.ras_... values if condition is True
                self.ras_hab = Con((ras_new > 0), self.raster_dict_lf[self.raster_info_lf])
                self.raster_info_lf = "ras_hab"
                self.raster_dict_lf.update({self.raster_info_lf: self.ras_hab})


            if self.verify_raster_info() and (self.raster_dict_ds.__len__() > 0):

                i = 0
                for ras_ds in self.raster_dict_ds.keys():
                    self.logger.info("            design raster: " + str(ras_ds))
                    ras_base = Con((self.raster_dict_ds[ras_ds] > 0), self.raster_dict_ds[ras_ds])
                    points_base = arcpy.RasterToPoint_conversion(ras_base, self.cache + "ds_points" + str(i))
                    base_join = arcpy.SpatialJoin_analysis(target_features=points_chsi, join_features=points_base,
                                                           out_feature_class=arcpy.FeatureSet,
                                                           join_operation='JOIN_ONE_TO_MANY',
                                                           match_option='WITHIN_A_DISTANCE',
                                                           search_radius=precision)
                    ## reconvert to raster - grid_cod_1 corresponds to lf raster value (chsi value was field=grid_code)
                    ras_new = arcpy.PointToRaster_conversion(base_join, "grid_cod_1", self.cache + "ds_habitat" + str(i))

                    ## update ds_dict
                    # self.raster_dict_ds.update({"ras_hab" + str(i): Con((ras_new > 0), self.raster_dict_ds[ras_ds])})
                    self.raster_dict_ds.update({"ras_hab" + str(i): ras_new})
                    del self.raster_dict_ds[ras_ds]
                    i += 1

            arcpy.CheckInExtension('Spatial')
        except arcpy.ExecuteError:
            self.logger.info("ExecuteERROR: (arcpy) habitat matching.")
            self.logger.info(arcpy.GetMessages(2))
            arcpy.AddError(arcpy.GetMessages(2))
        except Exception as e:
            self.logger.info("ExceptionERROR: (arcpy) habitat matching.")
            self.logger.info(e.args[0])
            arcpy.AddError(e.args[0])
        except:
            self.logger.info("ERROR: (arcpy) habitat matching.")
            self.logger.info(arcpy.GetMessages())



    def save_manager(self, ds, lf, name):
        if lf:
            self.save_lifespan(name)
        if ds and lf:
            self.save_design(name)
        if ds and not(lf):
            ## applies when lifespan methods are used for creating ONE design raster
            if not(bool(self.raster_dict_ds)):
                self.raster_dict_ds.update({self.raster_info_lf : self.raster_dict_lf[self.raster_info_lf]})
            self.save_design(name)

    def save_design(self, name):
        ## Copy last RasterDataset as Esri Grid file to OutputRasters folder
        # dir = path (str)
        # map type =  either "lf" or "ds" (str) for lifespan / design maps
        # name = feature shortname (str, max. 6 char. for design maps)

        if (name.__len__() > 6):
            ## shorten name if required
            self.logger.info("   >> Hint: shortname too long - applying instead: " + str(name[:6]))
            name = name[:6]

        try:
            arcpy.CheckOutExtension('Spatial')  # check out license
            arcpy.gp.overwriteOutput = True
            arcpy.env.workspace = self.cache
            for ras in reversed(self.raster_dict_ds.keys()):
                self.logger.info("   >> Saving design map " + ras + " (takes time) ... ")
                self.raster_dict_ds[ras].save(self.cache + ras)
                if ras[4:].__len__() > 3:
                    par_name = ras[4:]
                else:
                    par_name = ras[4:7]
                self.logger.info("   >> Casting to /OutputRasters/" + self.condition + "/ds_" + name + "_" + par_name +
                                 " (may take time) ...")
                arcpy.CopyRaster_management(self.cache + ras, self.output + "ds_" + name + "_" + par_name)
            try:
                self.logger.info("   >> Clearing .cache (arcpy.Delete_management - temp.designs - please wait) ...")
                for ras in self.raster_dict_ds:
                    arcpy.Delete_management(self.raster_dict_ds[ras])
                self.logger.info("   >> Done.")
            except:
                self.logger.info("WARNING: .cache folder removed by package control.")
            arcpy.CheckInExtension('Spatial')
        except arcpy.ExecuteError:
            self.logger.info(arcpy.GetMessages(2))
            arcpy.AddError(arcpy.GetMessages(2))
            for ras in self.raster_dict_ds:
                arcpy.Delete_management(self.raster_dict_ds[ras])
            self.logger.info("Cache cleared (arcpy.Delete_management).")
        except Exception as e:
            self.logger.info(e.args[0])
            arcpy.AddError(e.args[0])
            for ras in self.raster_dict_ds:
                arcpy.Delete_management(self.raster_dict_ds[ras])
            self.logger.info("Cache cleared (arcpy.Delete_management).")
        except:
            self.logger.info("ERROR: "+ name + " - raster copy to OutputRasters folder failed raster failed.")
            self.logger.info(arcpy.GetMessages())
            for ras in self.raster_dict_ds:
                arcpy.Delete_management(self.raster_dict_ds[ras])
            self.logger.info("Cache cleared (arcpy.Delete_management).")

    def save_lifespan(self, name):
        ## Copy last RasterDataset as Esri Grid file to OutputRasters folder
        # dir = path (str)
        # map type =  either "lf" or "ds" (str) for lifespan / design maps
        # name = feature shortname (str, max. 10 char.)

        if (name.__len__() > 10):
            ## shorten name if required
            name = name[:10]


        try:
            arcpy.CheckOutExtension('Spatial')  # check out license
            arcpy.gp.overwriteOutput = True
            arcpy.env.workspace = self.cache
            self.logger.info("   >> Saving (takes time) ... ")
            self.raster_dict_lf[self.raster_info_lf].save(self.cache + self.raster_info_lf)
            self.logger.info("   >> Casting to /OutputRasters/" + self.condition + "/lf_" + name + " (may take time) ...")
            arcpy.CopyRaster_management(self.cache + self.raster_info_lf, self.output + "lf_" + name)
            try:
                self.logger.info("   >> Clearing cache (arcpy.Delete_management - temp.lifespans - please wait) ...")
                for ras in self.raster_dict_lf:
                    try:
                        arcpy.Delete_management(self.raster_dict_lf[ras])
                    except:
                        pass
                arcpy.CheckInExtension('Spatial')
                self.logger.info("   >> Done.")
            except:
                self.logger.info("WARNING: .cache folder removed by package control.")

        except arcpy.ExecuteError:
            print arcpy.GetMessages(2)
            arcpy.AddError(arcpy.GetMessages(2))
            for ras in self.raster_dict_lf:
                arcpy.Delete_management(self.raster_dict_lf[ras])
            self.logger.info("Cache cleared (arcpy.Delete_management).")
        except Exception as e:
            print e.args[0]
            arcpy.AddError(e.args[0])
            for ras in self.raster_dict_lf:
                arcpy.Delete_management(self.raster_dict_lf[ras])
            self.logger.info("Cache cleared (arcpy.Delete_management).")
        except:
            self.logger.info("ERROR: "+ name + "- raster copy to OutputRasters folder failed raster failed.")
            self.logger.info(arcpy.GetMessages())
            for ras in self.raster_dict_lf:
                arcpy.Delete_management(self.raster_dict_lf[ras])
            self.logger.info("Cache cleared (arcpy.Delete_management).")



    def verify_inverse_tcd(self, inverse):
        ## inverse is boolean (False or True)
        self.inverse_tcd = inverse

    def verify_sf(self, sf):
        ## inverse is boolean (False or True)
        try:
            self.sf = float(sf)
        except:
            self.sf = 1

    def verify_threshold_freq(self, freq):
        ## inverse is boolean (False or True)
        try:
            self.threshold_freq = float(freq)
        except:
            self.threshold_freq = 0.0

    def verify_raster_info(self):
        if self.raster_info_lf in self.raster_dict_lf:
            return(True)


    def __call__(self):
        pass