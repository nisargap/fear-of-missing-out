import expedia as exp
import json
import requests
def sendReq():
    theURL = "http://terminal2.expedia.com/x/nlp/results?q=" + " holiday honeymoons" + "&apikey=" + exp.key
    attrReq = requests.get(theURL).content
    attrReq = json.loads(attrReq)
    print "CLUSTERS:"
    print attrReq["result"]["clusters"][0].keys()
    print "PREF ENT: "
    print attrReq["result"]["clusters"][0]["preferredEntity"]
    print "CLUSTERS HOTELS: "
    print attrReq["result"]["clusters"][0]["hotels"][0].keys()
    print "RESULT: "
    print attrReq["result"].keys()
    print "HOTEL KEYS:"
    print attrReq["result"]["hotels"][0].keys()
    print "CENTER: "
    print attrReq["result"]["hotels"][0]["center"].keys()
    print "SIGNALS: "
    print attrReq["result"]["hotels"][0]["signals"][0].keys()
    print "SIGNALS PERCENT: "
    print attrReq["result"]["hotels"][0]["signals"][0]["percent"]
    print "SIGNALS TYPE: "
    print attrReq["result"]["hotels"][0]["signals"][0]["type"]
    if len(attrReq["result"]["hotels"]) >= 3:
        for i in range(0,3):
            print attrReq["result"]["hotels"][i]["name"]
            print attrReq["result"]["hotels"][i]["score"]
sendReq()
