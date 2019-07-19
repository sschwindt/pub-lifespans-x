
import os, sys
import Tkinter as tk
from tkMessageBox import askokcancel, showinfo
import webbrowser


class RunGui():
    def __init__(self, master):
        self.path = r"" + os.path.dirname(os.path.abspath(__file__))

        # Construct the Frame object.
        self.master = tk.Toplevel(master)
        self.master.wm_title("ISSUE - CHECK CONSOLE MESSAGES")
        self.master.bell()

        self.msg = ""
        self.xd = 5  # distance holder in x-direction (pixel)
        self.yd = 5  # distance holder in y-direction (pixel)
        # ARRANGE GEOMETRY
        ww = 400
        wh = 100
        wx = (self.master.winfo_screenwidth() - ww) / 2
        wy = (self.master.winfo_screenheight() - wh) / 2
        self.master.geometry("%dx%d+%d+%d" % (ww, wh, wx, wy))


    def gui_raster_maker(self, condition, feature_list, mapping, habitat):
        import feature_analysis as fa
        fa.raster_maker(condition, feature_list, mapping, habitat)

    def gui_layout_maker(self, condition):
        import feature_analysis as fa
        fa.layout_maker(condition)

    def gui_map_maker(self, condition):
        import feature_analysis as fa
        fa.map_maker(condition)

    def gui_quit(self):
        self.master.destroy()

    def open_log_file(self):
        logfilenames = ["error.log", "rasterlogfile.log", "logfile.log", "map_logfile.log", "mxd_logfile.log"]
        for filename in logfilenames:
            _f = r'' + os.path.dirname(os.path.abspath(__file__)) + "\\" + filename
            if os.path.isfile(_f):
                try:
                    webbrowser.open(_f)
                except:
                    pass

