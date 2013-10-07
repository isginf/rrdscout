import sys
sys.path.insert(0, '/opt/rrdscout')

activate_this = '/opt/virtualenvs/rrdscout/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from app import app as application

application.config['SECRET_KEY'] = 'F34TF$($e34D';