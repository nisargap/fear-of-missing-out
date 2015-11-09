from flask import Flask, request, redirect,render_template, session
import urllib
from collections import deque
import twilio.twiml
import hackAppAuto as happ
import requests
import time
import expedia as exp
from twilio.rest import TwilioRestClient 
import json
import creds

# put your own credentials here 
ACCOUNT_SID = creds.ACCOUNT_SID
AUTH_TOKEN = creds.AUTH_TOKEN
client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN) 


webAppMenu = ["Welcome to fomo : Fear of Missing Out!", 
        "press 1 to apply for hackathons...", 
        "press 2 to find a dream vacation...", 
        "press 3 to do our survey..."]

webCurr = {"hackathon" : False, "expedia" : False, "survey" : False}
# gets the user's last sent message
def getUserMessage():
    messages = client.messages.list(  ) 
    return messages[0].body

app = Flask(__name__, static_url_path='')
firstTextMessage = True
app.config['SECRET_KEY'] = 'secret!'    
callers = {}
attractions = {}
currentState = {"hackathon" : False, "expedia" : False, "survey" : False}

def checkOthers(name):
    for key in currentState:
        if not key == name and currentState[key] == True:
            return False
    return True

def checkOthersWeb(name):
    for key in webCurr:
        if not key == name and webCurr[key] == True:
            return False
    return True

def resetSurveyVars():
    global callers
    currentState["survey"] = False
    callers = {}

@app.route("/start", methods=['GET','POST'])
def start():
    resp = twilio.twiml.Response()
    userMessage = getUserMessage()
    if userMessage == "bye":
        currentState["hackathon"] = False
        currentState["expedia"] = False
        resetSurveyVars()

    if userMessage == "menu":
        resp.message("hackathon->1, expedia->2, survey->3")
        return str(resp)

    if (userMessage == "1" or userMessage.lower() == "hackathon") and checkOthers("hackathon"):
        currentState["hackathon"] = True
    
    if (userMessage == "2" or userMessage.lower() == "expedia") and checkOthers("expedia"):
        currentState["expedia"] = True
        
    if (userMessage == "3" or userMessage.lower() == "survey") and checkOthers("survey"):
        currentState["survey"] = True

    if currentState["hackathon"]:
        currentState["hackathon"] = False
        resp.message("coming soon!")

    if currentState["expedia"]:
        return expedia_start(resp)

    if currentState["survey"]:
        return sms(resp)    
        
    return str(resp)

def expedia_start(resp):
    resp = resp
    userMessage = getUserMessage()
    if userMessage == "2" or userMessage == "expedia":
        resp.message("enter a dream vacation")
    if len(userMessage) > 1 and not userMessage == "expedia":
        question =  userMessage
        theURL = "http://terminal2.expedia.com/x/nlp/results?q=" + question + "&apikey=" + exp.key
        attrReq = requests.get(theURL).content
        attrReq = json.loads(attrReq)
        msg = ""
        if len(attrReq["result"]["hotels"]) >= 3:
            for i in range(0,3):
                msg += attrReq["result"]["hotels"][i]["name"] + "; "
                
        resp.message(msg)
        
    return str(resp)
def expedia_web_start(userMessage):
    if len(userMessage) > 1:
        question =  userMessage
        theURL = "http://terminal2.expedia.com/x/nlp/results?q=" + question + "&apikey=" + exp.key
        attrReq = requests.get(theURL).content
        attrReq = json.loads(attrReq)
        msg = []
        if len(attrReq["result"]["hotels"]) >= 3:
            for i in range(0,len(attrReq["result"]["hotels"])):
                msg.append("Hotel: " + attrReq["result"]["hotels"][i]["name"])
                msg.append(" Score: " + str(int(attrReq["result"]["hotels"][i]["score"]) - 1) + "/10")
        return json.dumps(msg)
    return json.dumps(["enter a dream vacation"])

def sms(resp):
    resp = resp
    userMessage = getUserMessage()
    global firstTextMessage
    if userMessage[0] == ';':
        code = userMessage[1:]
        response = str(eval(code))
        resp.message(response)
    else:
        """Respond to incoming calls with a simple text message."""
        from_number = request.values.get('From', None)
        if not from_number in callers:
            callers[from_number] = {"answers":[], "questions" : deque(happ.getQuestions()), "submitted" : False}
    
    
        if callers[from_number]["questions"]:
            resp.message(callers[from_number]["questions"][0])
            callers[from_number]["questions"].popleft()
            if not firstTextMessage:
                callers[from_number]["answers"].append(userMessage)
            firstTextMessage = False
        elif not callers[from_number]["submitted"]:
            happ.submitForm(callers[from_number]["answers"])
            callers[from_number]["submitted"] = True
            currentState["survey"] = False
        if callers[from_number]["submitted"]:
            resp.message("Thank you for filling out our form!")

    return str(resp)


