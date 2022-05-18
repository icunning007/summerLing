from flask import Flask, current_app, url_for
mysubsite = Flask(__name__)
from summer import routes

