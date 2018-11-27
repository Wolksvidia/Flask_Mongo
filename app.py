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
    user = users.find_one({'username':username})
    return user['tokens']

def verify_user(username,password):
    return True


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
    def get(self):
        pass
    

@app.route('/')
def hello_world():
    return "Hello World!"

api.add_resource(Register,'/register')
api.add_resource(Store,'/store')

if __name__=="__main__":
    app.run(host='0.0.0.0',debug=True)
