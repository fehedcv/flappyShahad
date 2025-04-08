from flask import Flask, send_from_directory, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__, static_folder='frontend', static_url_path='')

# Initialize Firebase
cred = credentials.Certificate('credentials.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Serve index.html
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

# Serve all other frontend assets
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# Get name from roll number
@app.route('/get-name')
def get_name():
    roll = request.args.get('roll')
    if not roll:
        return jsonify({'error': 'Roll required'}), 400
    doc = db.collection('students').document(roll).get()
    if doc.exists:
        return jsonify({'name': doc.to_dict()['name']})
    return jsonify({'error': 'Not found'}), 404

# Submit score
@app.route('/submit-score', methods=['POST'])
def submit_score():
    data = request.get_json()
    roll = data.get('roll')
    score = data.get('score')
    if not roll or score is None:
        return jsonify({'error': 'Roll and score required'}), 400

    ref = db.collection('scores').document(roll)
    existing = ref.get()
    if existing.exists and existing.to_dict()['score'] >= score:
        return jsonify({'message': 'Lower score ignored'})
    ref.set({'score': score})
    return jsonify({'message': 'Score submitted'})

# Leaderboard
@app.route('/leaderboard')
def leaderboard():
    top = db.collection('scores').order_by('score', direction=firestore.Query.DESCENDING).limit(10).stream()
    result = []
    for doc in top:
        roll = doc.id
        score = doc.to_dict()['score']
        name_doc = db.collection('students').document(roll).get()
        name = name_doc.to_dict().get('name', 'Unknown') if name_doc.exists else 'Unknown'
        result.append({'roll': roll, 'name': name, 'score': score})
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80)
