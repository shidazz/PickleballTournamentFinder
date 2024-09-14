import datamanager
from geopy.distance import geodesic


def search_by_range(usrinput, radius):
    tourney_df = datamanager.tourney_df
    
    target_lat, target_lng = datamanager.get_coordinates(usrinput)
    if target_lat is None or target_lng is None:
        print("Error: Couldn't find coordinates for the target address.")
        return []

    in_radius = []
    tourney_dict = tourney_df.apply(lambda x: x.to_dict(), axis=1)

    for t in tourney_dict:
        lat = t['coordinates_lat']
        lng = t['coordinates_lng']
        if lat is not None and lng is not None:
            distance = geodesic((target_lat, target_lng), (lat, lng)).miles
            if distance <= float(radius):
                in_radius.append(t['address'])

    if len(in_radius) > 0:
        locations = tourney_df[tourney_df['address'].isin(in_radius)]
        locations = locations.apply(lambda x: x.to_dict(), axis=1)
        return locations
    else:
        print('did not find any tournaments in that area.')
        return []