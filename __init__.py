from flask import Flask, current_app, url_for
mysubsite = Flask(__name__)
from summer import routes

'''
if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SERVER_NAME'] = 'writingsystems.org'
    app.run(host=app.config['SERVER_NAME'], port=80, debug=True)

mysubsite.config['SERVER_NAME'] = 'writingsystems.org'
with mysubsite.app_context():
    print(url_for('index', _external=True))
'''
