from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'

with open('{}/databases/bookings.json'.format("."), "r") as jsf:
   bookings = json.load(jsf)["bookings"]

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"


@app.route("/bookings", methods=['GET'])
def get_json():
   return make_response(jsonify({"bookings": bookings}), 200)

@app.route("/bookings/<userid>", methods=['GET'])
def get_booking_for_user(userid):
   for booking in bookings:
      if str(booking["userid"]) == str(userid):
         res = make_response(jsonify(booking),200)
         return res
   return make_response(jsonify({"error":"This user doesn't have any bookings yet"}),400)


@app.route("/bookings/<userid>", methods=['POST'])
def add_booking_byuser(userid):
    req = request.get_json()
    date, movieid = req["date"], req["movieid"]

    # Check if the movie is scheduled for the given date
    showtime = requests.get(f"http://showtime:3202/showmovies/{date}")
    if showtime.status_code == 200:
        showtime_data = showtime.json()
        if movieid not in showtime_data["movies"]:
            return make_response(jsonify({"error": "The movie isn't scheduled on the indicated date"}), 400)
    else: return make_response(jsonify({"error": "The movie isn't scheduled on the indicated date"}), 400)
    booking_response = requests.get(f"http://localhost:{PORT}/bookings/{userid}")
    if booking_response.status_code != 200: 
    # Find the user's booking or create one if it doesn't exist
        user_booking = {"userid": str(userid), "dates": [{"date": date, "movies": [movieid]}]}
        bookings.append(user_booking)
        return make_response(jsonify(user_booking), 200)
    
    user_booking = booking_response.json() 
    # Check if the booking already exists
    for date_user in user_booking["dates"]:
        if date_user["date"] == date:
            if movieid in date_user["movies"]:
                return make_response(jsonify({"error": "The booking was already made"}), 409)
            date_user["movies"].append(movieid)
            return make_response(jsonify(user_booking), 200)

    # If the booking doesn't exist for the date, create a new one
    user_booking["dates"].append({"date": date, "movies": [movieid]})

    return make_response(jsonify(user_booking), 200)


if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT, debug=True)
