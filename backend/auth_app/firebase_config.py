# firebase_config.py

import firebase_admin
from firebase_admin import credentials, auth

# ✅ Only initialize if no apps are initialized
if not firebase_admin._apps:
    cred = credentials.Certificate('firebase_credentials.json')
    firebase_app = firebase_admin.initialize_app(cred)
else:
    firebase_app = firebase_admin.get_app()

# ✅ You can now use `auth` anywhere by importing from this file.
