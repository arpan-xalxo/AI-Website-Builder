from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app

# User model helper
class User:
    def __init__(self, email, password, role_id):
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.role_id = role_id

    def save(self, mongo):
        user = {
            'email': self.email,
            'password_hash': self.password_hash,
            'role_id': self.role_id
        }
        return mongo.db.users.insert_one(user)

    @staticmethod
    def find_by_email(mongo, email):
        return mongo.db.users.find_one({'email': email})

    @staticmethod
    def check_password(stored_hash, password):
        return check_password_hash(stored_hash, password)

# Role model helper
class Role:
    def __init__(self, name, permissions):
        self.name = name
        self.permissions = permissions  

    def save(self, mongo):
        role = {
            'name': self.name,
            'permissions': self.permissions
        }
        return mongo.db.roles.insert_one(role)

    @staticmethod
    def find_by_name(mongo, name):
        return mongo.db.roles.find_one({'name': name})

# Website model helper
class Website:
    def __init__(self, owner_id, data):
        self.owner_id = owner_id
        self.data = data  

    def save(self, mongo):
        from bson.objectid import ObjectId
        website = {
            'owner_id': ObjectId(self.owner_id),
            'data': self.data
        }
        return mongo.db.websites.insert_one(website)

    @staticmethod
    def find_by_id(mongo, website_id):
        from bson.objectid import ObjectId
        return mongo.db.websites.find_one({'_id': ObjectId(website_id)}) 