from flask import request, redirect, url_for, session, current_app, session
from flask import render_template
from summer import mysubsite
from pymongo import MongoClient, ASCENDING, DESCENDING


@mysubsite.route("/")
def main():
    mongo_client = MongoClient("mongodb://localhost:27017")
    db = mongo_client.testDB
    collections= db.list_collection_names()

    if "newKey" in request.form:
        key = request.form["newKey"]
        val = request.form['newValue']
        name = request.form['name']
        db.collections.update_one({'name' : name}, {"$set" : {key : val}})
        return render_template("basic.html", value=code, collection=collect)
    
    scripts = []
    nameScripts = db.collections.find()
    nameScripts = nameScripts.sort([("name", ASCENDING)])
    for name in nameScripts:
        scripts.append(name)
    

    msg = ''
    if 'msg' in request.args:
        msg = request.args['msg']

    return render_template("basic.html", msg=msg, scripts=scripts)
    

@mysubsite.route("/script")
def script():
    mongo_client = MongoClient("mongodb://localhost:27017")
    db = mongo_client.testDB
    collections= db.list_collection_names()

    scr = request.args['scr']

    return render_template("basic.html")
    
'''
    else:
        name = request.form['name']
        for key, val in request.form.items():
            if "_" in key:
                sp + key.split("_")
                key = sp[0]
                oldVal = sp[1]
            else:
'''                
    
