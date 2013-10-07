import os

# Where to find all collectd rrd files?
COLLECTD_DIR=os.path.join(os.getcwd(), "rrd")

# Where should temporary graph files be stored?
TEMP_DIR='/tmp'

# Supported languages
LANGUAGES = {
        'en': 'English',
        'de': 'German',
        'it': 'Italian',
        'fr': 'French',
}

# The name of our page
PAGE_NAME="Data Center Observatory"

# Width / heights of normal and thumbnail graph
GRAPH_WIDTH=1172
GRAPH_HEIGHT=355
GRAPH_THUMB_WIDTH=300
GRAPH_THUMB_HEIGHT=150

# Colors of graph area and lines
COLOR_AREA_MIN="#FFFFFF"
COLOR_AREA_MAX="#f4bf9c"
COLOR_LINES = ['#ff8442',
               '#bb8442',
               '#888442',
               '#448442',
               '#008442',
               '#004442',
               '#000042',
               '#000000']

# Logo link and image
LOGO_LINK = "/"
LOGO_IMAGE = "rrdscout_logo.png"

# Link to help site
HELP_LINK = "https://wiki.dco.ethz.ch"

# CSS filename
CSS_FILE="style.css"

# Unit filter for index page
# Can be combined with |
# e.g. *_total|temp_* to see all units ending with _total and staring with temp_
INDEX_TYPES='*_total|temp_*'

# Automatically reload index page in a certain interval?
RELOAD_PAGE=False
RELOAD_INTERVAL=60

# Date format used in detail graph view
DATE_FORMAT="%Y-%m-%d %H:%M"

# Automatically convert some data sources
CALC_OPERATION = {
    'celsius': '$VALUE,10,/,273.15,-,$QUANTITY,/',
    'kilowatt': '$VALUE,1000,/',
}
DATA_SOURCE_CONVERT = {
    'C': 'celsius',
    'kWh': 'kilowatt',
    'Total_kWh': 'kilowatt',
}

# Automatically label some units
# do not use white spaces
GRAPH_LABEL={
    'Total_W': 'W',
    'Total_mA': 'mA',
    'Total_kWh': 'kWh',
    'Total_PF': 'Power_Factor',
    'Total_VA': 'VA',
    'PF': 'Power Factor',
}

# Which units shall not have a summary table?
DATA_SOURCES_WITHOUT_SUMMARY = ['kWh', 'Total_kWh']


# Global translation of data sources
DATA_SOURCE_TRANSLATION = { 'kwh-0': 'kWh Port 1',
                            'kwh-1': 'kWh Port 2',
                            'kwh-2': 'kWh Port 3',
                            'kwh-3': 'kWh Port 4',
                            'kwh-4': 'kWh Port 5',
                            'kwh-5': 'kWh Port 6',
                            'kwh-6': 'kWh Port 7',
                            'kwh-7': 'kWh Port 8',
                            'kwh_total': 'kWh total',
                            'milliampere-0': 'milliampere Port 1',
                            'milliampere-1': 'milliampere Port 2',
                            'milliampere-2': 'milliampere Port 3',
                            'milliampere-3': 'milliampere Port 4',
                            'milliampere-4': 'milliampere Port 5',
                            'milliampere-5': 'milliampere Port 6',
                            'milliampere-6': 'milliampere Port 7',
                            'milliampere-7': 'milliampere Port 8',
                            'milliampere_total': 'Milliampere total',
                            'pf-0': 'Power Factor Port 1',
                            'pf-1': 'Power Factor Port 2',
                            'pf-2': 'Power Factor Port 3',
                            'pf-3': 'Power Factor Port 4',
                            'pf-4': 'Power Factor Port 5',
                            'pf-5': 'Power Factor Port 6',
                            'pf-6': 'Power Factor Port 7',
                            'pf-7': 'Power Factor Port 8',
                            'pf_total': 'Power Factor total',
                            'watt-0': 'Watt Port 1',
                            'watt-1': 'Watt Port 2',
                            'watt-2': 'Watt Port 3',
                            'watt-3': 'Watt Port 4',
                            'watt-4': 'Watt Port 5',
                            'watt-5': 'Watt Port 6',
                            'watt-6': 'Watt Port 7',
                            'watt-7': 'Watt Port 8',
                            'watt_total': 'Watt total',
                            'temp_a1_sensor_left': 'Temperature probe left',
                            'temp_a1_sensor_right': 'Temperature probe right',
                            'temp_a2_sensor_left': 'Temperature probe left',
                            'temp_a2_sensor_right': 'Temperature probe right',
                            'temp_a1_internal': 'Internal temperature probe 1',
                            'temp_a2_internal': 'Internal temperature probe 2',
}

# Per device translation  ovverrides settings from GLOBAL_TYPES_TRANSLATION
DEVICE_TRANSLATION = {'localhost': {'milliampere-0': 'test translation of data sources at a specific device'}
                      }
