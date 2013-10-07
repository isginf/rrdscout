#!/usr/bin/env python
import sys
from app import app
from werkzeug.contrib.profiler import ProfilerMiddleware

app.config['SECRET_KEY'] = 'F34TF$($e34D'

# enable profiling
#app.config['PROFILE'] = True
#app.wsgi_app = ProfilerMiddleware(app.wsgi_app)

debug = True
host = "127.0.0.1"
port = 5000

if len(sys.argv) == 2:
    host = sys.argv[1]
elif len(sys.argv) == 3:
    host = sys.argv[1]
    port = int(sys.argv[2])

app.run(debug=debug, host=host, port=port)