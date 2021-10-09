from flask import Flask,render_template, request, jsonify, redirect
import random
import json
app = Flask(__name__)
import pyrebase

firebaseConfig = {
    "apiKey": "AIzaSyAhI-yYG7Rb0d7AQbGejjMXGbOkNxoHxA4",
    "authDomain": "automated-ship-loading-planner.firebaseapp.com",
    "databaseURL": "https://automated-ship-loading-planner-default-rtdb.firebaseio.com",
    "projectId": "automated-ship-loading-planner",
    "storageBucket": "automated-ship-loading-planner.appspot.com",
    "messagingSenderId": "525902838420",
    "appId": "1:525902838420:web:ac55f0fa910f2e2796d281"
}

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

auth = firebase.auth()
global finbay
Capacity = 0
var_list = []
rows = []
baysList = []
sortedList = []
colors = ['red','darkgreen','yellow','lightblue','pink','orange','coralblue','grey','violet']


class Bay:
    def __init__(self, id, arr):
        self.id = id
        self.tiers = len(arr)
        self.rows = len(arr[0])
        self.arr = arr
    
    def __repr__(self):
        return str(self.arr)

ships = {}
containers = {}

def output(noOfTiers,noOfRows):
    rows = []
    for i in range(noOfTiers):
        rows.append(noOfRows[i])
    rws = []
    totalSpace = rows[0]
    for j in range(noOfTiers):
        rws.append([])
        shipSpace = totalSpace - rows[j]

        for k in range(int(shipSpace/2)):
                rws[j].append(False)

        for k in range(totalSpace-shipSpace):
                rws[j].append(True)

        for k in range(int(shipSpace/2)):
                rws[j].append(False)
    return rws

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        string = var_list[0].split("@", 1)
        email = string[0]
        var_list.append(email)
        password = request.form["password"]
        print(email, password)
        try:
            auth.sign_in_with_email_and_password(email, password)

        except:
            return "Error please enter valid credentials"
        return redirect("/home")
    return render_template('login.html')

@app.route('/plangeneration', methods=['GET', 'POST'])
def plan():
    bays = int(request.form['bays'])
    Capacity = int(request.form['capacity'])
    # baysList.append(bays)
    ship = request.form["shipid"]
    email = var_list[0]
    print(email)
    var_list.append(ship)
    result = []
    for i in range(bays):
        rows = list(map(int, request.form[f'rows{i}'].split(',')))
        arr = output(int(request.form[f'tier{i}']), rows)
        bayb = Bay(i+1, arr).__dict__
        result.append(bayb)
        baysList.append(result)
        db.child("users").child({"userEmail" : email}).child("Ships").child({"ShipID" : ship}).child("Bays").push({"bay" :json.dumps(bayb)})
    
    ships[request.form['shipid']] = result
    return render_template('plangeneration.html', arr=result)


@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        email = request.form["email"]
        db.child("users").push(email)
    return render_template('home.html')

@app.route('/result', methods=['GET', 'POST'])
def result():
    a = json.loads(request.form['hiddenField'])[0]
    email = var_list[0]
    db.child("users").child({"userEmail" : email}).child("Containers").push(json.loads(request.form['hiddenField']))
    boat = var_list[1]
    print(a)
    if a['idnumber'] in containers.keys():
        containers[a['idnumber']].append(a)
    else:
        containers[a['idnumber']] = [a]

    arr =  finbay

    db.child("users").child({"userEmail" : email}).child("Plans").child("Ships").child({"ShipID" : boat}).push(arr)
    ship = []
    for k in arr:
        ship.append([Bay(i+1, x) for i, x in enumerate(k)])
    name =  db.child("users").child({"userEmail" : email}).child("Containers").get()
    nameArr = name.val().values()["LoadAt"]["UnLoadAt"]
    return render_template('result.html', ship=ship, colors = colors, name = nameArr)

@app.route('/bayinput')
def bayinput():
    return render_template('bayinput.html')

@app.route('/containerdetails', methods=['GET','POST'])
def containerdetails():
    email = var_list[0]
    print(email)
    if request.method == 'POST':
        idnumber = int(request.form['idnumber'])
        Weight = int(request.form['Weight'])
        Size = int(request.form['Size'])
        loadat = int(request.form['loadat'])
        unloadat = int(request.form['unloadat'])
        sortedList.append(loadat)
        db.child("users").child({"userEmail" : email}).child("Containers").push({"ID" : idnumber, 
                                                                                  "Weight" : Weight,
                                                                                  "Size" : Size,
                                                                                  "LoadAt" : loadat,
                                                                                  "UnloadAt" : unloadat})
    return render_template('containerdetails.html')

