import os
import sys
from pipes import quote
import rrdtool
import tempfile
import commands
from datetime import datetime
import settings
from device_utils import get_device_name

# Maximum graph comment size
MAX_GRAPH_COMMENT_SIZE=170


def get_rrd_file(device, graph_plugin, graph_type):
    """
    Returns the rrd filename for a given device, plugin, type combination
    """
    device = get_device_name(device)
    return os.path.join(settings.COLLECTD_DIR, quote(device), quote(graph_plugin), quote(graph_type + ".rrd"))


def get_data_sources(filename):
    """
    Return all data sources of a rrd file
    """
    data_sources = []

    if os.path.isfile(filename):
        # rrdtool info returns dictionary with keys like ds[Total_W].type
        # parse all ds type keys
        for ds in filter(lambda x: x.startswith('ds[') and x.endswith('].type'),
                         rrdtool.info(filename.encode('ascii')).keys()):
            data_sources.append(ds.replace('ds[', '').replace('].type', ''))

    return data_sources


# def get_data_sources(filename):
#     """
#     pyrrd loads rrd info metadata horribly slow atm (~25s per file!)
#     """
#     data_sources = []
#     rrd = RRD(filename, mode="r")

#     for ds in rrd.ds:
#         data_sources.append(ds.name)

#     return data_sources


def export_rrd_data(graph_device, graph_plugin, graph_type, time_from, time_to, format='CSV'):
    """
    Export the RRD data as file in the given format (currently only CSV supported)
    """
    delimiter = ";"
    out_file = tempfile.NamedTemporaryFile('rw', suffix="." + format.lower(), dir=settings.TEMP_DIR, delete=True)
    fh = open(out_file.name, "w")
    fh.write("Device" + delimiter + "Time" + delimiter + "Value\n")

    for device in sorted(map(lambda x: get_device_name(x), graph_device.split(","))):
        export_cmd = "rrdtool fetch " + quote(get_rrd_file(device, graph_plugin, graph_type)) + \
                     " AVERAGE --start " + quote(str(time_from)) + " --end " + quote(str(time_to))
        data = commands.getoutput(export_cmd).splitlines()

        for value in data:
            try:
                t,v = str(value).split(": ")
                t = datetime.fromtimestamp(float(t)).strftime(settings.DATE_FORMAT + ":%S")
                fh.write(device + delimiter + t + delimiter + v + "\n")
            except ValueError:
                pass

    fh.close()

    return out_file
