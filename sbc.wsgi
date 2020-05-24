#! /home/dmitriy/testap/venv/bin/python3 
import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/home/dmitriy/testap')
from app import app as application
# app.secret_key = 'anythingsecretkey'

