from dotenv import load_dotenv
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import firestore

from models import User
from dataclasses import asdict
from dacite import from_dict

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

    def add_user(self, username: str, id: int, firstname: str, lastname: str):
        self.db.collection("users").document(username).set({
            "username": username,
            "firstname": firstname if firstname else "name-not-set",
            "lastname": lastname if lastname else "",
            "id": id,
            "context": {}
        })
        user = self.get_user(username)
        return user

    def get_user(self, username: str) -> User or None:
        u = self.db.collection("users").document(username).get()
        if not u.exists:
            return None
        return from_dict(User, u.to_dict())

    def update_user(self, username: str, user: User):
        self.db.collection("users").document(username).update(asdict(user))