@app.route('/history', methods=['GET', 'POST'])
def history():
    shipID = request.args.get("shipid")
    email = var_list[0]
    plan = db.child("users").child({"userEmail" : email}).child("Plans").child("Ships").child({"ShipID" : shipID}).get()
    arr = list(plan.val().values())[0]
    ship = []
    for k in arr:
        ship.append([Bay(i+1, x) for i, x in enumerate(k)])
    naam = ["Kandla to Mumbai", "Mumbai to Nhava Seva", "Nhava Seva to Marmagao", "Marmagao to Kochin"]
    return render_template('result.html', ship=ship, colors = colors, naam = naam)
    return render_template('history.html')

@app.route('/planhistory', methods=['GET', 'POST'])
def planhistory():
    return render_template('planhistory.html')


@app.route('/locationDetails', methods=['GET', 'POST'])
def locationDetails():
    email = var_list[0]
    print(email)
    boat = var_list[1]
    if request.method == 'POST':
        locations = int(request.form['locations'])
        for i in range(locations):
            loc = request.form[f'location{i}']
            db.child("users").child({"userEmail" : email}).child("Ships").child({"ShipID" : boat}).child("Locations").push(loc)
        return redirect("/containerdetails")
    return render_template('locationDetails.html')

if __name__ == "__main__":
    app.run(debug=True)


def get_ship():
    global baysList
    return eval(str(baysList))

def get_List():
    global sortedList
    return eval(str(sortedList))

weight = 0
finbay = []
finfav = -1000000
allPorts = []

terminalOutcome = []
totalTerminals = len(sortedList)
containerlist = []
term = 0
favourable=0
def Voyage(baysList,sortedList,Capacity): 
    global finbay,finfav,favourable,weight
    for xyz in range(100):
        weight = 0
        favourable=0
        bays = get_ship()
        sortedList = get_List()
        term = 0
        allPorts = []
        while term < len(sortedList):
            if term > 0 :
                unload(term,baysList,sortedList)
            randList = random.sample(range(0, len(sortedList[term])), len(sortedList[term]))
            a = 0
            i = 0
            nooOfTiers = len(baysList[i])-1
            while (nooOfTiers != -1):
                nooOfRows = len(bays[i][nooOfTiers])-1
                while(nooOfRows != -1):
                    if bays[i][nooOfTiers][nooOfRows] == True:
                        bays[i][nooOfTiers][nooOfRows] = str(sortedList[term][randList[a]])
                        weight += baysList[i][nooOfTiers][nooOfRows][2]
                        a += 1
                    nooOfRows -= 1
                i += 1
                if not CheckCapacity(weight,Capacity):
                    favourable -= 100000
                    break
                if i == len(baysList):
                    i = 0
                    nooOfTiers -= 1
                
            if not CheckCapacity(weight,Capacity):
                favourable -= 100000
                break
            allPorts.append(bays)
            print("----------")
            print(bays)
            print(allPorts)
            print("-----------")
            evaluation(bays)
            term += 1
        print(favourable)
        if finfav < favourable:
            finfav = favourable
            finbay = allPorts
    return allPorts
def evaluation(bays):
    global finbay,finfav,favourable
    a = 0
    i = 0
    nooOfTiers = len(baysList[i])-1
    while (nooOfTiers != 0):
        nooOfRows = len(baysList[i][nooOfTiers-1])-1
        while(nooOfRows != -1):
            if baysList[i][nooOfTiers][nooOfRows][1] < bays[i][nooOfTiers-1][nooOfRows][1]:
                favourable -= 2
            elif baysList[i][nooOfTiers][nooOfRows][1] == bays[i][nooOfTiers-1][nooOfRows][1]:
                favourable += 1
            elif baysList[i][nooOfTiers][nooOfRows][1] > baysList[i][nooOfTiers-1][nooOfRows][1]:
                favourable += 2
                a += 1
            nooOfRows -= 1
        i += 1
        if i == len(bays):
            i = 0
            nooOfTiers -= 1

def unload(term,bays,sortedList):
    a = 0
    i = 0
    global favourable,weight
    noTiers = len(baysList[i])-1
    nOfTiers = 0
    while (nOfTiers <= noTiers):
        noRows = len(baysList[i][noTiers])-1
        
        while(noRows >= 0):
            if baysList[i][nOfTiers][noRows][1] == str(term):
                weight -= baysList[i][nOfTiers][noRows][2]
                bays[i][nOfTiers][noRows] = True
               
                temp=0
                while(nOfTiers>=0):
                    if baysList[i][nOfTiers][noRows] == True:
                        nOfTiers-=1
                        temp+=1
                    else:
                        sortedList[term].append(baysList[i][nOfTiers][noRows])
                        weight -= baysList[i][nOfTiers][noRows][2]
                        baysList[i][nOfTiers][noRows] = True
                        favourable -= 2
                        nOfTiers-=1
                        temp+=1
                nOfTiers+=(temp)
                a += 1
            noRows -= 1
        i += 1
        if i == len(bays):
            i = 0
            nOfTiers += 1
    

def CheckCapacity(weight,Capacity):
    return weight <= Capacity

Voyage(baysList,sortedList,Capacity)