from device_utils import *
from rrd_utils import *
from misc_utils import *
from time import time
from pyrrd.graph import DEF, CDEF, ColorAttributes, LINE, AREA, GPRINT, VariableDefinition, GraphComment
from pyrrd.graph import Graph as PyrrdGraph
from flask.ext.babel import gettext
import tempfile
import settings
from pipes import quote
import os

# Mask magic numbers
AGGREGATED=1
MULTI_LINE=2

# Maximum graph comment size
MAX_GRAPH_COMMENT_SIZE=170


class Graph(object):
    def __init__(self, devices, plugin, data_source,
                 time_from=time()-60*60, time_to=time(),
                 width=settings.GRAPH_WIDTH, height=settings.GRAPH_HEIGHT,
                 mode=AGGREGATED, comment="", add_comment=True):
        """
        Constructor.
        Needed parameters: list of devices, plugin name, data source name
        Optional parameters: time_from and time_to (default before 1 hour till now),
        width and height of graph in pixel, mode aggregated or multi-line, comment

        To set multi-line graph use mode=rrdscout.MULTI_LINE
        """
        self.devices = devices
        self.plugin = plugin
        self.data_source = data_source
        self.time_from = time_from
        self.time_to = time_to
        self.width = width
        self.height = height
        self.mode = mode
        self.title = ""
        self.y_label = ""
        self.attachment_name = ""
        self.comment = comment
        self.add_comment = add_comment
        self.out_file = tempfile.NamedTemporaryFile('rw', suffix='.png', dir=settings.TEMP_DIR, delete=True)

        self._defs = []
        self._cdefs = []
        self._def_map = {}
        self._cdef_map = {}
        self._cdef_values = {}
        self._metadata = {}
        self._lines = []
        self._areas = {}
        self._vdefs = []
        self._gprints = []
        self._got_errors = False
        self._cf_map = {'min': 'MINIMUM',
                       'max': 'MAXIMUM',
                       'average': 'AVERAGE'}

        graph_color = ColorAttributes()
        graph_color.back = '#ffffff'
        graph_color.shadea = '#ffffff'
        graph_color.shadeb = '#ffffff'

        self.graph = PyrrdGraph(self.out_file.name,
                                start=self.time_from,
                                end=self.time_to,
                                width=self.width,
                                height=self.height,
                                color=graph_color)

    def _generate_defs(self):
        """
        FOR INTERNAL USE ONLY

        This generates an RRD DEF objects for every data source in every device (rrd file)
        and saves them in the list self._defs.
        Additionally it generates a dictionary def_map with key is DEF name and value is a
        lookup key for metadata

        Saves meta information for DEFs and CDEFs like device, data source and cf in metadata
        """
        def_count = 0
        self._defs = []
        self._def_map = {}

        for device in self.devices:
            rrd_file = get_rrd_file(device, self.plugin, self.data_source)

            if os.path.isfile(rrd_file):
                # Get all data sources from rrd
                for data_source in get_data_sources(rrd_file):
                    for cf in self._cf_map.keys():
                        metadata_key = cf + str(def_count)

                        # generate definition
                        def_vname = 'def_%s_%s_%s' % (data_source, cf, str(def_count))
                        self._def_map[def_vname] = metadata_key

                        self._metadata.setdefault(metadata_key, {})
                        self._metadata[metadata_key]['data_source'] = data_source
                        self._metadata[metadata_key]['device'] = device
                        self._metadata[metadata_key]['cf'] = cf

                        self._defs.append( DEF(rrdfile=rrd_file,
                                              dsName=data_source,
                                              cdef=cf.upper(),
                                              vname=def_vname) )
                    def_count += 1


    def _generate_cdefs(self):
        """
        FOR INTERNAL USE ONLY

        This generates an RRD CDEF object for every DEF object and saves them in the list self._cdefs.
        Additionally it generates a dictionary cdef_map with key is CDEF name and value is a
        lookup key for metadata

        metadata saves meta information for DEFs and CDEFs like device, data source and cf
        This function adds a vnames lookup which includes all DEF objects that should be calculated
        to build the CDEF
        """
        def_count = 0
        self._cdefs = []
        self._cdef_map = {}
        self._cdef_values = {}

        # generate cdef map
        # for every data_source keep a list of definitions to calculate
        for (def_vname, metadata_key) in self._def_map.items():
            if self.mode == MULTI_LINE:
                cdef_vname = 'cdef_%s_%s_%s' % (self._metadata[metadata_key]['data_source'],
                                                self._metadata[metadata_key]['cf'],
                                                def_count)
                def_count += 1
            else:
                cdef_vname = 'cdef_%s_%s' % (self._metadata[metadata_key]['data_source'],
                                                self._metadata[metadata_key]['cf'])

            self._cdef_map[cdef_vname] = metadata_key
            self._cdef_values.setdefault(cdef_vname, []).append(def_vname)


        def_count = 0

        # Iterate over all cdefs and either generate a rpn to aggregate all defs in values or if mode is multi-line
        # generate a rpn for every single def
        for (cdef_vname, metadata_key) in self._cdef_map.items():
            cdef_opts = self._metadata[metadata_key]

            if self.mode == MULTI_LINE:
                for vname in self._cdef_values[cdef_vname]:
                    cdef = CDEF(vname=cdef_vname + "_" + str(def_count),
                                rpn=self._generate_rpn(cdef_opts['data_source'], vname))

                    self._metadata[metadata_key].setdefault('cdef_objs', []).append(cdef)
                    self._cdefs.append(cdef)

                    def_count += 1
            else:
                cdef = CDEF(vname=cdef_vname + "_" + str(def_count),
                            rpn=self._generate_rpn(cdef_opts['data_source'], self._cdef_values[cdef_vname]))

                self._metadata[metadata_key].setdefault('cdef_objs', []).append(cdef)
                self._cdefs.append(cdef)

                def_count += 1


    def _generate_lines(self):
        """
        FOR INTERNAL USE ONLY

        This generates an RRD LINE object to graph for every CDEF object with the CF average
        and saves them in the list self._lines.
        """
        color_count = 0
        self._lines = []

        for (cdef_vname, metadata_key) in self._cdef_map.items():
            cdef_opts = self._metadata[metadata_key]

            # Draw only average value as line
            if cdef_opts['cf'] == "average":
                for cdef_obj in cdef_opts['cdef_objs']:
                    if color_count >= len(settings.COLOR_LINES):
                        color_count = 0

                    line_color = settings.COLOR_LINES[color_count]
                    color_count += 1

                    if self.mode == MULTI_LINE:
                        self._lines.append(LINE(defObj=cdef_obj,
                                                color=line_color,
                                                legend=cdef_opts['device'] + " - " + str(color_count)))
                    else:
                        self._lines.append(LINE(defObj=cdef_obj,
                                                color=line_color))


    def _generate_areas(self):
        """
        FOR INTERNAL USE ONLY

        This generates an RRD AREA object for every CDEF object with the CF min or max
        and saves them in the list self._areas.
        Only useful in aggregated (single line) graphs
        """
        self._areas = {}

        for (cdef_vname, metadata_key) in self._cdef_map.items():
            cdef_opts = self._metadata[metadata_key]

            if cdef_opts['cf'] == "max":
                self._areas.setdefault('max', []).append(AREA(defObj=cdef_opts['cdef_objs'][0],
                                                        color=settings.COLOR_AREA_MAX))

            elif cdef_opts['cf'] == "min":
                self._areas.setdefault('min', []).append(AREA(defObj=cdef_opts['cdef_objs'][0],
                                                        color=settings.COLOR_AREA_MIN))


    def _generate_table(self):
        """
        FOR INTERNAL USE ONLY

        This generates an RRD VDEF and GPRINT object for every CDEF object
        and saves them in the list self._vdefs and self._gprints.
        """
        def_count = 0
        self._vdefs = []
        self._gprints = []

        for (cdef_vname, metadata_key) in self._cdef_map.items():
            cdef_opts = self._metadata[metadata_key]

            if cdef_opts['cf'] == "average":
                vdef = VariableDefinition(vname="vdef_" + str(def_count),
                                          rpn="%s,%s" % (cdef_vname + "_" + str(def_count), "AVERAGE"))
                gprint_label = gettext("Avg")

                vdef_last = VariableDefinition(vname="vdef_last_" + str(def_count),
                                               rpn="%s,%s" % (cdef_vname + "_" + str(def_count), "LAST"))
                self._vdefs.append(vdef_last)

                if cdef_opts['data_source'] not in settings.DATA_SOURCES_WITHOUT_SUMMARY:
                    self._gprints.append(GPRINT(vdef_last, 'Last %0.1lf'))

            # Draw min and max as area
            if cdef_opts['cf'] == "max":
                vdef = VariableDefinition(vname="vdef_" + str(def_count),
                                          rpn="%s,%s" % (cdef_vname + "_" + str(def_count), "MAXIMUM"))
                gprint_label = gettext("Max")

            elif cdef_opts['cf'] == "min":
                vdef = VariableDefinition(vname="vdef_" + str(def_count),
                                          rpn="%s,%s" % (cdef_vname + "_" + str(def_count), "MINIMUM"))
                gprint_label = gettext("Min")

            # create table
            if vdef and cdef_opts['data_source'] not in settings.DATA_SOURCES_WITHOUT_SUMMARY:
                self._vdefs.append(vdef)
                self._gprints.append(GPRINT(vdef, gprint_label + ' %0.1lf'))

            def_count += 1



    def _generate_rpn(self, data_source, vnames):
        """
        FOR INTERNAL USE ONLY

        Generate calculation for given data source
        Look into the setting if we should automatically recalculate this data_source
        We add 0 if we cannot find any way to recalculate
        """
        if type(vnames) == str:
            vnames = [vnames]

        # if no cdefop is given we just add 0
        default_cdef = '$VALUE,0,+'

        rpn = settings.CALC_OPERATION.get(settings.DATA_SOURCE_CONVERT.get(data_source))
        summands = []

        if not rpn:
            rpn = default_cdef

        for def_vname in vnames:
            rpn = rpn.replace('$VALUE', def_vname)
            rpn = rpn.replace('$QUANTITY', str(len(vnames)))
            summands.append(rpn)

        if len(vnames) == 1:
            rpn = summands[0]
        else:
            rpn = ",".join(summands)

            # postfix operation for each pair of summands
            for i in range(1, len(vnames)):
                rpn += ",+"

        return rpn


    def _generate_title(self):
        """
        FOR INTERNAL USE ONLY

        Generate the graph title
        Look into settings if we should automatically translate the data source name
        Make sure there are no spaces
        """
        if len(self.devices) == 1:
            self.title = translate(self.data_source, self.devices[0]).replace(' ', '_')
        else:
            self.title = translate(self.data_source).replace(' ', '_')


    def _generate_y_axis_label(self):
        """
        FOR INTERNAL USE ONLY

        Generate the label for the graph
        """
        self.y_label = ""

        for device in self.devices:
            device = get_device_name(device)
            rrd_file = get_rrd_file(device, self.plugin, self.data_source)

            if os.path.isfile(rrd_file):
                # Get all data sources from rrd
                for data_source in get_data_sources(rrd_file):
                    self.y_label = "".join(Graph.get_label_for_data_source(data_source))

        self.y_label = self.y_label.replace(' ','_')


    @staticmethod
    def get_label_for_data_source(data_source):
        """
        Return the converted data source name or the data source name
        if we cannot find a conversion
        """
        return settings.GRAPH_LABEL.get(data_source, data_source)


    @staticmethod
    def generate_comment(label_input):
        """
        Generate a comment for graph from device list or just make sure that
        a comment doesnt overflow and have unwanted chars
        """
        graph_comment = ""

        if type(label_input) == list:
            graph_comment = ','.join([get_device_name(x).split('.')[0] for x in label_input])
        elif type(label_input) == str or type(label_input) == unicode:
            graph_comment = label_input.lstrip("'").rstrip("'")
        else:
            try:
                graph_comment = str(label_input)
            except ValueError:
                pass

        if len(graph_comment) > MAX_GRAPH_COMMENT_SIZE:
            graph_comment = graph_comment[0:MAX_GRAPH_COMMENT_SIZE] + "..."
