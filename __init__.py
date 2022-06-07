from flask import Flask, current_app, url_for
mysubsite = Flask(__name__)
from summer import routes

'''
@mysubsite.route('/')
def index():
 return 'hello flask'


mysubsite.config['SERVER_NAME'] = 'writingsystems.org'
with mysubsite.app_context():
    print(url_for('index', _external=True))
'''

