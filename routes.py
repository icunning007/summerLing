from flask import request, redirect, url_for, session, current_app, session
from flask import render_template
from summer import mysubsite
from pymongo import MongoClient, ASCENDING, DESCENDING
import re

@mysubsite.route("/advancedSearch", methods=['GET', 'POST'])
def advancedSearch():
    mongo_client = MongoClient("mongodb://localhost:27017")
    db = mongo_client.worldScriptsUMW
    collections= db.list_collection_names()
    
    if "searched" in request.form:
        query = []
        
        query.append({"Name":{"$not": re.compile('bibliography')}})

        if "Name" in request.form:
            value = request.form['Name']
            if value:
                query.append({"Name":{"$regex":value, "$options":'i'}})
        if "type" in request.form:
            value = request.form['type']
            if value:
                query.append({"type":{"$regex":value, "$options":'i'}})
            
        print(query)
        result = db.collections.find({"$and":query})
        return render_template("results.html", result=result)

            

    return render_template("search.html")

@mysubsite.route("/ISOcodes", methods=['GET', 'POST'])
def ISOcodes():
    mongo_client = MongoClient("mongodb://localhost:27017")
    db = mongo_client.worldScriptsUMW
    collections= db.list_collection_names()

    ISO = []
    find=''
    name = ''
    if "filterISO" in request.form:
        name = request.form['search']
        num = db.collections.count_documents({"Name" : "ISO.2", 'code2':name})
        if num == 0:
            find = "No"
        else:
            find = db.collections.find({"Name" : "ISO.2", 'code2':name}).next()
        
    iso = db.collections.find({"Name" : "ISO.2"})
    for i in iso:
        ISO.append(i)
    return render_template("ISOcodes.html", iso=ISO, result=find, name=name)

@mysubsite.route("/Results", methods=['GET', 'POST'])
def Results():
    mongo_client = MongoClient("mongodb://localhost:27017")
    db = mongo_client.worldScriptsUMW
    collections= db.list_collection_names()
    search = request.args['search']
    values = search.split(" ")
    total = 0
    query = []
    for v in values:
        query.append({"Name":{"$regex":v, "$options":'i'}})
    nameResult = db.collections.find({"$and":query})
    name = []
    for n in nameResult:
        if "bibliography" not in n['Name']:
            total += 1
            name.append(n)
    nameTotal = len(name)
    return render_template("results.html", name=name, total=total, nameTotal=nameTotal)

@mysubsite.route("/about", methods=['GET', 'POST'])
def about():
    return render_template("about.html")

@mysubsite.route("/ScriptDescription", methods=['GET', 'POST'])
def ScriptDescription():
    mongo_client = MongoClient("mongodb://localhost:27017")
    db = mongo_client.worldScriptsUMW
    collections= db.list_collection_names()
    name = request.args["script"]
    nameScripts = db.collections.find({"Name" : name}).next()                     #get all the scripts
    return render_template("ScriptDescription.html", script=nameScripts)

@mysubsite.route("/example", methods=['GET', 'POST'])
def example():
    mongo_client = MongoClient("mongodb://localhost:27017")
    db = mongo_client.worldScriptsUMW
    collections= db.list_collection_names()
    if "search" in request.args:
        search = request.args['search']
        return redirect(url_for("Results", search=search))

    nameScripts = db.collections.find()                     #get all the scripts
    nameScripts = nameScripts.sort([("Name", ASCENDING)])   #sort them in alphabetical order
    #code for displaying existing skripts
    certScripts = []
    alphabet = {}

    bib_dic = []
    bib_true = 0
    totalNum = 0

    for name in nameScripts:    #adds the name of scripts to a list
        if "bibliography" not in name['Name'] and "ISO.2" not in name["Name"]:
            cert = db.collections.find({"Name" : name['Name']}, {'_id': False, "ignore_certified":1}).next()
            certScripts.append(name) 
            totalNum += 1
            key = name['Name'][0]
            alphKeys = alphabet.keys()
            if key not in alphKeys:
                alphabet[key] = [name['Name']]
            else:
                alphabet[key].append(name['Name'])

            '''cert = cert['ignore_certified']
            if(cert==1):
                print(name['Name'])
                certScripts.append(name) '''
        if "bibliography" in name["Name"] and "ISO.2" not in name['Name']:
            script = str(name['Name']).split("_")
            find = db.collections.find({"Name" : name['Name'], "Sources.0" : {"$exists" : True}})
            for f in find:
                for val in f['Sources']:
                    bib_true = 1
                    val['script'] = script[0]
                    bib_dic.append(val)

    return render_template("example.html", alphabet=alphabet, totalNum=totalNum, scripts=certScripts, bib_dic=bib_dic)

