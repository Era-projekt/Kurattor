# seed_materials.py
"""Seed educational material files into Firebase Realtime Database.
Each entry represents a downloadable resource (PDF, PPT, VIDEO, DOC) for a specialty.
The script can be run locally with `python seed_materials.py`.
"""

import datetime
import random

# Initialize Firebase Admin (uses mock_firebase if real credentials missing)
try:
    from firebase_admin import initialize_app, credentials, db
    # Adjust the path to your Firebase credentials JSON if needed
    cred = credentials.Certificate('firebase_config.json')
    initialize_app(cred, {
        'databaseURL': 'https://your-project-id.firebaseio.com'
    })
except Exception as e:
    # Fallback to mock Firebase (for local development)
    from mock_firebase import MockFirebase
    mock = MockFirebase()
    db = mock.db

# List of specialties present in the system (extend as needed)
SPECIALTIES = [
    'IT',
    'Law',
    'Medicine',
    'Design',
    'Economics',
    'Psychology'
]

# Sample resource types and dummy URLs (replace with real storage URLs later)
RESOURCE_TYPES = ['pdf', 'ppt', 'vid', 'doc']
DUMMY_BASE_URL = 'https://example.com/materials'

def generate_dummy_name(specialty, idx, rtype):
    titles = {
        'pdf': f"{specialty} Lecture {idx+1}.pdf",
        'ppt': f"{specialty} Presentation {idx+1}.ppt",
        'vid': f"{specialty} Video {idx+1}.mp4",
        'doc': f"{specialty} Handbook {idx+1}.doc"
    }
    return titles.get(rtype, f"{specialty} Resource {idx+1}.{rtype}")

def seed_materials():
    ref = db.reference('files')
    existing = ref.get() or {}
    if existing:
        print('⚠️  Files node already contains data. Seed aborted to avoid duplicates.')
        return

    for specialty in SPECIALTIES:
        for i in range(3):  # three resources per specialty
            rtype = random.choice(RESOURCE_TYPES)
            name = generate_dummy_name(specialty, i, rtype)
            file_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(1000, 9999))
            url = f"{DUMMY_BASE_URL}/{specialty.lower()}/{name.replace(' ', '_')}"
            ref.child(file_id).set({
                'name': name,
                'url': url,
                'type': rtype,
                'date': datetime.date.today().isoformat(),
                'specialty': specialty
            })
            print(f'✅  Added {name} for {specialty}')

if __name__ == '__main__':
    seed_materials()
