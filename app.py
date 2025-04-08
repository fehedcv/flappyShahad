from flask import Flask, request, jsonify, send_from_directory
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import json
import os

app = Flask(__name__, static_folder='.')

# 🔐 Get the base64-encoded creds from environment variable
firebase_creds_b64 = os.getenv("FIREBASE_CREDS_BASE64")
if not firebase_creds_b64:
    raise Exception("Missing FIREBASE_CREDS_BASE64 environment variable")

# Decode and initialize Firebase
creds_dict = json.loads(base64.b64decode(firebase_creds_b64).decode())
cred = credentials.Certificate(creds_dict)
firebase_admin.initialize_app(cred)
db = firestore.client()

# 🧑‍🎓 Roll number to name mapping
students = [
    "Aadinath", "Abhimanyu", "Abhinav krishna", "Abhishek KB", "Abinav A", "Adhil Chandra",
    "Adithya narayanan", "Akshay", "Aleena fathima", "Aman pasha", "Anandakrishnan",
    "Anaswara CV", "Anusree", "Ardra", "Asif kamal", "Aswin Das", "Aswin M", "Athul krishna",
    "Danish ahmed", "Dilshad OK", "Fahad mohammed kabeer", "Fathima Hiba KM", "Fathima Minha",
    "Fathima Thehsina", "Fidha P", "Gopika", "Harikrishnan", "Hemanth", "Hiba A", "Hikka",
    "Krishnapriya", "Lamisha", "Mohammed Javad", "Mohammed Sabith", "Mohammed Abile",
    "Mohammed Yahfin", "Mruduldev", "Mohammed Diyan", "Mohammed Anas", "Mohammed Hisham",
    "Mohammed Hisham AK", "Mohammed Minhaj", "Mohammed Shahad", "Mohammed Shinadh",
    "Mohammed Swalih", "Mohammed Thamim", "Muhsina", "Nurul Ameen", "Praveen MT", "Ridhwan",
    "Rilwan", "Rinsha", "Risham Mohammed", "Shifana", "Shimna Jasmin", "Sudeep", "Suhair",
    "Thazmeen", "Visal", "Vishnu", "Vivek", "Yazeed"
]

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/get-name')
def get_name():
    roll = request.args.get('roll', '')
    if not roll.isdigit() or not (1 <= int(roll) <= len(students)):
        return jsonify({'error': 'Invalid roll number'})
    return jsonify({'name': students[int(roll) - 1]})

@app.route('/submit-score', methods=['POST'])
def submit_score():
    data = request.get_json()
    roll = str(data.get('roll', ''))
    score = int(data.get('score', 0))
    name = students[int(roll) - 1] if roll.isdigit() and 1 <= int(roll) <= len(students) else "Unknown"

    doc_ref = db.collection('flappy_scores').document(roll)
    existing = doc_ref.get()
    if existing.exists:
        if score > existing.to_dict().get('score', 0):
            doc_ref.set({'score': score, 'name': name, 'roll': roll})
    else:
        doc_ref.set({'score': score, 'name': name, 'roll': roll})
    return jsonify({'success': True})

@app.route('/leaderboard')
def leaderboard():
    docs = db.collection('flappy_scores').order_by('score', direction=firestore.Query.DESCENDING).limit(10).stream()
    leaderboard = [doc.to_dict() for doc in docs]
    return jsonify(leaderboard)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
