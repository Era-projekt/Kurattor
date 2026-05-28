import sys
import os
# Add parent dir to sys.path so we can import mock_firebase
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mock_firebase

def verify_id_token(id_token):
    return mock_firebase.MockAuthModule.verify_id_token(id_token)

def create_user(email, password=None, display_name=None, uid=None):
    return mock_firebase.MockAuthModule.create_user(email, password, display_name, uid)

def get_user_by_email(email):
    return mock_firebase.MockAuthModule.get_user_by_email(email)
