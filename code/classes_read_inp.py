#!/usr/bin/python
# Filename: classes_read_inp.py
import os, logging

class Info(object):

    # CONSTRUCTOR
    def __init__(self, *args):
        ## type defines lines to read in .inp file
        self.alt_path=str()
        self.inp_file = r'' + os.path.dirname(os.path.abspath(__file__)) + "\\Input\\.templates\\input_definitions.inp"
        self.inp_coord = r'' + os.path.dirname(os.path.abspath(__file__)) + "\\Input\\.templates\\mapping.inp"
        self.ras_names = []
        try:
            self.type = args[0] # (str) corresponding to type_dict entries (e.g., type = "h")
        except:
            self.type = ""
            pass
        self.type_dict = {"d2w": 15, "det": 10, "dod": 9, "chsi": 8, "grains": 13, "h": 12,
                          "mu": 14, "u": 11, "dem": 16, "sidech": 17}

        self.logger = logging.getLogger("feature_analysis")

    def get_line_entries(self, line_no):
        if os.path.isfile(self.inp_file):
            file = open(self.inp_file)
            lines = file.readlines()
            the_line = lines[line_no - 1]
            the_line = the_line.split("=")[1]   # remove line first part
            the_line = the_line.split("#")[0]   # remove line end
            try:
                entries = the_line.split(",")   # applies to multiple raster definitions
                msg = "      >>> Input raster definitions of: " + str(self.type)
            except:
                entries = the_line
                msg = "ERROR: Missing (or wrong format of) raster input definitions."
            file.close()
        else:
            entries = []
            msg = "ERROR: Input file not available."
        if self.type.__len__() > 0:
            self.logger.info(msg)
        return(entries)

    def get_map_extent(self, direction):
        ## direction is either dx or dy
        if os.path.isfile(self.inp_coord):

            if direction == "x":
                line_no = 3
            if direction == "y":
                line_no = 4
            if not("line_no" in locals()):
                self.logger.info("ERROR: Bad call of map centre coordinates. Creating sqeare-x layouts.")
                line_no = 3
            file = open(self.inp_coord)
            lines = file.readlines()
            the_line = lines[line_no - 1]
            the_line = the_line.split("=")[1]  # remove line first part
            entry = the_line.split("#")[0]  # remove line end
            try:
                extent = float(entry.strip())
            except:
                extent = 7000.00
                self.logger.info("ERROR: Extent is not FLOAT. Substituting to extent = 7000.00.")
            file.close()
        else:
            extent = 7000.00
            self.logger.info("ERROR: Bad mapping input file.")
        return(extent)

    def get_map_scale(self):
        if os.path.isfile(self.inp_coord):

            line_no = 2
            file = open(self.inp_coord)
            lines = file.readlines()
            the_line = lines[line_no - 1]
            the_line = the_line.split("=")[1]  # remove line first part
            entry = the_line.split("#")[0]  # remove line end
            try:
                scale = int(entry.strip())
            except:
                scale = 2000
                self.logger.info("ERROR: Scale is not INT. Substituting to scale = 2000.")
            file.close()
        else:
            scale = 2000
            self.logger.info("ERROR: Bad mapping input file.")
        return(scale)


    def coordinates_read(self):
        points = []
        if os.path.isfile(self.inp_coord):
            file = open(self.inp_coord)
            for line in file:
                if line[0:4] == "Page":
                    the_line = line.split("[")[1]       # remove line first part
                    the_line = the_line.split("]")[0]   # remove line end
                    entries = the_line.split(",")       # separate x and y coordinate
                    try:
                        x = float(entries[0])
                        y = float(entries[1])
                        points.append([x, y])
                    except:
                        self.logger.info("ERROR: Bad assignment of x/y values in coordinate input file.")
            file.close()
        else:
            self.logger.info("ERROR: Bad coordinate input file.")
        return(points)

    def lifespan_read(self):
        lifespans = []
        line_no = 4 # .inp stores lifespans in line no. 4
        entries = self.get_line_entries(line_no)
        for entry in entries:
            try:
                __lifespan__ = float(entry.strip())
            except:
                __lifespan__ = entry.strip()
                self.logger.info("ERROR: Wrong format of lifespan list (.inp)")
            lifespans.append(__lifespan__)

        return(lifespans)

    def raster_read(self):
        raster_names = []
        entries = self.get_line_entries(self.type_dict[self.type])
        for entry in entries:
            raster_names.append(entry.strip())
        return(raster_names)


    def __call__(self):
        pass






