#!/usr/bin/env python
import os
import sys

if len(sys.argv) != 2:
    print "usage: tr_init <language-code>"
    sys.exit(1)

os.system('pybabel extract -F app/babel.cfg -k lazy_gettext -o app/translations/messages.pot app')
os.system('pybabel init -i app/translations/messages.pot -d app/translations -l ' + sys.argv[1])
os.unlink('app/translations/messages.pot')
