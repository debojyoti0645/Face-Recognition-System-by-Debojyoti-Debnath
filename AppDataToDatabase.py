import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-recognition-2cb6c-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "321654":
        {
            "name": "Barack Obama",
            "ID": 9865,
            "Address": "USA",
            "Age": 55,
            "Gender": "Male"
        },
    "6519":
        {
            "name": "Debojyoti Debnath",
            "ID": 1645,
            "Address": "India",
            "Age": 19,
            "Gender": "Male"
        },
    "654321":
        {
            "name": "Narendra Modi",
            "ID": 1235,
            "Address": "India",
            "Age": 65,
            "Gender": "Male"
        },
    "987654":
        {
            "name": "Tom Cruise",
            "ID": 1007,
            "Address": "America",
            "Age": 61,
            "Gender": "Male"
        }
}

for key,value in data.items():
    ref.child(key).set(value)


