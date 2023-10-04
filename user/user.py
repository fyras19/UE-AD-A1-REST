from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3203
HOST = '0.0.0.0'

with open('{}/databases/users.json'.format("."), "r") as jsf:
   users = json.load(jsf)["users"]

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the User service!</h1>"

@app.route("/users", methods=['GET'])
def get_json():
   return make_response(jsonify({"users": users}), 200)

@app.route("/users/<userid>", methods=['GET'])
def get_user_byid(userid):
    for user in users:
        if str(user["id"]) == str(userid):
            return make_response(jsonify(user),200)
    return make_response(jsonify({"error":"User ID not found"}),400)

@app.route("/bookings/<userid>", methods=['GET'])
def get_booking_for_user(userid):
   response = requests.get(f"http://{HOST}:3201/bookings/{userid}")
   return make_response(response.json(), response.status_code)

@app.route("/movies", methods=['GET'])
def get_movies():
   response = requests.get(f"http://{HOST}:3200/json")
   return make_response(response.json(), response.status_code)

@app.route("/users/<userid>", methods=['POST'])
def add_user(userid):
   req = request.get_json()
   for user in users:
      if str(user["id"]) == str(userid):
            return make_response(jsonify({"error":"User already exists"}),409)
   users.append(req)
   res = make_response(jsonify(req),200)
   return res

@app.route("/bookings/<userid>", methods=['POST'])
def add_booking_byuser(userid):
   req = request.get_json()
   response = requests.post(f"http://{HOST}:3201/bookings/{userid}",json=req)
   return make_response(response.json(), response.status_code)



if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT, debug=True)
