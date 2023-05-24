from dotenv import load_dotenv
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import firestore

load_dotenv()


class DatabaseConfig:
    def __init__(self, key_file_path: str):
        self.key_file_path = key_file_path


class Database:
    def __init__(self, config: DatabaseConfig):
        self.config = config

        cred = credentials.Certificate(self.config.key_file_path)

        firebase_admin.initialize_app(cred, {
            "databaseURL": f"https://{cred.project_id}.firebaseio.com"
        })

        # Write user json in the users firestore collection
        self.db = firestore.client()

    def test(self, msg: str):
        self.db.collection("users").document("alainrk").set({
            "firstname": "Alain",
            "lastname": "Test",
            "msg": msg
        })
