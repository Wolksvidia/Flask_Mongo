"""
Registration of a user - 0 token
Each user gets 10 tokens
Store a sentence on our DB for 1 token
Retrive his stored sentence on out DB for 1 token
"""
import bcrypt
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

#client = MongoClient("mongodb://root:root@192.168.64.158:27017/?authSource=test&authMechanism=SCRAM-SHA-1")
client = MongoClient(
    '192.168.64.158',
    port=27017,
    username='root',
    password='root',
    authSource='test',
    authMechanism='SCRAM-SHA-1'
    )

db = client.test #db
sentences = db['sentences'] #collection
users = db['users']


class Register(Resource):
    def post(self):
        data = request.get_json()

        username = data['username']
        password = data['password']

        hpw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        users.insert_one({'username':username, 'password':hpw, 'sentence':'','tokens':10})

        return {
            'status':200,
            'message':'User registered'
            }


def count_token(username):
    return users.find_one({'username':username})['tokens']

def verify_user(username,password):
    hash_pw = users.find_one({'username':username})['password']
    if bcrypt.hashpw(password.encode('utf-8'), hash_pw) == hash_pw:
        return True
    else:
        return False


class Store(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data['password']
        sentence = data['sentence']

        if not verify_user(username, password):
            return {
                'status':302,
                'message':'Wrong user or password'
                }

        ntoken = count_token(username)
        if ntoken <= 0:
            return {
                'status':301,
                'message':'You need more tokens'
                }

        users.update({'username':username},{'$set':{'sentence':sentence,'tokens':ntoken - 1}})
        return {
            'status':200,
            'message':'Sentence are stored'
            }   

    
class Retrive(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data['password']

        if not verify_user(username, password):
            return {
                'status':302,
                'message':'Wrong user or password'
                }

        ntoken = count_token(username)
        if ntoken <= 0:
            return {
                'status':301,
                'message':'You need more tokens'
                }
        users.update({'username':username},{'$set':{'tokens':ntoken - 1}})
        sentence = users.find_one({'username':username})['sentence']
        return {
            'status':200,
            'username': username,
            'sentence': sentence
            }

@app.route('/')
def hello_world():
    return '<h2>Hello World!</h2><br><p>Esta aplicacion intenta ser un juego, en la misma se usa Flask, Flask-Restful y MongoDB con pymongo</p> '

api.add_resource(Register,'/register')
api.add_resource(Store,'/store')
api.add_resource(Retrive, '/get')

if __name__=="__main__":
    app.run(host='0.0.0.0',debug=True)
