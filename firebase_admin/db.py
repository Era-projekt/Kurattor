import sys
import os
# Add parent dir to sys.path so we can import mock_firebase
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mock_firebase

def reference(path='/'):
    return mock_firebase.MockDBModule.reference(path)
