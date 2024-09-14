import pickleballbrackets_scraper as pbs
import pandas as pd
import googlemaps
import json
from Spinner import Spinner

api_key = 'AIzaSyBrPPVd_WgScTeSA66YRNYZkqu7HZE4kNk'


def __init__():
    global tourney_data
    global tourney_df
    global event_num

    tourney_data = read_tournament_data_file()

    tourney_df = pd.DataFrame(tourney_data)
    tourney_df = organize_df(tourney_df)

    event_num = len(tourney_df.index)

    coordinates = read_coordinates()
    tourney_df.insert(len(tourney_df.columns), "coordinates_lat", pd.Series(coordinates[0]))
    tourney_df.insert(len(tourney_df.columns), "coordinates_lng", pd.Series(coordinates[1]))



def organize_df(df):
    df['EventActivityFirstDate'] = df.apply(lambda x: '%s' % (x['EventActivityFirstDate'][:-11].strip()), axis=1)
    df['EventActivityLastDate'] = df.apply(lambda x: '%s' % (x['EventActivityLastDate'][:-11].strip()), axis=1)

    new_df = df[['Title', 'EventActivityFirstDate', 'EventActivityLastDate', 'LocationOfEvent_City', 'LocationOfEvent_StateTitle', 'LocationOfEvent_Zip', 'LocationOfEvent_StreetAddress', 'RegistrationCount_InAtLeastOneLiveEvent', 'RegistrationCount_NotInAtLeastOneLiveEvent', 'OnlineRegistration_Active', 'IsRegClosed', 'IsPrizeMoney', 'EventID', 'Logo',
                  'Sanction_PCO', 'Sanction_SSIPA', 'Sanction_USAPA', 'Sanction_WPF', 'Sanction_GPA', 'Sanction_PC', 'Sanction_LifeTime', 'Sanction_PAA', 'Sanction_PPA', 'Sanction_APP']].copy()
    
    new_df.rename(columns={
        'Title': 'title',
        'EventActivityFirstDate': 'start_date',
        'EventActivityLastDate': 'end_date',
        'LocationOfEvent_City': 'city',
        'LocationOfEvent_StateTitle': 'state',
        'LocationOfEvent_Zip': 'zipcode',
        'LocationOfEvent_StreetAddress': 'address',
        'IsRegClosed': 'registration_closed',
        'IsPrizeMoney': 'prize_money',
        'EventID': 'event_id',
        'Logo': 'image'
    }, inplace=True)

    new_df['address'] = new_df.apply(lambda x: '%s, %s, %s %s' % (x['address'], x['city'], x['state'], x['zipcode']), axis=1)
    new_df['image'] = new_df.apply(lambda x: 'https://pickleballbrackets.com/uploads/%s' % (x['image']), axis=1)
    new_df['link'] = new_df.loc[:, 'event_id']
    new_df['link'] = new_df.apply(lambda x: 'https://pickleballbrackets.com/ptd.aspx?eid=%s' % (x['link']), axis=1)
    new_df['registered_players'] = new_df.apply(lambda x: '%s' % (str(int(x['RegistrationCount_InAtLeastOneLiveEvent']) + int(x['RegistrationCount_NotInAtLeastOneLiveEvent']))), axis=1)

    sanction_df = new_df[['Sanction_PCO', 'Sanction_SSIPA', 'Sanction_USAPA', 'Sanction_WPF', 'Sanction_GPA', 'Sanction_PC', 'Sanction_LifeTime', 'Sanction_PAA', 'Sanction_PPA', 'Sanction_APP']]
    sanction_dict = sanction_df.apply(lambda x: x.to_dict(), axis=1)

    sanctioned = []
    s = False
    for i in sanction_dict:
        for x in i:
            if i[x] == True:
                s = True
        if s == True:
            sanctioned.append(True)
        else:
            sanctioned.append(False)
        s = False

    new_df.insert(len(new_df.columns), 'sanctioned', sanctioned)

    return new_df
        

def write_tournament_data_file(date_filter):
        data = []
        events = []
        pgnum = 1

        with Spinner(message='Loading Tournaments... '):
            while True:
                data.clear()
                data = pbs.get_tournament_data(str(pgnum), date_filter)

                if len(data) == 0:
                    break

                for i in range(len(data)):
                    events.append(data[i])
                
                pgnum += 1
        
        print("Tournaments found: " + str(len(events)))

        with Spinner(message='Writing Tournaments to File...'):
            filename = ('tournaments.json')

            with open(filename, 'w') as f:
                json.dump(events, f)

        print("Successfully updated tournament file.")


def read_tournament_data_file():
    with open('tournaments.json', 'rb') as f:
        events = json.load(f)
        return events


def get_coordinates(address):
    gmaps = googlemaps.Client(key=api_key)
    geocode_result = gmaps.geocode(address)
    if geocode_result:
        location = geocode_result[0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        return '0', '0'



def write_coordinates():
    global tourney_df
    locations = tourney_df.apply(lambda x: x.to_dict(), axis=1)

    address_lat = []
    address_lng = []

    with Spinner(message='Getting Coordinates...'):
        for l in locations:
            lat, lng = get_coordinates(l['address'])
            address_lat.append(lat)
            address_lng.append(lng)
            print(lat,lng)


    with Spinner(message='Writing Coordinates to File...'):
        with open('coordinates.txt', 'w') as f:
                json.dump([address_lat, address_lng], f)

    print('Coordinates written to file successfully')



def read_coordinates():
    with open('coordinates.txt', 'r') as f:
        data = json.load(f)
    return list(data)


def write_event_data():
    global tourney_df
    events = tourney_df.apply(lambda x: x.to_dict(), axis=1)

    with Spinner(message='Writing Event Data to File'):
        for e in events:
            with open(f'event_data/{e['event_id']}.txt', 'w') as f:
                json.dump(pbs.get_event_data(e['event_id']), f)
        
    print('Event data updated successfully')


def read_event_data(event_id):
    with open(f'event_data/{event_id}.txt', 'r') as f:
        data = json.load(f)
    return data