from flask import request, redirect, url_for, session, current_app, session
from flask import render_template
from summer import mysubsite
from pymongo import MongoClient, ASCENDING, DESCENDING

''''code for displaying all the scripts'''
@mysubsite.route("/", methods=['GET', 'POST'])
def main():
    #opens mongo Database
    mongo_client = MongoClient("mongodb://localhost:27017")
    db = mongo_client.worldScriptsUMW
    collections= db.list_collection_names()

    #adding a new script
    if "newScript" in request.form:
        name = request.form['newScript']
        name = name.title()
        exist = db.collections.count_documents({"Name":name})
        #check if the script is already in the database
        if exist == 0:
            db.collections.insert_one({'Name' : name})
            db.collections.update_one({"Name" : name}, {"$set" : {"ignore_certified": 0}})
            mash = str(name) + "_bibliography"
            db.collections.insert_one({
                                    "Name" : mash, "Sources" : []})
            #set certified as false so it only happens once

        else:
            return redirect(url_for("main", msg=f"This script already exists!"))
            
    #deleting a script
    if "delKey" in request.args:
        name = request.args['keyScript']
        key = request.args['delKey']
        db.collections.delete_one({"Name":name})
        mongo_client.close()
        return redirect(url_for("main",scr=name, msg=f"{key} deleted from {name} successfully!"))

    nameScripts = db.collections.find()                     #get all the scripts
    nameScripts = nameScripts.sort([("Name", ASCENDING)])   #sort them in alphabetical order
    
    if "filtScript" in request.form:
        key = request.form['key']
        value = request.form['value']
        print(key)
        if key != "none":
            if value:
                print("yes-value")
                ans = db.collections.find({key : {"$regex": value, "$options": 'i'}})
                nameScripts = ans.sort([("name", ASCENDING)])
            else:
                print("no-value")
                ans = db.collections.find({ key : {"$exists" : 1 }})
                nameScripts = ans.sort([("name", ASCENDING)])


    #code for displaying existing skripts
    certScripts = []
    uncertScripts = []
    scriptCertTF = {}

    bib_dic = []
    bib_true = 0

    for name in nameScripts:    #adds the name of scripts to a list
        if "bibliography" not in name['Name']:
            print(name['Name'])
            cert = db.collections.find({"Name" : name['Name']}, {'_id': False, "ignore_certified":1}).next()
            cert = cert['ignore_certified']
            if(cert==1):
                certScripts.append(name)
            else:
                uncertScripts.append(name)

            name = str(name['Name'])
            scriptCertTF[name] = cert 
    
    allScripts = db.collections.find()                     #get all the scripts
    allScripts = allScripts.sort([("Name", ASCENDING)])    #sort them in alphabetical order
    for name in allScripts:
        if "bibliography" in name["Name"]:
            print(name['Name'])
            script = str(name['Name']).split("_")
            find = db.collections.find({"Name" : name['Name'], "Sources.0" : {"$exists" : True}})
            for f in find:
                for val in f['Sources']:
                    bib_true = 1
                    val['script'] = script[0]
                    bib_dic.append(val)
            

    #if there's a mesage we get it here
    msg = ''
    if 'msg' in request.args:
        msg = request.args['msg']

    print(scriptCertTF)

    mongo_client.close()                                    #closes the database
    return render_template("basic.html", bib_true=bib_true, bib_dic=bib_dic, msg=msg, scriptCertTF=scriptCertTF, certScripts=certScripts, uncertScripts=uncertScripts)
    