#        elif len(graph_comment) < MAX_GRAPH_COMMENT_SIZE:
#            graph_comment = graph_comment + " " * int(MAX_GRAPH_COMMENT_SIZE) - len(graph_comment)

        graph_comment = graph_comment.replace("\"", "").replace("'", "")

        return graph_comment.encode("ascii", "ignore")


    def generate_attachment_name(self, suffix="png"):
        """
        Generate the attachment file name for the graph for the given suffix
        Default suffix is png
        """
        self.attachment_name = ""

        if len(self.devices) == 1:
            self.attachment_name = quote(self.devices[0].replace('.', '_')) + "_" + quote(self.plugin) + \
                                                "_" + quote(self.data_source + "." + suffix)
        else:
            self.attachment_name = quote(self.plugin) + "_" + quote(self.data_source + "." + suffix)



    def generate_graph(self):
        """
        Generate all needed RRD objects like DEFs, CDEFs, LINES etc and stuff them together to
        create a graph

        You can use failed() to check if we got errors otherwise graph will be in out_file
        """
        self._generate_defs()
        self._generate_cdefs()
        self._generate_lines()
        self._generate_title()
        self._generate_y_axis_label()
        self.generate_attachment_name()

        self.graph.title = self.title

        # Add vertical axes label
        self.graph.vertical_label = self._generate_y_axis_label()

        # Add all data to the graph
        self.graph.data = []
        self.graph.data.extend(self._defs)
        self.graph.data.extend(self._cdefs)

        # min must be after max to overpaint max color in area
        if self.mode == AGGREGATED:
            self._generate_areas()
            self.graph.data.extend(self._areas['max'])
            self.graph.data.extend(self._areas['min'])

        self.graph.data.extend(sorted(self._lines, key=lambda x: x.legend))

        # Add a graph comment
        if self.add_comment:
            if self.comment:
                graph_comment = self.generate_comment(self.comment)
            else:
                graph_comment = self.generate_comment(self.devices)

            self.graph.data.append(GraphComment(graph_comment, autoNewline=False))

        # Add table
        if self.mode == AGGREGATED:
            self._generate_table()
            self.graph.data.extend(self._vdefs)
            self.graph.data.extend(sorted(self._gprints, key=lambda x: x.format))

        try:
            self.graph.write()
        except Exception:
            self.__got_error = True


    def generation_failed(self):
        """
        Returns true if generation failed
        """
        if len(self._defs) == 0 or self._got_errors:
            return True
        else:
            return False
