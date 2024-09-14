import pandas as pd
import datamanager


def search_by_skill(in_radius, skill):
    if str(skill).upper() == 'ANY':
        return in_radius
    
    tourney_df = datamanager.tourney_df

    events_in_radius = []
    for t in in_radius:
        events_in_radius.append(t['event_id'])

    tourney_df = tourney_df[tourney_df['event_id'].isin(events_in_radius)]
    tourney_dict = tourney_df.apply(lambda x: x.to_dict(), axis=1)
    
    within_skill_level = []

    for t in tourney_dict:
        event_data = datamanager.read_event_data(t['event_id'])
        if str(skill).upper() in str(event_data).upper():
            within_skill_level.append(t['event_id'])
    
    if len(within_skill_level) > 0:
        events = tourney_df[tourney_df['event_id'].isin(within_skill_level)]
        events = events.apply(lambda x: x.to_dict(), axis=1)
        return events
    else:
        print('Did not find any tournaments with that skill level.')
        return []
    