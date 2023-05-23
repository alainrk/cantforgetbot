from dotenv import load_dotenv
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import firestore

load_dotenv()

firebaseProjectKeyFilename = "firebase-service-account-key.json"
firebaseProjectId = os.getenv('FIREBASE_PROJECT_ID')

# Initialize Firebase Admin SDK
script_dir = os.path.dirname(os.path.realpath(__file__))
key_file_path = os.path.join(
    script_dir, "..", "data", firebaseProjectKeyFilename)
cred = credentials.Certificate(key_file_path)

firebase_admin.initialize_app(cred, {
    "databaseURL": f"https://{firebaseProjectId}.firebaseio.com"
})

# Write user json in the users firestore collection
db = firestore.client()
db.collection("users").document("alainrk").set({
    "firstname": "Alain",
    "lastname": "Kramar",
})

# Read data from the database
# data = ref.get()
# print(data)
