import unittest
import os
import sys
sys.path.append("../app")
os.putenv("LANG", "C")

from rrd_utils import *

class UtilsTest(unittest.TestCase):
    def setUp(self):
        self.device = "localhost"
        self.plugin = "snmp"
        self.data_source = "milliampere-0"
        self.time_from = 1380802176
        self.time_to = 1380842640

    def test_get_rdd_file(self):
        self.assertEqual(get_rrd_file(self.device, self.plugin, self.data_source),
                         os.path.join(os.getcwd(), "rrd", self.device, self.plugin, self.data_source + ".rrd"))

    def test_get_data_sources(self):
        ds = get_data_sources(os.path.join(os.getcwd(), "rrd", self.device, self.plugin, self.data_source + ".rrd"))
        self.assertEqual(ds[0], "mA", "get_data_sources returns a list")

    def test_export_rrd_data(self):
        csv = export_rrd_data(self.device, self.plugin, self.data_source, self.time_from, self.time_to)
        data = csv.read().splitlines()
        self.assertEqual("Device;Time;Value", data[0])
        self.assertEqual("localhost;2013-10-03 14:10:48;8.9440277778e+02", data[1])
