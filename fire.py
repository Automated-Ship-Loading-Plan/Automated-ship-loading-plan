import pyrebase
from flask import jsonify

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

user = jsonify(db.child("users").get().val())
print(user.values())