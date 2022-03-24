from flask import request, redirect, url_for, session, current_app, session
from flask import render_template
from test import mysubsite
from pymongo import MongoClient, ASCENDING, DESCENDING

@mysubsite.route("/")
def main():
    mongo_client = MongoClient("mongodb://localhost:27017")
    db = mongo_client.testDB
    collections= db.list_collection_names()

    collect = []
    col = db.collection.find().limit(5)
    for c in col:
        collect.append(c)

    if "unicode" in request.args:
        code = request.args["unicode"]
        return render_template("basic.html", value=code, collection=collect)
    
    else:
        return render_template("basic.html", value="HI", collection=collect)
    
