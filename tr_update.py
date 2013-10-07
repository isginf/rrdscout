#!/usr/bin/env python
import os
import sys

os.system('pybabel extract -F app/babel.cfg -k lazy_gettext -o app/translations/messages.pot app')
os.system('pybabel update -i app/translations/messages.pot -d app/translations')
os.unlink('app/translations/messages.pot')
