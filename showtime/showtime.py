from flask import Flask, render_template, request, jsonify, make_response
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3202
HOST = '0.0.0.0'

with open('{}/databases/times.json'.format("."), "r") as jsf:
   schedule = json.load(jsf)["schedule"]

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Showtime service!</h1>"

@app.route("/showtimes", methods=['GET'])
def showtimes():
   return make_response(jsonify({"schedule": schedule}))

@app.route("/showmovies/<date>", methods=['GET'])
def showmoviesByDate(date):
   for day in schedule:
      if day["date"] == date:
         return make_response(jsonify(day))
   return make_response(jsonify({"error": "Date not found!"}))

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT, debug=True)