'''code for editing an individual script'''
@mysubsite.route("/script", methods=['GET', 'POST'])
def scriptEdit():
    #opening the database
    mongo_client = MongoClient("mongodb://localhost:27017")
    db = mongo_client.worldScriptsUMW
    collections= db.list_collection_names()

    msg = ''

    #code to delete individual value
    if "delValue" in request.args:
        name = request.args['valueName']
        key = request.args['delValue']
        val = request.args['val']
        #mash = str(key) + "." + str(val)
        db.collections.update_one({"Name":name}, {"$pull":{ key : val}})
        count = db.collections.count_documents({"Name": name, key : {"$size" : 0}})
        if count == 1:
            db.collections.update_one({"Name":name}, {"$unset":{key : ""}})

        mongo_client.close()
        return redirect(url_for("scriptEdit",scr=name, msg=f"{val} deleted from {name} successfully!"))
    #code to delete entire key
    if "delkey" in request.args:
        name = request.args['nam']
        key = request.args['delkey']
        db.collections.update_one({"Name":name}, {"$unset":{key : ""}})
        mongo_client.close()
        return redirect(url_for("scriptEdit",scr=name, msg=f"{key} deleted from {name} successfully!"))
   
    if "bibName" in request.args:
        name = request.args['bibName']
        mash = str(name) + "_bibliography"
        publisher = request.args['publisher']
        print("|", publisher, "|")
        query = {}
        
        if request.args['author']:
            query['author'] = request.args['author']
        if request.args['year']:
            query['year'] = request.args['year']
        if request.args['book']:
            query['book'] = request.args['book']
        if request.args['chapter']:
            query['chapter'] = request.args['chapter']
        if request.args['pages']:
            query['pages'] = request.args['pages']
        if request.args['publisher']:
            query['publisher'] = request.args['publisher']

        db.collections.update_one({"Name" : mash}, {"$pull" : {"Sources" : query}})

        return redirect(url_for("scriptEdit",scr=name, msg=f"Source deleted from {name} successfully!"))

    if request.method=="GET":
        #name of script
        name = request.args['scr']
        
        existCert1 = db.collections.count_documents({"Name":name, "ignore_certNum1": {"$exists": 1}})
        existCert2 = db.collections.count_documents({"Name":name, "ignore_certNum2": {"$exists": 1}})
        certNum1 = ''
        certNum2 = ''
        certTF = 0
        if existCert1 == 1 and existCert2 == 1:
            print("1!!!")
            certTF = 1
            db.collections.update_one({"Name":name}, {"$unset":{"ignore_certified" : ""}})
            db.collections.update_one({"Name":name}, {"$set": {"ignore_certified": 1}})
            certNum1 = db.collections.find({"Name" : name}, {'_id': False, "ignore_certNum1":1}).next()
            for key, val in certNum1.items():
                certNum1 = val
            certNum2 = db.collections.find({"Name" : name}, {"ignore_certNum2"}).next()
            for key, val in certNum2.items():
                certNum2 = val
        elif existCert1 == 1 and existCert2 == 0:
            print("2!!!")
            db.collections.update_one({"Name":name}, {"$unset":{"ignore_certified" : ""}})
            db.collections.update_one({"Name":name}, {"$set": {"ignore_certified": 0}})
            certNum1 = db.collections.find({"Name" : name}, {"ignore_certNum1"}).next()
            for key, val in certNum1.items():
                certNum1 = val
        elif existCert1 == 0 and existCert2 == 1:
            print("3!!!")
            db.collections.update_one({"Name":name}, {"$unset":{"ignore_certified" : ""}})
            db.collections.update_one({"Name":name}, {"$set": {"ignore_certified": 0}})
            certNum2 = db.collections.find({"Name" : name}, {"ignore_certNum2"}).next()
            for key, val in certNum2.items():
                certNum2 = val

        
        #get all the data from the database for the script
        print(name)
        ans = db.collections.find({"Name" : name}, {"_id":0}).next()
        filtered_data = {}
        filtered_dataList = {}
        true_false = {}                         #checks if it the value needs a big box
        for key, val in ans.items():
            if type(val) in [int, str]:
                filtered_data[key] = val
            if type(val) in [list]:             #all data should be list
                for v in val:
                    if type(v) not in [int]:
                        if len(v) > 56:             #makes the text box larger
                            true_false[v] = 1
                        else:
                            true_false[v] = 0

                #if key exists already just add to the key
                if key in filtered_dataList.keys():
                    filtered_dataList[key].append(val)
                #orthewise create the key and add value
                else:
                    filtered_dataList[key] = []
                    filtered_dataList[key].append(val)
        #gets a list of keys
        keys = []
        for key, val in filtered_dataList.items():
            if "ignore" not in key:             #makes sure I want it displayed
                keys.append(key)
        
        #get the message
        msg = ''
        if 'msg' in request.args:
            msg = request.args['msg']
      
        


        mash = str(name) + "_bibliography"
        print(mash)
        ans = db.collections.count_documents({"Name" : mash})
        
        bib_dic = []
        bib_true = 0

        find = db.collections.find({"Name" : "Arabic_bibliography", "Sources.0" : {"$exists" : True}})
        for f in find:
            for val in f['Sources']:
                bib_true = 1
                bib_dic.append(val)
        


        mongo_client.close()

        return render_template("scriptEdit.html", bib_true=bib_true, bib_dic=bib_dic, certTF=certTF, certNum1=certNum1, certNum2=certNum2, tf=true_false, dic=filtered_dataList, keys = keys, scripts=filtered_data, msg=msg)
   
    #code for adding a new key/value pair
    elif "listkey" in request.form:                
        key=request.form['listkey']                 #gets key name
        if "yperlinks" in key:
            key = "Hyperlinks"
        elif "escription" in key:
            key = "description"
        elif "evelopment" in key:
            key = "children"
        elif "arent" in key:
            key = "parent"
        elif "arliest" in key and "ocation" in key:
            key = "earliestLoc"
        elif "arliest" in key and "ate" in key:
            key = "earliestDate"
        elif "atest" in key and "ate" in key:
            key = "latestDate"
        elif "apitals" in key:
            key = "capitalUsed"
        elif "lyphs" in key:
            key = "glyphNumber"
        elif "irection" in key:
            key = "direction"
        elif "amily" in key:
            key = "family"
        elif "ype" in key:
            key = "type"

        #key = key.title()                           #makes the key title case
        val=request.form['listvalue']               #gets value
        name=request.form['Name']                   #gets name of script
        #checks if script exists or not
        exist = db.collections.count_documents({"Name":name, key:val})
        if exist == 0:
            db.collections.update_one({"Name":name}, {"$push": {key : val}})
            mongo_client.close()                    #closes database
            return redirect(url_for("scriptEdit",scr=name, msg=f"{val} added!"))
        else:
            mongo_client.close()                    #closes database
            return redirect(url_for("scriptEdit",scr=name, msg=f"{val} already exists!"))
   
    #All the certifications are to make sure that the people working on the research
    #have all the information they want to have in it + it's been checked
    #only after that it will be published
    elif "certificationNum1" in request.form:
        name = request.form['Name']                 #gets script name
        val = request.form['certificationNum1']
        db.collections.update_one({"Name":name}, {"$set": {"ignore_certNum1": val}})
        exist = db.collections.count_documents({"Name":name, "ignore_peopleWhoSigned":val})
        if exist == 0:
            db.collections.update_one({"Name":name}, {"$push": {"ignore_peopleWhoSigned": val}})
        mongo_client.close()                    #closes database
        return redirect(url_for("scriptEdit",scr=name, msg=f"{val} signed!"))

    elif "certificationNum2" in request.form:
        name = request.form['Name']                 #gets script name
        val = request.form['certificationNum2']
        db.collections.update_one({"Name":name}, {"$set": {"ignore_certNum2": val}})
        mongo_client.close()                    #closes database
        return redirect(url_for("scriptEdit",scr=name, msg=f"{val} signed!"))
    
    #In case they wanted to work more on the script they can unsign it, so it would be
    #unpublished until it gets signed again and they're done working.
    elif "unsignNum1" in request.form:
        name = request.form['Name']
        val = request.form['unsignNum1']
        db.collections.update_one({"Name":name}, {"$unset":{"ignore_certNum1" : val}})
        mongo_client.close()                    #closes database
        return redirect(url_for("scriptEdit",scr=name, msg=f"{val} UNsigned!"))
        
    elif "unsignNum2" in request.form:
        name = request.form['Name']
        val = request.form['unsignNum2']
        db.collections.update_one({"Name":name}, {"$unset":{"ignore_certNum2" : val}})
        mongo_client.close()                    #closes database
        return redirect(url_for("scriptEdit",scr=name, msg=f"{val} UNsigned!"))
    
    
    elif "textSource" in request.form:
        name = request.form['Name']
        author = request.form['author']
        year = request.form['year']
        book = request.form['book']
        chapter = request.form['chapter']
        pages = request.form['pages']
        publisher = request.form['publisher']
        mashName = str(name) + "_bibliography"
        
        query = {}

        if author:
            query['author'] = str(author)
        if chapter:
            query['chapter'] = str(chapter)
        if book:
            query['book'] = str(book)
        if publisher:
            query['publisher'] = str(publisher)
        if year:
            query['year'] = str(year)
        if pages:
            query['pages'] = str(pages)

        one = {"Name" : mashName}
        two = {"$push" : {"Sources" : query}}


        print('db.collections.update_one({"Name" : "test_biliography"}, {"$push" : {"Sources" : {"author" : "Boy, Guy",  "chapter" : "What he does cool",  "book" : "The book",  "publisher" : "Food Network",  "year" : "2009 CE",  "pages" : "40-79"}}})')
        print("db.collections.update_one(" + str(one) + str(two))
        
        db.collections.update_one(one, two)
        
        mongo_client.close()                    #closes database
        return redirect(url_for("scriptEdit",scr=name, msg=f"{book}, {year} added!"))


    #for make changes portion
    else:
        name = request.form['Name']                 #gets script name
        print("NAME="+str(name))
        for key, val in request.form.items():
            print("KEY=" + key)
            print("VAL=" + val)
            if "_" in key and val:                          #splits on the _ because it's the value that changes  
                sp = key.split("_")
                key = sp[0]
                oldVal = sp[1]
                count = db.collections.count_documents({"Name":name, key: val}) #count num of key/value 
                count = int(count)                              #pairs that exist with those kye/values
                if count==0:                                    #if it doesn't exist (0) then update it
                    db.collections.update_one({"Name":name}, {"$pull":{ key : oldVal}})
                    db.collections.update_one({"Name":name}, {"$push": {key : val}})
            elif "Name" not in key:
                if val:
                    db.collections.update_one({"Name":name}, {"$push": {key : val}})

        mongo_client.close()                                    #closes database
        
        return redirect(url_for("scriptEdit",scr=name, msg=f"{name} updated successfully!"))

