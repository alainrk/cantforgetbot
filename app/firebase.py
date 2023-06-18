import hashlib
from dataclasses import asdict
from datetime import datetime, timedelta

import firebase_admin
from dacite import from_dict
from dotenv import load_dotenv
from firebase_admin import credentials, firestore
from models import Key, Reminder, User

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

    def add_key(self, user: User, key: str, value: str = ""):
        keys = self.db.collection("keys").document(user.username).get()
        # No keys saved for this user yet
        if not keys.exists:
            keys = {}
        else:
            keys = keys.to_dict()

        now = datetime.now()
        next_reminder_time = now + timedelta(seconds=60)

        # TODO: This stuff has to be moved outside and passed here as model Key
        keys[key] = {
            "key": key,
            "value": value,
            "created_at": now,
            "updated_at": now,
            "reminders": 0,
            "reminders_failed": 0,
            "reminders_succeded": 0,
            "next_reminder": next_reminder_time
        }

        # TODO: Create reminder collection
        # Each reminder will have a document with all the references to user and key.
        # There will be a routine to get the expired reminders and send them to the user.
        # The reminder will be deleted after it is sent to the user.
        # The key will be updated with the next reminder date and the next reminder date will be set in its collection.

        self.db.collection("keys").document(user.username).set(keys)

        hash = hashlib.sha256(key.encode()).hexdigest()
        reminder_id = f"{user.username}-{hash}"

        self.db.collection("reminders").document(reminder_id).set({
            "id": reminder_id,
            "chat_id": user.id,
            "username": user.username,
            "key": key,
            "value": value,
            "expire": next_reminder_time
        })

    def get_expired_reminders(self):
        now = datetime.now()
        expired_rems = self.db.collection("reminders").where(
            "expire", "<=", now).get()
        return list(map(lambda k: from_dict(Reminder, k.to_dict()), expired_rems))