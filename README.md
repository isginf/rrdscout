[![Build Status](https://travis-ci.org/isginf/rrdscout.png)](https://travis-ci.org/isginf/rrdscout.png )

RRDscout  
========

RRDscout is a web frontend to generate rrd graphs from rrd files created by collectd.
In contrast to other rrd web frontends it supports features like

- Automatic recalculation of rrd values
- Dynamic renaming of data sources depending on data source name or even data source of a specific device
- Aggregated graphs
- Multi-line graphs

The installation process for different environments is described in the file INSTALL.txt

For a quick evaluation setup try the development server version by running

    ./run.py [ip] [port]