answers = {}
userMessages = {}
mySessions = {}
def webSMS(userMessage):
    oldValue = "You have submitted!"
    if session.get('unique') == False:
        session['unique'] = int(time.time())
    if not session['unique'] in mySessions:
        mySessions[session['unique']] =  {"questions" : deque(happ.getQuestions()), "submitted" : False}
    if mySessions[session['unique']]["questions"]:
        oldValue = mySessions[session['unique']]["questions"][0]
        mySessions[session['unique']]["questions"].popleft()
    elif not mySessions[session['unique']]["submitted"]:
        happ.submitForm(answers[session['unique']])
        # here is where further expansions can be done for after a form has been completed
        userMessages[session['unique']] = []
        mySessions[session['unique']]["submitted"] = True
    
    return oldValue

@app.route("/use", methods=["GET"])
def use():
    userMessages = webAppMenu
    return render_template('use.html', message=userMessages)

fwm = True
answersWeb = {}
questionsWeb = {}
webSubmit = {}
userMsgStore = {}
currentHackathon = ""
def resetWebVars():
    global answersWeb
    global questionsWeb
    global webSubmit
    global userMsgStore
    global currentHackathon
    answersWeb = {}
    questionsWeb = {}
    webSubmit = {}
    userMsgStore = {}
    currentHackathon = ""
@app.route("/socket", methods=["POST"])
def socket():
    if not session.get("unique"):
        session["unique"] = int(time.time())
    
    userMessage = request.form["usermsg"]
    if not session['unique'] in userMsgStore:
        userMsgStore[session['unique']] = []
    if userMessage == "menu":
        webCurr["hackathon"] = False
        webCurr["expedia"] = False
        webCurr["survey"] = False
        answersWeb = {}
        return json.dumps(webAppMenu)
    if userMessage == "bye":
        webCurr["hackathon"] = False
        webCurr["expedia"] = False
        webCurr["survey"] = False
        answersWeb = {}
        return json.dumps(["you quit!"])
    if (userMessage == "1" or userMessage == "hackathon") and checkOthersWeb("hackathon"):
        webCurr["hackathon"] = True

    # update webCurr in the 2nd userMessage section to become True
    if (userMessage == "2" or userMessage == "expedia") and checkOthersWeb("expedia"):
        webCurr["expedia"] = True
        # return json.dumps(["yoooooo!"])
    if (userMessage == "3" or userMessage == "survey") and checkOthersWeb("survey"):
        webCurr["survey"] = True
    global currentHackathon
    if webCurr["hackathon"] and checkOthersWeb("hackathon"):
        if userMessage == "1":
            return json.dumps(["2 for MHacks", "3 for WHACK", "4 for HackUMass"])
        if userMessage == "2":
            currentHackathon = "MHACKS MHACKS"
        if userMessage == "3":
            currentHackathon = "WHACK Registration Form"
        if userMessage == "4":
            currentHackathon = "HackUMass III Application"
        if currentHackathon == "":
            currentHackathon = "MHACKS MHACKS"
        
        return recordWebAnswer(userMessage, currentHackathon)

    if webCurr["expedia"] and checkOthersWeb("expedia"):
        return expedia_web_start(userMessage)
    # update webCurr in the 3rd userMessage section to become True
    if webCurr["survey"] and checkOthersWeb("survey"):
        # take out general elements to top
        global fwm
        if not session.get('unique'):
            session['unique'] = int(time.time())
        if not session['unique'] in userMessages:
            userMessages[session['unique']] = []
        if not session['unique'] in answers:
            answers[session['unique']] = []
        global fwm
        userMessages[session['unique']].append(userMessage)
        if fwm == False:
            answers[session['unique']].append(userMessage)
        fwm = False
        userMessages[session['unique']].append(webSMS(userMessage))
        return json.dumps(userMessages[session['unique']])
    if userMessage:
        return json.dumps(["Choose a valid menu option"])
firstTime = True
def recordWebAnswer(userMessage, name):
    global firstTime
    userMsgStore[session['unique']].append(userMessage)
    oldValue = userMessage
    if not session['unique'] in answersWeb:
        answersWeb[session['unique']] = []
    if not session['unique'] in questionsWeb:
        questionsWeb[session['unique']] = deque(happ.getQuestionsAuto(name))
    if not session['unique'] in webSubmit:
        webSubmit[session['unique']] = False
    if firstTime == False:
        answersWeb[session['unique']].append(userMessage)
        if questionsWeb[session['unique']]:
            oldValue = questionsWeb[session['unique']][0]
    firstTime = False
    if questionsWeb[session['unique']]:
        userMsgStore[session['unique']].append([questionsWeb[session['unique']][0]])
        questionsWeb[session['unique']].popleft()
        #return json.dumps([questionsWeb[session['unique']][0]])
        return json.dumps(userMsgStore[session['unique']])
    elif webSubmit[session['unique']] == False:
        happ.submitFormAuto(answersWeb[session['unique']],name)
        webSubmit[session['unique']] = True
        resetWebVars()

        webCurr["hackathon"] = False
    else:
        webCurr["hackathon"] = False
    return json.dumps(["You successfully submitted!"])
        
@app.route("/", methods=["GET"]) 
def home():
    session["unique"] = int(time.time())
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=80)

