import json
import os
import uuid
import base64

DB_FILE = "local_db.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class MockReference:
    def __init__(self, path):
        self.path_parts = [p for p in path.split('/') if p]

    def _get_node(self, db_data, create=False):
        current = db_data
        for part in self.path_parts:
            if not isinstance(current, dict):
                return None
            if part not in current:
                if create:
                    current[part] = {}
                else:
                    return None
            current = current[part]
        return current

    def get(self, shallow=False):
        db_data = load_db()
        return self._get_node(db_data)

    def set(self, value):
        db_data = load_db()
        current = db_data
        if not self.path_parts:
            save_db(value)
            return
        for part in self.path_parts[:-1]:
            if part not in current or not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        current[self.path_parts[-1]] = value
        save_db(db_data)

    def update(self, value):
        db_data = load_db()
        current = db_data
        for part in self.path_parts[:-1]:
            if part not in current or not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        last_part = self.path_parts[-1]
        if last_part not in current or not isinstance(current[last_part], dict):
            current[last_part] = {}
        current[last_part].update(value)
        save_db(db_data)

    def delete(self):
        db_data = load_db()
        current = db_data
        for part in self.path_parts[:-1]:
            if part not in current or not isinstance(current[part], dict):
                return
            current = current[part]
        if self.path_parts and isinstance(current, dict):
            current.pop(self.path_parts[-1], None)
        save_db(db_data)

    def push(self, value=None):
        new_key = "push_" + str(uuid.uuid4()).replace('-', '')[:12]
        child_path = '/'.join(self.path_parts + [new_key])
        child_ref = MockReference(child_path)
        if value is not None:
            child_ref.set(value)
        return child_ref

    def order_by_key(self):
        return self

    def limit_to_last(self, n):
        return self

class MockUser:
    def __init__(self, uid, email, display_name):
        self.uid = uid
        self.email = email
        self.display_name = display_name

def verify_id_token(id_token):
    try:
        parts = id_token.split('.')
        if len(parts) >= 2:
            payload_b64 = parts[1]
            payload_b64 += '=' * (4 - len(payload_b64) % 4)
            payload_json = base64.b64decode(payload_b64).decode('utf-8')
            payload = json.loads(payload_json)
            if 'uid' in payload:
                return payload
        return {"uid": id_token, "email": f"{id_token}@mock.com"}
    except Exception as e:
        print("Mock verify_id_token fallback:", e)
        return {"uid": id_token, "email": f"{id_token}@mock.com"}

def create_user(email, password=None, display_name=None, uid=None):
    if not uid:
        uid = "mock_uid_" + email.replace('@', '_').replace('.', '_')
    return MockUser(uid, email, display_name)

def get_user_by_email(email):
    db_data = load_db()
    users = db_data.get('users', {})
    for uid, udata in users.items():
        if udata.get('email') == email:
            return MockUser(uid, email, udata.get('name'))
    raise Exception("user-not-found")

class MockDBModule:
    @staticmethod
    def reference(path='/'):
        return MockReference(path)

class MockAuthModule:
    @staticmethod
    def verify_id_token(id_token):
        return verify_id_token(id_token)

    @staticmethod
    def create_user(email, password=None, display_name=None, uid=None):
        return create_user(email, password, display_name, uid)

    @staticmethod
    def get_user_by_email(email):
        return get_user_by_email(email)

def patch_firebase_admin():
    import sys
    import types
    
    # Create mock modules
    mock_db = types.ModuleType("firebase_admin.db")
    mock_db.reference = MockDBModule.reference
    
    mock_auth = types.ModuleType("firebase_admin.auth")
    mock_auth.verify_id_token = MockAuthModule.verify_id_token
    mock_auth.create_user = MockAuthModule.create_user
    mock_auth.get_user_by_email = MockAuthModule.get_user_by_email
    
    mock_admin = types.ModuleType("firebase_admin")
    mock_admin.initialize_app = lambda *args, **kwargs: None
    mock_admin.db = mock_db
    mock_admin.auth = mock_auth
    
    # Inject into sys.modules
    sys.modules["firebase_admin"] = mock_admin
    sys.modules["firebase_admin.db"] = mock_db
    sys.modules["firebase_admin.auth"] = mock_auth
    print("[MOCK FIREBASE] Successfully patched firebase_admin modules.")
