from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_apscheduler import APScheduler
import googlemaps
import datamanager
import searchbyrange
import searchbyskill
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# Initialize Google Maps API client
api_key = 'AIzaSyDWe67VvbE-aTyPUm8oOun87Xg1-KmezFU'
gmaps = googlemaps.Client(key=api_key)

@app.route('/')
def index():
    return app.send_static_file('index.html')


@scheduler.task('date', id='background')
def background_processes():
    datamanager.__init__()

@scheduler.task('cron', id='update_data', hour='23')
def update_data():
    datamanager.write_tournament_data_file("Future")
    datamanager.write_coordinates()
    datamanager.write_event_data()
    


@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    zipcode = data.get('zipcode')
    distance = data.get('distance')
    start_date = data.get('startDate', datetime.now())
    end_date = data.get('endDate', (datetime.now() + timedelta(days=365)))
    sanctioned_only = data.get('sanctioned')
    selected_skill = data.get('skillLevel')

    within_range = searchbyrange.search_by_range(zipcode, distance)
    places = searchbyskill.search_by_skill(within_range, selected_skill)

    locations = []
    for place in places:
        tourney_date = datetime.strptime(place['start_date'], f"%m/%d/%Y")

        if place['registration_closed'] == 0 and datetime.strptime(start_date, "%Y-%m-%d") <= tourney_date <= datetime.strptime(end_date, "%Y-%m-%d"):
            allowed = True
            if sanctioned_only:
                if place['sanctioned']:
                    allowed = True
                else:
                    allowed = False
            
            if allowed:
                locations.append({
                    'title': place['title'],
                    'address': place['address'],
                    'image': place['image'],
                    'coordinates': {
                        'lat': place['coordinates_lat'],
                        'lng': place['coordinates_lng']
                    },
                    'link': place['link'],
                    'date': place['start_date'] + ' to ' + place['end_date'],
                    'registered_players': place['registered_players'],
                    'registration_closed': place['registration_closed']
                })

    return jsonify({'locations': locations})

if __name__ == '__main__':
    app.run(debug=True) 