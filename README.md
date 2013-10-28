RRDscout  [![Build Status](https://travis-ci.org/isginf/rrdscout.png)](https://travis-ci.org/isginf/rrdscout.png ) [![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/isginf/rrdscout/trend.png)](https://bitdeli.com/free "Bitdeli Badge")
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


License
=======

Copyright 2013 ETH Zurich, ISGINF, Bastian Ballmann and Daniel Winter
E-Mail: bastian.ballmann@inf.ethz.ch daniel.winter@inf.ethz.ch
Web: http://www.isg.inf.ethz.ch

This is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

It is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License.
If not, see <http://www.gnu.org/licenses/>.
