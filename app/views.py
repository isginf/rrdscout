#
# Loading modules
#

from app import app
from device_utils import *
from misc_utils import *
from rrd_utils import *
import settings

from flask import render_template, send_file, abort, request, session
from flask.ext.babel import Babel, gettext
from werkzeug.routing import BaseConverter

import os
from pipes import quote
from time import time, mktime
from datetime import datetime
import rrdscout
from rrdscout import Graph, AGGREGATED, MULTI_LINE
from pyrrd.rrd import RRD


#
# Settings
#

# Define a URL rexexp matcher
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app.url_map.converters['regex'] = RegexConverter


# Global variables we need in all templates
@app.context_processor
def inject_settings():
    return dict(css_file=settings.CSS_FILE,
                logo_image=settings.LOGO_IMAGE,
                logo_link=settings.LOGO_LINK,
                help_link=settings.HELP_LINK,
                page_name=settings.PAGE_NAME,
                current_date=datetime.today().strftime("%d.%B %Y"))


# Custom template filters
@app.template_filter()
def hostname(value):
    return value.split('.')[0]


# I18n support
babel = Babel(app)

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(settings.LANGUAGES.keys())


#
# VIEWS
#

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    """
    List all plugins of devices defines with INDEX_TYPES and
    an aggregated summary graph for every plugin
    """

    timespan = 60
    time_to = int(time())

    if session.get('timespan'):
        timespan = int(session.get('timespan'))

    if not session.get('device_filter'):
        session['device_filter'] = "*"

    if not session.get('type_filter'):
        session['type_filter'] = settings.INDEX_TYPES

    if not session.get('reload_page'):
        session['reload_page'] = settings.RELOAD_PAGE

    if request.method == 'POST' and request.form.get('timespan'):
        session['timespan'] = request.form.get('timespan')

    if request.method == 'POST' and request.form.get('device_filter'):
        session['device_filter'] = request.form.get('device_filter')

    if request.method == 'POST' and request.form.get('type_filter'):
        session['type_filter'] = request.form.get('type_filter')

    if request.method == 'POST' and request.form.get('reload_page'):
        session['reload_page'] = bool(request.form.get('reload_page'))
    elif request.method == 'POST' and not request.form.get('reload_page'):
        session['reload_page'] = False

    devices, plugins = get_all_devices_and_plugins(session['device_filter'], session['type_filter'])

    return render_template("index.html",
                           page_name=settings.PAGE_NAME + ": " + gettext("Overview"),
                           devices = devices,
                           plugins = plugins,
                           time_from=time_to - timespan * 60,
                           time_to=time_to,
                           timespan=timespan,
                           device_filter=session['device_filter'],
                           type_filter=session['type_filter'],
                           reload_page=session['reload_page'],
                           reload_interval=settings.RELOAD_INTERVAL)



@app.route('/devices')
def devices():
    """
    List all devices
    """
    devices = os.listdir(settings.COLLECTD_DIR)

    return render_template("devices.html",
                           page_name=settings.PAGE_NAME + ": " + gettext("Devices"),
                           devices=sorted(devices))


@app.route('/datasources')
def datasources():
    """
    List all data sources (types)
    """
    devices, plugins = get_all_devices_and_plugins()
    time_from = int(time()) - 60*60
    time_to = int(time())

    return render_template("datasources.html",
                           page_name=settings.PAGE_NAME + ": " + gettext("Data sources"),
                           time_from=time_from,
                           time_to=time_to,
                           plugins=plugins)

@app.route('/device/<regex("[a-zA-Z0-9,\-\.]+"):graph_device>', methods = ['GET'])
def device(graph_device):
    """
    Show all graphs of a single device
    """
    plugins = get_plugins_for_device(graph_device)
    time_from = int(time()) - 60*60
    time_to = int(time())
    time_from_day = time_from - 60 * 60 * 24
    time_from_week = time_from - 60 * 60 * 24 * 7
    time_from_month = time_from - 60 * 60 * 24 * 30
    time_from_year = time_from - 60 * 60 * 24 * 365

    return render_template("device.html",
                           page_name=settings.PAGE_NAME + ": " + gettext("Device detail"),
                           graph_device=graph_device,
                           plugins=plugins,
                           time_from=time_from,
                           time_to=time_to,
                           time_from_day=time_from_day,
                           time_from_week=time_from_week,
                           time_from_month=time_from_month,
                           time_from_year=time_from_year)


@app.route('/export/<regex("[a-zA-Z0-9,\-\.]+"):graph_device>/<graph_plugin>/<graph_type>/<int:time_from>/<int:time_to>/<format>', methods = ['GET', 'POST'])
def export_data(graph_device, graph_plugin, graph_type, time_from, time_to, format='CSV'):
    """
    Export the graph data as CSV file
    """
    out_file = export_rrd_data(graph_device, graph_plugin, graph_type, time_from, time_to, format)

    return send_file(out_file,
                     attachment_filename=generate_attachment_name(graph_device, graph_plugin, graph_type, format.lower()),
                     as_attachment=True,
                     cache_timeout=1)



