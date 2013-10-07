# Where to find all collectd rrd files?
COLLECTD_DIR="/var/lib/collectd/rrd"

# Where should temporary graph files be stored?
TEMP_DIR='/tmp'

# Supported languages
LANGUAGES = {
        'en': 'English',
        'de': 'German',
}

# The name of our page
PAGE_NAME="My page name"

# Width / heights of normal and thumbnail graph
GRAPH_WIDTH=1172
GRAPH_HEIGHT=355
GRAPH_THUMB_WIDTH=300
GRAPH_THUMB_HEIGHT=150

# Colors of graph area and lines
COLOR_AREA_MIN="#FFFFFF"
COLOR_AREA_MAX="#f4bf9c"
COLOR_LINES = [ '#ff8442', '#800000', '#008B8B', '#DEB887', '#5F9EA0', '#D2691E',
                '#FF7F50', '#6495ED', '#DC143C', '#0000FF', '#9ACD32', '#EE82EE',
                '#A9A9A9', '#006400', '#BDB76B', '#8B008B', '#556B2F', '#FF8C00',
                '#9932CC', '#8B0000', '#E9967A', '#8DBC8F', '#483D8B', '#2F4F4F',
                '#00DED1', '#9400D3', '#FF1493', '#00BFFF', '#696969', '#1E90FF',
                '#B22222', '#000000', '#228B22', '#FF00FF', '#DCDCDC', '#F8F8FF',
                '#FFD700', '#DAA520', '#808080', '#008000', '#ADFF2F', '#B8860B',
                '#FF69B4', '#CD5C5C', '#4B0082', '#FFFFF0', '#F0E68C', '#E6E6FA',
                '#FFF0F5', '#7CFC00', '#FFFACD', '#ADD8E6', '#F08080', '#E0FFFF',
                '#FAFAD2', '#90EE90', '#D3D3D3', '#FFB6C1', '#FFA07A', '#20B2AA',
                '#87CEFA', '#778899', '#B0C4DE', '#8A2BE2', '#00FF00', '#32CD32',
                '#FAF0E6', '#FF00FF', '#FFFF00', '#66CDAA', '#0000CD', '#BA55D3',
                '#9370DB', '#3CB371', '#7B68EE', '#00FA9A', '#48D1CC', '#C71585',
                '#191970', '#F5FFFA', '#FFE4E1', '#FFE4B5', '#FFDEAD', '#000080',
                '#FDF5E6', '#6B8E23', '#FFA500', '#FF4500', '#DA70D6', '#EEE8AA',
                '#98FB98', '#AFEEEE', '#DB7093', '#FFEFD5', '#FFDAB9', '#CD853F',
                '#FFC8CB', '#DDA0DD', '#B0E0E6', '#800080', '#FF0000', '#BC8F8F',
                '#4169E1', '#8B4513', '#FA8072', '#F4A460', '#2E8B57', '#FFF5EE',
                '#A0522D', '#C0C0C0', '#87CEEB', '#6A5ACD', '#FFFAFA', '#00FF7F',
                '#4682B4', '#D2B48C', '#D8BFD8', '#008080', '#FF6347', '#40E0D0' ]

# Logo link and image
LOGO_LINK = "/"
LOGO_IMAGE = "rrdscout_logo.png"

# Link to help site
HELP_LINK = "#"

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
}
DATA_SOURCE_CONVERT = {
    'C': 'celsius',
}

# Automatically label some units
# do not use white spaces
GRAPH_LABEL={
    'PF': 'Power Factor',
}

# Which units shall not have a summary table?
DATA_SOURCES_WITHOUT_SUMMARY = ['kWh']


# Global translation of data sources
DATA_SOURCE_TRANSLATION = { 'kwh-0': 'kWh Port 1',
}

# Per device translation  ovverrides settings from GLOBAL_TYPES_TRANSLATION
DEVICE_TRANSLATION = {'test-node-01': {'kWh_total': 'A description text for a data source at a specific device',
                                   }
                      }
