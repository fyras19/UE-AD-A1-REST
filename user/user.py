import json

import requests
from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

PORT = 3203
HOST = '0.0.0.0'

with open('{}/databases/users.json'.format("."), "r") as jsf:
    users = json.load(jsf)["users"]


###### Users part ##########

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
            return make_response(jsonify(user), 200)
    return make_response(jsonify({"error": "User ID not found"}), 400)


@app.route("/users/<userid>", methods=['POST'])
def add_user(userid):
    req = request.get_json()
    for user in users:
        if str(user["id"]) == str(userid):
            return make_response(jsonify({"error": "User already exists"}), 409)
    users.append(req)
    res = make_response(jsonify(req), 200)
    return res


###### Bookings part ##########

@app.route("/bookings/<userid>", methods=['GET'])
def get_booking_for_user(userid):
    response = requests.get(f"http://booking:3201/bookings/{userid}")
    return make_response(response.json(), response.status_code)


@app.route("/bookings/<userid>", methods=['POST'])
def add_booking_byuser(userid):
    req = request.get_json()
    response = requests.post(f"http://booking:3201/bookings/{userid}", json=req)
    return make_response(response.json(), response.status_code)


@app.route("/<userid>/movies", methods=['GET'])
def get_movies_for_user(userid):
    bookings_by_user = requests.get(f"http://booking:3201/bookings/{userid}")
    movies_ids = set()
    if bookings_by_user.status_code == 200:
        bookings_data = bookings_by_user.json()
        for date_data in bookings_data["dates"]:
            for movie in date_data["movies"]:
                movies_ids.add(movie)
        movies = []
        for movie_id in movies_ids:
            movie_request = requests.get(f"http://movie:3200/movies/{movie_id}")
            if movie_request.status_code == 200:
                movies.append(movie_request.json())
        return make_response(jsonify({"movies": movies}), 200)
    else:
        return make_response(jsonify({"error": "No bookings found for this user"}), 400)


@app.route("/movies", methods=['GET'])
def get_movies():
    response = requests.get(f"http://movie:3200/json")
    return make_response(response.json(), response.status_code)


@app.route("/movies/<movieid>", methods=['GET'])
def get_movie_byid(movieid):
    response = requests.get(f"http://movie:3200/movies/{movieid}")
    return make_response(response.json(), response.status_code)


@app.route("/titles", methods=['GET'])
def get_movie_bytitle():
    title = request.args.get('title')
    response = requests.get(f"http://movie:3200/titles", params={'title': title})
    return make_response(response.json(), response.status_code)


@app.route("/movies/<movieid>", methods=['POST'])
def create_movie(movieid):
    req = request.get_json()
    response = requests.post(f"http://movie:3200/movies/{movieid}", json=req)
    return make_response(response.json(), response.status_code)


@app.route("/movies/<movieid>", methods=['DELETE'])
def del_movie(movieid):
    response = requests.delete(f"http://movie:3200/movies/{movieid}")
    return make_response(response.json(), response.status_code)


@app.route("/movies/<movieid>/<rate>", methods=['PUT'])
def update_movie_rating(movieid, rate):
    response = requests.put(f"http://movie:3200/movies/{movieid}/{rate}")
    return make_response(response.json(), response.status_code)


###### Run App ##########

if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT, debug=True)
