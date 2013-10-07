import os
import glob
import settings

def device_index(reverse=False):
    """
    Get a dictionary of index nr to device map sorted by creation time
    """
    device_index = {}
    devices = []

    # Get a list of full path names
    for device_dir in os.listdir(settings.COLLECTD_DIR):
        devices.append(os.path.join(settings.COLLECTD_DIR, device_dir))

    # Sort it by creation time
    devices.sort(key=lambda x: os.path.getctime(x))

    # Generate index dict
    if reverse:
        for (i, device) in enumerate(devices):
            device_index[os.path.basename(device)] = i
    else:
        for (i, device) in enumerate(devices):
            device_index[i] = os.path.basename(device)

    return device_index


def get_index_for_device(device):
    """
    Find the index number to a device
    """
    return device_index(True).get(device, -1)


def get_device_name(device):
    """
    if device is an index lookup the device name
    """
    device_map = device_index()

    try:
        int(device)
        device = device_map.get(int(device), "")
    except ValueError:
        pass

    return device


def get_all_devices_and_plugins(device_filter="", type_filter="*"):
    """
    Returns a list of all devices and their plugins and the types of every plugin as well as
    a dictionary of all plugins and their types and a list of devices supporting this plugin / type combination
    Parameter: Optional device and type glob filter
    """
    devices = []
    plugins = {}
    device_filter = device_filter.replace("*", "")
    devices_index = device_index()

    for device_number in devices_index:
        device = {}

        device['index'] = device_number
        device['name'] = devices_index[device_number]

        if device_filter in device['name']:
            device['plugins'] = []

            device_dir = os.path.join(settings.COLLECTD_DIR, device['name'])

            for plugin_dir in os.listdir(device_dir):
                plugin = {}
                plugin['name'] = plugin_dir
                plugin['types'] = []

                # type filter can be concatenated with |
                # find all defined type (rrd) files
                for type_pattern in type_filter.split("|"):
                    for type_filename in glob.glob(os.path.join(device_dir, plugin_dir, type_pattern + ".rrd")):
                        type_name = os.path.basename(type_filename).replace('.rrd', '')
                        plugins.setdefault(plugin_dir, {})[type_name] = ""
                        plugin['types'].append(type_name)

                if plugin['types']:
                    device['plugins'].append(plugin)

            if device['plugins']:
                devices.append(device)

    for (plugin, types) in plugins.items():
        for type_name in types.keys():
            for device_filename in glob.glob(os.path.join(settings.COLLECTD_DIR, '*', plugin, type_name + ".rrd")):
                # parse device name
                # /var/lib/collectd/rrd/dco-pdu013-mgt.dco.ethz.ch/snmp/kwh_total.rrd
                device = device_filename.replace(settings.COLLECTD_DIR, '').replace(plugin, '').replace(type_name + ".rrd", '')[1:-2]
                plugins[plugin][type_name] += str(get_index_for_device(device)) + ","
            plugins[plugin][type_name] = plugins[plugin][type_name].rstrip(',')

    return sorted(devices, key=lambda k: k['name']), plugins


def get_plugins_for_device(device, glob_filter='*'):
    """
    Get a list of dictionary of all plugins of a devices and their types
    List can be optionally filtered by a glob filter
    """
    plugins = []
    device = get_device_name(device)
    device_dir = os.path.join(settings.COLLECTD_DIR, device)

    for plugin_dir in os.listdir(device_dir):
        plugin = {}
        plugin['name'] = plugin_dir
        plugin['types'] = []

        for type_filename in glob.glob(os.path.join(device_dir, plugin_dir, glob_filter)):
            type_name = os.path.basename(type_filename).replace('.rrd', '')
            plugin['types'].append(type_name)

        plugin['types'].sort()
        plugins.append(plugin)

    return plugins