@mysubsite.route("/", methods=['GET', 'POST'])
def password():
    if 'password' in request.form:
        password = request.form['password']
        correctpass = 'teamFallon'
        if password == correctpass:
            return redirect(url_for("main", msg=f"Your password was correct!"))
        else:
            return redirect(url_for("password", msg=f"Incorrect Password >:|"))
    else:
        msg = ''
        if 'msg' in request.args:
            msg = request.args['msg']
        return render_template('password.html', msg=msg)

''''code for displaying all the scripts'''
@mysubsite.route("/dataEntry", methods=['GET', 'POST'])
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
        mash = str(name) + "_bibliography"
        db.collections.delete_one({"Name":mash})
        mongo_client.close()
        return redirect(url_for("main",scr=name, msg=f"{key} deleted from {name} successfully!"))

    nameScripts = db.collections.find()                     #get all the scripts
    nameScripts = nameScripts.sort([("Name", ASCENDING)])   #sort them in alphabetical order
    keyLabel = ""
    valueLabel = ""
    existsLabel = "yes"
    
    if "filtScript" in request.form:
        key = request.form['key']
        value = request.form['value']
        exists = request.form['true_false']

        if key != "none" and exists == "yes":
            if value:
                existsLabel = "yes"
                keyLabel = str(key)
                valueLabel = str(value)
                ans = db.collections.find({key : {"$regex": value, "$options": 'i'}})
                nameScripts = ans.sort([("name", ASCENDING)])
            else:
                existsLabel = "yes"
                keyLabel = str(key)
                ans = db.collections.find({ key : {"$exists" : 1 }})
                nameScripts = ans.sort([("name", ASCENDING)])
        if key != "none" and exists == "no":
            if value:
                existsLabel = "no"
                keyLabel = str(key)
                valueLabel = str(value)
                ans = db.collections.find({key : {"$regex": value, "$exists" : 0, "$options": 'i'}})
                nameScripts = ans.sort([("name", ASCENDING)])
            else:
                existsLabel = "no"
                keyLabel = str(key)
                ans = db.collections.find({ key : {"$exists" : 0 }})
                nameScripts = ans.sort([("name", ASCENDING)])


    #code for displaying existing skripts
    certScripts = []
    oneTwo = {}
    uncertScripts = []
    scriptCertTF = {}
    totalNum =0


    bib_dic = []
    bib_true = 0

    for name in nameScripts:    #adds the name of scripts to a list
        if "bibliography" not in name['Name'] and "ISO.2" not in name['Name']:
            totalNum += 1
            cert = db.collections.find({"Name" : name['Name']}, {'_id': False, "ignore_certified":1}).next()
            cert = cert['ignore_certified']
            scriptCertTF[str(name['Name'])] = cert 
            if(cert==1):
                certScripts.append(name)

            else:
                uncertScripts.append(name)
                cert1 = db.collections.count_documents({"Name" : name['Name'], "ignore_certNum1" : {"$exists" : True}})
                cert2 = db.collections.count_documents({"Name" : name['Name'], "ignore_certNum2" : {"$exists" : True}})
                cert1 = int(cert1)
                cert2 = int(cert2)
                name= name['Name']
                if cert1>0 and cert2>0:
                    oneTwo[name] = "both"
                elif cert1>0 and cert2==0:
                    oneTwo[name] = 'one'
                elif cert1==0 and cert2>0:
                    oneTwo[name] = 'two'
                elif cert1==0 and cert2==0:
                    oneTwo[name] = 'neither'

    '''
    allScripts = db.collections.find({"Name" : {"$regex" : 'bibliog', "$options": "i"}})                     #get all the scripts
    allScripts = allScripts.sort([("Sources.author", ASCENDING)])    #sort them in alphabetical order
    ''' 
    allScripts = db.collections.aggregate([{"$project":{"_id":1 ,'Name':1, 'author' : "$Sources.author", "Sources":1}}, {"$unwind":"$author"}, {"$sort": {"author":1}}])

    for name in allScripts:
        if "bibliography" in name["Name"] and "ISO.2" not in name['Name']:
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


    mongo_client.close()                                    #closes the database
    return render_template("basic.html", totalNum=totalNum, oneTwo=oneTwo, valueLabel=valueLabel, keyLabel=keyLabel, existsLabel=existsLabel, bib_true=bib_true, bib_dic=bib_dic, msg=msg, scriptCertTF=scriptCertTF, certScripts=certScripts, uncertScripts=uncertScripts)
    
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
        print("|", mash, "|")
        query = {}

        if 'author' in request.args:
            query['author'] = request.args['author']
        if 'year' in request.args:
            query['year'] = request.args['year']
        if 'book' in request.args:
            query['book'] = request.args['book']
        if 'chapter' in request.args:
            query['chapter'] = request.args['chapter']
        if 'pages' in request.args:
            query['pages'] = request.args['pages']
        if 'publisher' in request.args:
            query['publisher'] = request.args['publisher']
        if 'url' in request.args:
            query['url'] = request.args['url']

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
        ans = db.collections.count_documents({"Name" : mash})
        
        bib_dic = []
        bib_true = 0

        find = db.collections.find({"Name" : mash, "Sources.0" : {"$exists" : True}})
        for f in find:
            for val in f['Sources']:
                bib_true = 1
                bib_dic.append(val)
        
        startScript = ''
        exists = db.collections.count_documents({"Name" : name, "ignore_startedScript" : {"$exists" : True}})
        if exists > 0:
            startScript = db.collections.find({"Name" : name, "ignore_startedScript" : {"$exists" : True}})
            startScript = startScript[0]['ignore_startedScript']
           # for s in startScript:

        mongo_client.close()

        return render_template("scriptEdit.html", startScript=startScript, bib_true=bib_true, bib_dic=bib_dic, certTF=certTF, certNum1=certNum1, certNum2=certNum2, tf=true_false, dic=filtered_dataList, keys = keys, scripts=filtered_data, msg=msg)
   
    #code for adding a new key/value pair
    elif "listkey" in request.form:                
        key=request.form['listkey']                 #gets key name
        if "ddress" in key:
            key = "imageAddress"
        elif "mage" in key and "escription" in key:
            key = "imageDescription"
        elif "mage" in key and "itation" in key:
            key = "imageCitation"
        elif "yperlinks" in key:
            key = "Hyperlinks"
        elif "escription" in key:
            key = "description"
        elif "anguage" in key:
            key = "languages"
        elif "fficial" in key or "ountries" in key:
            key = "countries"
        elif "evelopment" in key or "hildren" in key:
            key = "children"
        elif "arent" in key:
            key = "parent"
        elif "nventor" in key:
            key = "inventor"
        elif "arliest" in key and "ocation" in key:
            key = "earliestLoc"
        elif "arliest" in key and "ate" in key:
            key = "earliestDate"
        elif "atest" in key and "ate" in key:
            key = "latestDate"
        elif "apitals" in key:
            key = "capitalUsed"
        elif "ontextual" in key:
            key = "contextualForms"
        elif "iacritics" in key:
            key = "diacritics"
        elif "lyphs" in key:
            key = "glyphNumber"
        elif "irection" in key:
            key = "direction"
        elif "nicode" in key:
            key = "unicode"
        elif "nicode" in key and "art" in key:
            key = "unicodeChart"
        elif "amily" in key:
            key = "family"
        elif "ype" in key:
            key = "type"
        elif "ote" in key or "esearch" in key:
            key = "researchNotes"
    
        

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
  
    elif "madeScript1" in request.form:
        name = request.form['Name']
        val = request.form['madeScript1']
        db.collections.update_one({"Name":name}, {"$set": {"ignore_startedScript": val}})
        mongo_client.close()
        return redirect(url_for("scriptEdit",scr=name, msg=f"{val} started {name}!"))
    elif "madeScript" in request.form:
        name = request.form['Name']
        val = request.form['madeScript']
        db.collections.update_one({"Name":name}, {"$unset":{"ignore_startedScript" : val}})
        mongo_client.close()
        return redirect(url_for("scriptEdit",scr=name))


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

        mashName = str(name) + "_bibliography"
        
        query = {}

        if 'author' in request.form:
            author = request.form['author']
            query['author'] = str(author)
        if 'chapter' in request.form:
            chapter = request.form['chapter']
            query['chapter'] = str(chapter)
        if 'book' in request.form:
            book = request.form['book']
            query['book'] = str(book)
        if 'publisher' in request.form:
            publisher = request.form['publisher']
            query['publisher'] = str(publisher)
        if 'year' in request.form:
            year = request.form['year']
            query['year'] = str(year)
        if 'pages' in request.form:
            pages = request.form['pages']
            query['pages'] = str(pages)
        if 'url' in request.form:
            url = request.form['url']
            query['url'] = str(url)

        one = {"Name" : mashName}
        two = {"$push" : {"Sources" : query}}


        
        db.collections.update_one(one, two)
        
        mongo_client.close()                    #closes database
        return redirect(url_for("scriptEdit",scr=name, msg=f"Source added!"))


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

