from dotenv import load_dotenv
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import firestore

from models import User, Context
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

    ############################
    # Users
    ############################
    def add_user(self, user: User):
        self.db.collection("users").document(user.username).set({
            "username": user.username,
            "firstname": user.firstname if user.firstname else "name-not-set",
            "lastname": user.lastname if user.lastname else "",
            "id": user.id,
            "context": asdict(user.context)
        })
        user = self.get_user(user.username)
        return user

    def get_user(self, username: str) -> User or None:
        u = self.db.collection("users").document(username).get()
        if not u.exists:
            return None
        return from_dict(User, u.to_dict())

    def update_user(self, username: str, user: User):
        self.db.collection("users").document(username).update(asdict(user))

    ############################
    # Keys
    ############################
    def check_key_exists(self, username: str, key: str):
        keys = self.db.collection("keys").document(username).get()
        # No keys saved for this user yet
        if not keys.exists:
            return False
        if key in keys.to_dict():
            return True
        return False
        # return self.db.collection("keys").document(username).get().exists

    def add_key(self, username: str, key: str, value: str = ""):
        keys = self.db.collection("keys").document(username).get()
        # No keys saved for this user yet
        if not keys.exists:
            keys = {}
        else:
            keys = keys.to_dict()
        keys[key] = {
            "value": value
        }
        self.db.collection("keys").document(username).set(keys)