@app.route('/detail/<regex("[a-zA-Z0-9,\-\.]+"):graph_device>/<graph_plugin>/<graph_type>/<int:time_from>/<int:time_to>', methods = ['GET', 'POST'])
@app.route('/detail/<regex("[a-zA-Z0-9,\-\.]+"):graph_device>/<graph_plugin>/<graph_type>/<int:time_from>/<int:time_to>/<regex("(multi-line)|(aggregated)"):graph_mode>', methods = ['GET', 'POST'])
def detail(graph_device, graph_plugin, graph_type, time_from, time_to, graph_mode="aggregated", cdefop=None):
    """
    Show the details of a single graph
    """

    device_map = device_index()
    graph_title = []
    graph_comment = ""

    # Got datetime values from post? Convert them
    if request.method == 'POST' and request.form.get('time_from'):
        time_from = int(mktime(datetime.strptime(request.form['time_from'], settings.DATE_FORMAT).timetuple()))

    if request.method == 'POST' and request.form.get('time_to'):
        time_to = int(mktime(datetime.strptime(request.form['time_to'], settings.DATE_FORMAT).timetuple()))

    # User defined graph comment
    if request.method == 'POST' and request.form.get('comment'):
        graph_comment = request.form['comment']
    else:
        graph_comment = rrdscout.Graph.generate_comment(graph_device.split(','))

    # Shall we export the graph data instead of generating an image?
    if request.method == 'POST' and request.form.get('export_graph'):
        return export_data(graph_device, graph_plugin, graph_type, time_from, time_to)

    # if device is a number its an index to the ctime sorted device directory
    try:
        graph_title.append(device_map.get(int(graph_device), ""))
    except ValueError:
        pass

    # if device is a list
    if not graph_title:
        try:
            graph_title = sorted( map(lambda x: device_map.get(int(x), x), graph_device.split(',')) )
        except ValueError:
            pass

    # Still no label?
    if not graph_title:
        graph_title = [graph_device]

    # calculate timespans
    time_from_day = int(time()) - 60 * 60 * 24
    time_from_week = int(time()) - 60 * 60 * 24 * 7
    time_from_month = int(time()) - 60 * 60 * 24 * 30
    time_from_year = int(time()) - 60 * 60 * 24 * 365

    return render_template("detail.html",
                           page_name=settings.PAGE_NAME + ": " + gettext("Data source detail"),
                           graph_title=graph_title,
                           graph_device=graph_device,
                           graph_plugin=graph_plugin,
                           graph_type=graph_type,
                           graph_comment=graph_comment,
                           graph_mode=graph_mode,
                           time_from=time_from,
                           time_to=time_to,
                           time_to_str=datetime.fromtimestamp(time_to).strftime(settings.DATE_FORMAT),
                           time_from_str=datetime.fromtimestamp(time_from).strftime(settings.DATE_FORMAT),
                           time_from_day=time_from_day,
                           time_from_week=time_from_week,
                           time_from_month=time_from_month,
                           time_from_year=time_from_year)



@app.route('/graph/<regex("[a-zA-Z0-9,\-\.]+"):graph_devices>/<graph_plugin>/<graph_type>/<int:time_from>/<int:time_to>', methods = ['GET'])
@app.route('/graph/<regex("[a-zA-Z0-9,\-\.]+"):graph_devices>/<graph_plugin>/<graph_type>/<int:time_from>/<int:time_to>/<graph_comment>', methods = ['GET'])
@app.route('/graph/<regex("[a-zA-Z0-9,\-\.]+"):graph_devices>/<graph_plugin>/<graph_type>/<int:time_from>/<int:time_to>/<regex("(multi-line)|(aggregated)"):graph_mode>', methods = ['GET'])
@app.route('/graph/<regex("[a-zA-Z0-9,\-\.]+"):graph_devices>/<graph_plugin>/<graph_type>/<int:time_from>/<int:time_to>/<regex("(multi-line)|(aggregated)"):graph_mode>/<graph_comment>', methods = ['GET'])
def graph(graph_devices, graph_plugin, graph_type, time_from, time_to, graph_comment=None, cdefop=None, graph_width=settings.GRAPH_WIDTH, graph_height=settings.GRAPH_HEIGHT, comment=True, graph_mode="aggregated"):
    """
    Create a graph for a specified device, plugin and type on a specified timespan
    Returns an image per HTTP
    """

    devices = sorted(map(lambda x: get_device_name(x), graph_devices.split(",")))

    if not comment:
        graph_comment = None

    if graph_mode == "aggregated":
        graph_mode = AGGREGATED
    else:
        graph_mode = MULTI_LINE

    graph = Graph(devices=devices,
                  plugin=graph_plugin,
                  data_source=graph_type,
                  time_from=time_from,
                  time_to=time_to,
                  comment = graph_comment,
                  add_comment = comment,
                  width = graph_width,
                  height = graph_height,
                  mode = graph_mode)
    graph.generate_graph()

    if graph.generation_failed():
        abort(404)

    return send_file(graph.out_file,
                     attachment_filename=graph.attachment_name,
                     as_attachment=True,
                     cache_timeout=1)


@app.route('/graphthumb/<regex("[a-zA-Z0-9,\-\.]+"):graph_devices>/<graph_plugin>/<graph_type>/<int:time_from>/<int:time_to>', methods = ['GET'])
@app.route('/graphthumb/<regex("[a-zA-Z0-9,\-\.]+"):graph_devices>/<graph_plugin>/<graph_type>/<int:time_from>/<int:time_to>/<regex("(multi-line)|(aggregated)"):graph_mode>', methods = ['GET'])
def graphthumb(graph_devices, graph_plugin, graph_type, time_from, time_to, graph_mode="aggregated", cdefop=None):
    """
    Return a thumbnailed graph image per HTTP
    """
    return graph(graph_devices, graph_plugin, graph_type, time_from, time_to,
                 cdefop=cdefop,
                 graph_width=settings.GRAPH_THUMB_WIDTH,
                 graph_height=settings.GRAPH_THUMB_HEIGHT,
                 graph_mode=graph_mode,
                 comment=False)


@app.route('/disclaimer', methods=['GET'])
def disclaimer():
    return render_template('disclaimer.html',
                           page_name=settings.PAGE_NAME + ": " + gettext("Disclaimer"))
