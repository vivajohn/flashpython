import os
import json
import base64
from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app
from munch import Munch

# Initialize Flask app
app = Flask(__name__)

# Initialize Firestore DB
cred = credentials.Certificate('blazorapp1-50c53-firebase-adminsdk-ucwtd-69efb797ea.json')
default_app = initialize_app(cred)
db = firestore.client()

# Utility method for getting a document
def document(collName, docName):
  return db.collection(collName).document(docName)

@app.route('/')
def index():
  return "Audio Flashcards Ptyhon API"

# Get the user data structure
@app.route('/user/<uid>', methods=['GET'])
def user(uid):
  try:
      doc  = document('users', uid).get()
      if doc and doc.exists:
        return doc.to_dict(), 200
      else:
          return '', 200
  except Exception as e:
      return f"An Error occurred: {e}"

# Update or create a user
@app.route('/saveuser/<uid>', methods=['POST'])
def saveUser(uid):
  try:
    document('users', uid).set(json.loads(request.data))
    return "ok"
  except Exception as e:
      print("An error occurred: ", e)
      return f"An error occurred: {e}"

# For playback, get the list of active recordings (active means both prompt and
# response have been recorded)
@app.route('/currentpairs/<uid>/<currentTopicId>', methods=['GET'])
def currentPairs(uid, currentTopicId):
  try:
      query = db.collection('prpairs')\
        .where('uid', '==', uid)\
          .where('topicId', '==', int(currentTopicId))\
            .where('isActive', '==', True)\
              .order_by('nextDate')\
                .limit(20)
      docs  = query.get()
      list = []
      if docs:
        for doc in docs:
          list.append(doc.to_dict())
      return json.dumps(list) , 200
  except Exception as e:
      print("An error occurred: ", e)
      return f"An error occurred: {e}"

# Get a recording
@app.route('/blob/<uid>/<promptid>', methods=['GET'])
def blob(uid, promptid):
  try:
    key = f'{uid}_{promptid}'
    doc  = document('blobs', key).get()
    if doc and doc.exists:
      return doc.to_dict(), 200
    else:
        return 'error', 200
  except Exception as e:
      print("An error occurred: ", e)
      return f"An error occurred: {e}"

# Save a recording
@app.route('/saveblob/<uid>/<promptid>', methods=['POST'])
def saveblob(uid, promptid):
  try:
    blob = json.loads(request.data)
    key = f'{uid}_{promptid}'
    document('blobs', key).set(blob)
    return "ok"
  except Exception as e:
      print("An error occurred: ", e)
      return f"An error occurred: {e}"

# Delete a recording
@app.route('/deleteblob/<uid>/<promptid>', methods=['DELETE'])
def deleteBlob(uid, promptid):
  try:
    key = f'{uid}_{promptid}'
    document('blobs', key).delete()
    return "ok"
  except Exception as e:
      print("An error occurred: ", e)
      return f"An error occurred: {e}"

# Get the user's topic structure
@app.route('/gettopics/<uid>', methods=['GET'])
def getTopics(uid):
  try:
      docs = db.collection('topics').where('uid', '==', uid).get()
      list = []
      if docs:
        for doc in docs:
          list.append(doc.to_dict())
      return json.dumps(list) , 200
  except Exception as e:
      print("An error occurred: ", e)
      return f"An error occurred: {e}"

# Save the user's topic structure
@app.route('/savetopic/<uid>/<topicid>', methods=['POST'])
def saveTopic(uid, topicid):
  try:
    data = json.loads(request.data)
    key = f'{uid}_{topicid}'
    document('topics', key).set(data)
    return "ok"
  except Exception as e:
      print("An error occurred: ", e)
      return f"An error occurred: {e}"

# Get the prompt-reponse pairs for a deck      
@app.route('/getpairs/<uid>/<deckId>', methods=['GET'])
def getPairs(uid, deckId):
  try:
      query = db.collection('prpairs')\
        .where('uid', '==', uid)\
          .where('deckId', '==', int(deckId))\
            .order_by('order')
      docs  = query.get()
      list = []
      if docs:
        for doc in docs:
          list.append(doc.to_dict())
      return json.dumps(list) , 200
  except Exception as e:
      print("An error occurred: ", e)
      return f"An error occurred: {e}"

# Save a prompt-response pair
@app.route('/savepromptpair/<uid>/<pairid>', methods=['POST'])
def savepromptpair(uid, pairid):
  try:
    data = json.loads(request.data)
    key = f'{uid}_{pairid}'
    document('prpairs', key).set(data)
    return "ok"
  except Exception as e:
      print("An error occurred: ", e)
      return f"An error occurred: {e}"

# Delete a prompt-response pair
@app.route('/deletepair/<uid>/<pairid>', methods=['DELETE'])
def deletePair(uid, pairid):
  try:
    key = f'{uid}_{pairid}'
    document('prpairs', key).delete()
    return "ok"
  except Exception as e:
      print("An error occurred: ", e)
      return f"An error occurred: {e}"


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))