class FaGui(tk.Frame):
    def __init__(self, master = None):
        self.path = r"" + os.path.dirname(os.path.abspath(__file__))
        self.py_path = r"C:/Python27/ArcGISx6410.5/python.exe"
        self.feature_list = []
        self.condition = ""
        self.verified = False
        self.errors = False
        self.habitat = False
        self.mapping = False

        # Construct the Frame object.
        tk.Frame.__init__(self, master)
        self.pack(expand=True, fill=tk.BOTH)
        self.master.iconbitmap(os.path.dirname(os.path.abspath(__file__))+"\\Documentation\\code_icon.ico")

        self.xd = 5  # distance holder in x-direction (pixel)
        self.yd = 5  # distance holder in y-direction (pixel)
        # ARRANGE GEOMETRY
        # Width and height of the window.
        ww = 700
        wh = 200
        # Upper-left corner of the window.
        wx = (self.master.winfo_screenwidth() - ww) / 2
        wy = (self.master.winfo_screenheight() - wh) / 2
        # Set the height and location.
        self.master.geometry("%dx%d+%d+%d" % (ww, wh, wx, wy))
        # Give the window a title.
        self.master.title("Lifespan Mapping")

        # GUI OBJECT VARIABLES
        self.gui_condition = tk.StringVar()
        self.gui_interpreter = tk.StringVar()

        # LABELS
        self.l_s_feat = tk.Label(self, text="Selected features: ")
        self.l_s_feat.grid(sticky=tk.W, row=0, column=0, padx=self.xd, pady=self.yd)
        self.l_features = tk.Label(self, fg = "red", text="Choose from \'Add Features\' Menu")
        self.l_features.grid(sticky=tk.W, row=0, column=1, columnspan=3, padx=self.xd, pady=self.yd)
        self.l_condition = tk.Label(self, text="Condition: ")
        self.l_condition.grid(sticky=tk.W, row = 2, column = 0, padx=self.xd, pady=self.yd)


        # ENTRIES
        self.condition_entry = tk.Entry(self, width=10, textvariable=self.gui_condition)
        self.condition_entry.grid(sticky=tk.W, row=2, column=1, padx=self.xd, pady=self.yd)

        # BUTTONS
        self.b_mod_r = tk.Button(self, width=25, bg="white", text="Modify raster input", command=lambda:
                                self.open_inp_file("input_definitions.inp"))
        self.b_mod_r.grid(sticky=tk.EW, row=4, column=0, columnspan=2, padx=self.xd, pady=self.yd)
        self.b_mod_m = tk.Button(self, width=25, bg="white", text="Modify map extent", command=lambda:
                                self.open_inp_file("mapping.inp"))
        self.b_mod_m.grid(sticky=tk.EW,row=4, column=2, columnspan=2, padx=self.xd, pady=self.yd)

        # DROP DOWN MENU
        # the menu does not need packing - see page 44ff
        self.mbar = tk.Menu(self) # create new menubar
        self.master.config(menu=self.mbar) # attach it to the root window

        # FEATURE DROP DOWN
        self.featmenu = tk.Menu(self.mbar, tearoff=0) # create new menu
        self.mbar.add_cascade(label="Add Features", menu=self.featmenu) # attach it to the menubar
        # add menu entries
        self.featmenu.add_command(label="Add: ALL", command=lambda: self.define_feature(""))
        self.featmenu.add_command(label="Add: Backwater", command=lambda: self.define_feature("Backwater"))
        self.featmenu.add_command(label="Add: Bermsetback", command=lambda: self.define_feature("Bermsetback"))
        self.featmenu.add_command(label="Add: ELJ", command=lambda: self.define_feature("ELJ"))
        self.featmenu.add_command(label="Add: Finesediment", command=lambda: self.define_feature("Finesediment"))
        self.featmenu.add_command(label="Add: Grading", command=lambda: self.define_feature("Grading"))
        self.featmenu.add_command(label="Add: Gravel", command=lambda: self.define_feature("Gravel"))
        self.featmenu.add_command(label="Add: Plantings", command=lambda: self.define_feature("Plantings"))
        self.featmenu.add_command(label="Add: Riprap", command=lambda: self.define_feature("Riprap"))
        self.featmenu.add_command(label="Add: Sidecavity", command=lambda: self.define_feature("Sidecavity"))
        self.featmenu.add_command(label="Add: Sidechannel", command=lambda: self.define_feature("Sidechannel"))
        self.featmenu.add_command(label="CLEAR ALL", command=lambda: self.define_feature("clear"))

        # RUN DROP DOWN
        self.runmenu = tk.Menu(self.mbar, tearoff=0)  # create new menu
        self.mbar.add_cascade(label="Run", menu=self.runmenu)  # attach it to the menubar
        self.runmenu.add_command(label="Verify settings", command=lambda: self.verify())
        self.runmenu.add_command(label="Run: Raster Maker", command=lambda: self.run_raster_maker())
        self.runmenu.add_command(label="Run: Layout Maker", command=lambda: self.run_layout_maker())
        self.runmenu.add_command(label="Run: Map Maker", command=lambda: self.run_map_maker())

        # CLOSE DROP DOWN
        self.closemenu = tk.Menu(self.mbar, tearoff=0)  # create new menu
        self.mbar.add_cascade(label="Close", menu=self.closemenu)  # attach it to the menubar
        self.closemenu.add_command(label="Quit programm", command=lambda: self.myquit())

        # CHECK BOXES(CHECKBUTTONS) -- uncomment if needed
        self.cb_lyt = tk.Checkbutton(self, text = "Include layout creation in raster analysis", command=lambda:
                                    self.mod_mapping())
        self.cb_lyt.grid(sticky=tk.W, row=5, column=0, columnspan=4, padx=self.xd, pady=self.yd)
        self.cb_habitat = tk.Checkbutton(self, text="Apply matching with habitat relevance", command=lambda:
                                        self.mod_habitat())
        self.cb_habitat.grid(sticky=tk.W, row=6, column=0, columnspan=4, padx=self.xd, pady=self.yd)

        # MAKE PLACEHOLDER FILL
        logo = tk.PhotoImage(file=os.path.dirname(os.path.abspath(__file__))+"\\Documentation\\illu.GIF")
        logo = logo.subsample(5,5)
        self.l_img = tk.Label(self, image=logo)
        self.l_img.image = logo
        self.l_img.grid(row=3, column=4, rowspan=4)


    def define_feature(self, feature_name):
        if feature_name.__len__() < 1:
            self.feature_list = ["Backwater", "Bermsetback", "ELJ", "Finesediment", "Grading",
                            "Gravel", "Plantings", "Riprap", "Sidecavity", "Sidechannel"]
            self.l_features.destroy()
            self.l_features = tk.Label(self, fg="SteelBlue", text=", ".join(self.feature_list))
            self.l_features.grid(sticky=tk.W, row=0, column=1, columnspan=3, padx=self.xd, pady=self.yd)
        else:
            if not(feature_name == "clear"):
                self.feature_list.append(feature_name)
                self.l_features.destroy()
                self.l_features = tk.Label(self, fg="SteelBlue", text=", ".join(self.feature_list))
                self.l_features.grid(sticky=tk.W, row=0, column=1, columnspan=3, padx=self.xd, pady=self.yd)
            else:
                self.feature_list = []
                self.l_features.destroy()
                self.l_features = tk.Label(self, fg="SteelBlue", text="Choose from \'Add Features\' Menu")
                self.l_features.grid(sticky=tk.W, row=0, column=1, columnspan=3, padx=self.xd, pady=self.yd)

    def mod_habitat(self):
        if not(self.habitat):
            self.habitat = True
        else:
            self.habitat = False

    def mod_mapping(self):
        if not(self.mapping):
            self.mapping = True
        else:
            self.mapping = False

    def myquit(self):
        if askokcancel("Close", "Do you really wish to quit?"):
            tk.Frame.quit(self)

    def open_inp_file(self, filename):
        _f = r'' + os.path.dirname(os.path.abspath(__file__)) + "\\Input\\.templates\\" + filename
        if os.path.isfile(_f):
            try:
                webbrowser.open(_f)
            except:
                showinfo("ERROR ", "Cannot open " + str(filename) +
                         ". Make sure that your operating system has a standard application defined for *.inp-files.")
        else:
            showinfo("ERROR ", "The file " + str(filename) +" does not exist. Check feature_analysis directory.")

    def open_log_file(self):
        logfilenames = ["error.log", "rasterlogfile.log", "logfile.log", "map_logfile.log", "mxd_logfile.log"]
        for filename in logfilenames:
            _f = r'' + os.path.dirname(os.path.abspath(__file__)) + "\\" + filename
            if os.path.isfile(_f):
                try:
                    webbrowser.open(_f)
                except:
                    pass

    def run_raster_maker(self):
        showinfo("INFORMATION", " Analysis takes a while. \n Python windows seem irresponsive during analysis. \n Check console messages.\n \n PRESS OK TO START")
        if not (self.verified):
            self.verify()
        if not (self.errors):
            run = RunGui(self)
            run.gui_raster_maker(self.condition, self.feature_list, self.mapping, self.habitat)
            run.gui_quit()
            self.l_features.destroy()
            self.cb_lyt.destroy()
            self.cb_habitat.destroy()
            self.l_s_feat.destroy()
            self.l_condition.destroy()
            self.condition_entry.destroy()
            self.master.bell()
            tk.Button(self, width=25, bg="forest green", text="Finished - Click to quit.\n Or Run Layout / Map Maker", command=lambda:
                        tk.Frame.quit(self)).grid(sticky=tk.EW, row=1, column=0, columnspan=3, padx=self.xd,
                                                    pady=self.yd)
            if not(self.mapping):
                tk.Button(self, bg="salmon", width=25, text="IMPORTANT\n Read logfile(s)", command=lambda:
                        self.open_log_file()).grid(sticky=tk.EW, row=1, column=3, columnspan=2, padx=self.xd, pady=self.yd)
            else:
                tk.Button(self, bg="gold", width=25, text="IMPORTANT\n Read logfile(s) from Layout Maker",
                          command=lambda:
                          self.open_log_file()).grid(sticky=tk.EW, row=1, column=3, columnspan=2, padx=self.xd,
                                                     pady=self.yd)
                showinfo("INFORMATION",
                         "Layouts (.mxd files) prepared in opened folder.\n \n >> For obtaining PDF maps do the following:\n   1) Open layouts (mxd) in ArcMap Desktop and adapt symbology of sym layer.\n   2) Save layouts (overwrite existing) without committing any other change.\n   3) Back in Python console: Run feature_analysis.map_making(condition). \n \n Then, run Map Maker to obtain PDF maps.")

        else:
            showinfo("ERROR ", "Correct verification errors.")

    def run_layout_maker(self):
        if not(self.verified):
            self.verify()
        if not (self.errors):
            run = RunGui(self)
            run.gui_layout_maker(self.condition)
            run.gui_quit()
            self.l_features.destroy()
            self.cb_lyt.destroy()
            self.cb_habitat.destroy()
            self.l_s_feat.destroy()
            self.l_condition.destroy()
            self.condition_entry.destroy()
            self.master.bell()
            tk.Button(self, width=25, bg="forest green", text="Finished - Click to quit.\n Or (re-)Run Layout / Map Maker",
                      command=lambda:
                      tk.Frame.quit(self)).grid(sticky=tk.EW, row=1, column=0, columnspan=3, padx=self.xd,
                                                pady=self.yd)
            tk.Button(self, bg="gold", width=25, text="IMPORTANT\n Read logfile(s) from Layout Maker", command=lambda:
                    self.open_log_file()).grid(sticky=tk.EW, row=1, column=3, columnspan=2, padx=self.xd, pady=self.yd)
            showinfo("INFORMATION",
                     "Layouts (.mxd files) prepared in opened folder.\n \n >> For obtaining PDF maps do the following:\n   1) Open layouts (mxd) in ArcMap Desktop and adapt symbology of sym layer.\n   2) Save layouts (overwrite existing) without committing any other change.\n   3) Back in Python console: Run feature_analysis.map_making(condition). \n \n Then, run Map Maker to obtain PDF maps.")
        else:
            showinfo("ERROR ", "Correct verification errors.")


    def run_map_maker(self):
        if not(self.verified):
            self.verify()
        if not (self.errors):
            showinfo("INFORMATION",
                     " Map creation takes up to 5 minutes. \n Python windows seem irresponsive during analysis. \n Check console messages.\n \n PRESS OK TO START")
            run = RunGui(self)
            run.gui_map_maker(self.condition)
            run.gui_quit()
            self.l_features.destroy()
            self.cb_lyt.destroy()
            self.cb_habitat.destroy()
            self.l_s_feat.destroy()
            self.l_condition.destroy()
            self.condition_entry.destroy()
            self.master.bell()
            tk.Button(self, width=25, bg="forest green", text="Finished - Click to quit.\n Or Re-Run Layout / Map Maker",
                      command=lambda:
                      tk.Frame.quit(self)).grid(sticky=tk.EW, row=1, column=0, columnspan=3, padx=self.xd,
                                                pady=self.yd)
            tk.Button(self, bg="forest green", width=25, text="IMPORTANT\n Read logfile(s) from Map Maker", command=lambda:
                    self.open_log_file()).grid(sticky=tk.EW, row=1, column=3, columnspan=2, padx=self.xd, pady=self.yd)

        else:
            showinfo("ERROR ", "Correct verification errors.")



    def verify(self):

        error_msg = []
        self.verified = True
        try:
            import feature_analysis
        except:
            error_msg.append("Check installation of feature_analysis package.")
            self.verified = False
            self.errors = True
        if not (self.feature_list.__len__() > 0):
            error_msg.append("Choose at least one feature.")
            self.verified = False
            self.errors = True
        else:
            self.l_features.destroy()
            self.l_features = tk.Label(self, fg="forest green", text=", ".join(self.feature_list))
            self.l_features.grid(sticky=tk.W, row=0, column=1, columnspan=3, padx=self.xd, pady=self.yd)
        try:
            if not ((sys.version_info.major == 2) and (sys.version_info.minor == 7)):
                error_msg.append("Wrong Python interpreter (Required: Python v.2.7 or higher but not v.3.x).")
                self.errors = True
                self.verified = False
        except:
            pass
        try:
            self.condition = self.condition_entry.get()
            dir = self.path + "\\Input\\" + str(self.condition)
            if os.path.exists(dir):
                l_condition = tk.Label(self, fg="forest green", text="Verified condition: " + self.condition)
                l_condition.grid(sticky=tk.W, row=2, column=3, padx=self.xd, pady=self.yd)
            else:
                error_msg.append("Invalid file structure (non-existent directory /Input/condition ).")
                l_condition = tk.Label(self, fg="red", text="ERROR                                 ")
                l_condition.grid(sticky=tk.W, row=2, column=3, padx=self.xd, pady=self.yd)
                self.errors = True
                self.verified = False
        except:
            error_msg.append("Invalid entry for \'Condition\'.")
            self.errors = True
        if self.errors:
            self.master.bell()
            showinfo("VERIFICATION ERRORS ", "\n ".join(error_msg))



# Allow the class to run stand-alone.
if __name__ == "__main__":
    FaGui().mainloop()
