import unittest
from nose.tools import timed
import pyrrd
import os
import sys

sys.path.insert(0, "../test")
sys.path.append("../app")
sys.path.append("../")

import rrdscout
from rrdscout import Graph, MULTI_LINE

def not_on_travis(decorator):
  def wrapper(func):
    if os.getenv("TRAVIS"):
      return func
    else:
      return decorator(func)
  return wrapper


class GraphTest(unittest.TestCase):
    def setUp(self):
        self.devices = ["localhost"]
        self.plugin = "snmp"
        self.data_source = "milliampere-0"
        self.time_from = 1380802176
        self.time_to = 1380842640
        self.width = 200
        self.height = 100
        self.graph = Graph(devices=self.devices,
                           plugin=self.plugin,
                           data_source=self.data_source,
                           time_from=self.time_from,
                           time_to=self.time_to,
                           width=self.width,
                           height=self.height)


    def test_init(self):
        self.assertTrue(self.graph)
        self.assertEqual(self.graph.devices, self.devices)
        self.assertEqual(self.graph.plugin, self.plugin)
        self.assertEqual(self.graph.data_source, self.data_source)
        self.assertEqual(self.graph.time_from, self.time_from)
        self.assertEqual(self.graph.time_to, self.time_to)
        self.assertEqual(self.graph.width, self.width)
        self.assertEqual(self.graph.height, self.height)
        self.assertEqual(str(self.graph.out_file.__class__), "tempfile._TemporaryFileWrapper")


    def test_generate_defs(self):
        self.graph._generate_defs()
        self.assertTrue(self.graph._defs)
        self.assertTrue(self.graph._def_map)
        self.assertTrue(self.graph._metadata)
        self.assertEqual(type(self.graph._metadata['max0']), dict, "metadata has key max0 with value dict of metadata")
        self.assertEqual(self.graph._def_map['def_mA_average_0'], "average0")

    def test_generate_defs_fails_with_unknown_host(self):
        self.graph.devices[0] = "unfug"
        self.graph._generate_defs()
        self.assertFalse(self.graph._defs)


    def test_generate_cdefs(self):
        self.graph._generate_defs()
        self.graph._generate_cdefs()
        self.assertTrue(self.graph._cdef_map)
        self.assertTrue(self.graph._cdefs)
        self.assertEqual(type(self.graph._cdefs[0]), pyrrd.graph.CalculationDefinition, "cdefs stores CalculationDefinition objects")
        self.assertEqual(self.graph._cdef_values['cdef_mA_max'][0], "def_mA_max_0", "cdef_values stores def names to calculate to get cdef")
        self.assertEqual(self.graph._cdef_map['cdef_mA_max'], "max0", "cdef_map stores metadata keys")

        self.graph.mode = MULTI_LINE
        self.graph._generate_cdefs()
        self.assertEqual(self.graph._cdef_values['cdef_mA_max_0'][0], "def_mA_max_0", "cdef_values stores def names to calculate to get cdef")
        self.assertEqual(self.graph._cdef_map['cdef_mA_max_0'], "max0", "cdef_map stores metadata keys")

    def test_generate_cdefs_fails_without_defs(self):
        self.graph._generate_cdefs()
        self.assertFalse(self.graph._cdef_map)
        self.assertFalse(self.graph._cdefs)

    def test_generate_lines(self):
        self.graph._generate_defs()
        self.graph._generate_cdefs()
        self.graph._generate_lines()
        self.assertEqual(len(self.graph._lines), 1)
        self.assertEqual(type(self.graph._lines[0]),pyrrd.graph.Line, "lines stores Line objects")

    def test_generate_multi_lines(self):
        self.graph.mode = MULTI_LINE
        self.graph.devices.append('testhost')

        self.graph._generate_defs()
        self.graph._generate_cdefs()
        self.graph._generate_lines()
        print self.graph._lines
        self.assertEqual(len(self.graph._lines), 2)

    def test_generate_lines_fails_without_defs_and_cdefs(self):
        self.graph._generate_lines()
        self.assertFalse(self.graph._lines)

    def test_generate_areas(self):
        self.graph._generate_defs()
        self.graph._generate_cdefs()
        self.graph._generate_areas()
        self.assertEqual(len(self.graph._areas), 2)
        self.assertEqual(type(self.graph._areas['min'][0]),pyrrd.graph.Area, "areas stores Area objects")

    def test_generate_areas_fails_without_defs_and_cdefs(self):
        self.graph._generate_areas()
        self.assertFalse(self.graph._areas)

    def test_generate_table(self):
        self.graph._generate_defs()
        self.graph._generate_cdefs()
        self.graph._generate_table()
        self.assertEqual(type(self.graph._vdefs[0]), pyrrd.graph.VariableDefinition, "vdefs stores VariableDefinition objects")
        self.assertEqual(type(self.graph._gprints[0]), pyrrd.graph.GraphPrint, "gprints stores gprint objects")

    def test_generate_table_fails_without_defs_and_cdefs(self):
        self.graph._generate_table()
        self.assertFalse(self.graph._vdefs)
        self.assertFalse(self.graph._gprints)

    def test_generate_rpn(self):
        self.assertEqual(self.graph._generate_rpn("C", "test_def"), "test_def,10,/,273.15,-,1,/", "automatically convert C data sources")
        self.assertEqual(self.graph._generate_rpn("unfug", "test_def"), "test_def,0,+", "dont convert unknown data source")

    def test_generate_title(self):
        self.graph._generate_title()
        self.assertEqual(self.graph.title, "test_translation_of_data_sources_at_a_specific_device")

        self.graph.devices = ["localhost, testhost"]
        self.graph._generate_title()
        self.assertEqual(self.graph.title, "milliampere_Port_1", "title for more than one device")

    def test_generate_Y_Axis_Label(self):
        self.graph._generate_y_axis_label()
        self.assertEqual(self.graph.y_label, "mA", "y label is mA")

    def test_get_label_for_data_source(self):
        self.assertEqual(rrdscout.Graph.get_label_for_data_source("Total_W"), "W", "test with Total_W")
        self.assertEqual(rrdscout.Graph.get_label_for_data_source(""), "")
        self.assertEqual(rrdscout.Graph.get_label_for_data_source("ETHZ"), "ETHZ", "unconvertable input")


    def test_generate_comment(self):
        self.assertEqual(rrdscout.Graph.generate_comment(self.graph.devices), "localhost")
        self.assertEqual(rrdscout.Graph.generate_comment("test me"), "test me")

    def test_generate_attachment_name(self):
        self.graph.generate_attachment_name("jpg")
        self.assertEqual(self.graph.attachment_name, "localhost_snmp_milliampere-0.jpg")

        self.graph.devices = ["localhost", "testhost"]
        self.graph.generate_attachment_name()
        self.assertEqual(self.graph.attachment_name, "snmp_milliampere-0.png")

    @not_on_travis(timed(0.1))
    def test_generate_graph(self):
        self.graph.generate_graph()
        self.assertFalse(self.graph.generation_failed())

    @not_on_travis(timed(0.1))
    def test_generate_multi_line_graph(self):
        self.graph.devices = ["localhost", "testhost"]
        self.graph.mode = MULTI_LINE
        self.graph.generate_graph()
        self.assertFalse(self.graph.generation_failed())

    @not_on_travis(timed(0.1))
    def test_generate_aggregated_graph(self):
        self.graph.devices = ["localhost", "testhost"]
        self.graph.generate_graph()
        self.assertFalse(self.graph.generation_failed())
