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
def get_booking_byuserid(userid):
   for booking in bookings:
      if str(booking["userid"]) == str(userid):
         res = make_response(jsonify(booking),200)
         return res
   return make_response(jsonify({"error":"User ID not found"}),400)

@app.route("/bookings/<userid>", methods=['POST'])
def add_booking(userid):
   req = request.get_json()
   date,movieid = req["date"], req["movieid"]
   booking_response = requests.get(f"http://{HOST}:{PORT}/bookings/{userid}")
   if booking_response.status_code == 200:
    # Parse the response content as JSON
      booking_data = booking_response.json()       
   booking_dates = booking_data["dates"]
   for booking_date in booking_dates:
      if booking_date["date"]==date and movieid in booking_date["movies"]:
         return make_response(jsonify({"error":"The booking was already made"}),409)
   showtime = requests.get(f"http://{HOST}:3202/showmovies/{date}")
   if showtime.status_code == 200:
      showtime_data = showtime.json()
      if movieid in showtime_data["movies"]:
         
         for booking in bookings:
            if booking["userid"]==str(userid):
               
               for date_user in booking["dates"]:
                  if date_user["date"]==str(date):
                     
                     date_user["movies"].append(movieid)

                     return make_response(jsonify(booking),200)
               booking["dates"].append({"date":date,"movies":[movieid]})
               return make_response(jsonify(booking),200)

         
   return make_response(jsonify({"error":"The movie isn't scheduled on the indicated date"}),400)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT, debug=True)
