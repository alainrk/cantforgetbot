import datetime
import hashlib
from dataclasses import asdict

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
    # TODO: async handling
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
    # TODO: async handling
    def check_key_exists(self, username: str, key: str):
        keys = self.db.collection("keys").document(username).get()
        # No keys saved for this user yet
        if not keys.exists:
            return False
        if key in keys.to_dict():
            return True
        return False
        # return self.db.collection("keys").document(username).get().exists

    # TODO: async handling
    def get_key(self, username: str, key: str) -> Key or None:
        keys = self.db.collection("keys").document(username).get()
        # No keys saved for this user yet
        if not keys.exists:
            return None
        if key in keys.to_dict():
            return from_dict(Key, keys.to_dict()[key])
        return None

    # TODO: async handling
    def add_key(self, user: User, key: str, value: str = ""):
        keys = self.db.collection("keys").document(user.username).get()
        # No keys saved for this user yet
        if not keys.exists:
            keys = {}
        else:
            keys = keys.to_dict()

        now = datetime.datetime.now()
        next_reminder_time = now + datetime.timedelta(seconds=60)

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

        # TODO: transaction management
        self.db.collection("keys").document(user.username).set(keys)
        self.create_reminder(key, user.id, user.username, next_reminder_time, value)

    # TODO: async handling
    def update_key(self, username: str, key: Key):
        k = self.db.collection("keys").document(username).get()
        if not k.exists:
            # TODO: raise exception and handle it
            return None
        keys = k.to_dict()
        keys[key.key] = asdict(key)
        self.db.collection("keys").document(username).set(keys)


    ############################
    # Reminders
    ############################

    # TODO: async handling
    # TODO: these params should not be here, a Reminder must be passed instead
    def create_reminder(self, key: str, chat_id: int, username: str, expire: datetime.datetime, value: str = ""):
        hash = hashlib.sha256(key.encode()).hexdigest()
        reminder_id = f"{username}-{hash}"

        self.db.collection("reminders").document(reminder_id).set({
            "id": reminder_id,
            "chat_id": chat_id,
            "username": username,
            "key": key,
            "value": value,
            "expire": expire
        })

    # TODO: async handling
    def get_expired_reminders(self):
        now = datetime.datetime.now()
        expired_rems = self.db.collection("reminders").where(
            "expire", "<=", now).get()
        return list(map(lambda k: from_dict(Reminder, k.to_dict()), expired_rems))

    # TODO: async handling
    def delete_reminder(self, id):
        self.db.collection("reminders").document(id).delete()
