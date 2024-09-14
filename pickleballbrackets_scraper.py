import requests

base_url = "https://pickleballbrackets.com"
base_url_2 = "https://pickleballtournaments.com"

pgnum = "1"

eventID = ""
activityID = ""
activitySplitID = ""

showPlayersRequest = {
    "EventID":eventID,
    "ActivityID":activityID,
    "ActivitySplitID":activitySplitID,
    "Rating_1stChoice":"00000000-0000-0000-0000-000000000001",
    "pg":"ptplg",
    "ReturnType":"json"
}


with requests.Session() as s:

    def login(email):
        login = {
        "_EVENTTARGET": "ctl00$cphBody$lbtnLogin",
        "ctl00$cphBody$login": email,
        }

        s.post(f"{base_url}/lrfc_l.aspx", data=login)

    def password(email, pswrd):
        password = {
        "_EVENTTARGET": "ctl00$cphBody$lbtnLogin",
        "ct100$cphBody$htbxSignInEmail": email,
        "ctl00$cphBody$Password": pswrd
        }

        s.post(f"{base_url}/lrfc_p.aspx?", data=password)


    def get_tournament_data(pageCounter, date_filter):
        tourneyRequest = {
        "ReturnType":"json",
        "EventTypeIDs":"1",
        "ClubID":"",
        "CountryID":"",
        "StateIDs":"",
        "SportIDs":"dc1894c6-7e85-43bc-bfa2-3993b0dd630f",
        "PlayerGroupIDs":""
        ,"FormatIDs":"",
        "AgeIDs":"",
        "RankIDs":"",
        "DateFilter":date_filter,
        "FromDate":"",
        "ToDate":"",
        "ShowOnCalendar":"0",
        "IncludeTestEvents":"0",
        "SearchWord":"",
        "PrizeMoney":"All",
        "PageNumber":pageCounter,
        "PageSize":50,
        "OrderBy":"EventActivityFirstDate",
        "OrderDirection":"Asc",
        "Alpha":"All",
        "prt":""
        }

        r = s.post(f"{base_url}/Json.asmx/EventsSearch_PublicUI", json=tourneyRequest)
        return r.json().get('d')


    def get_event_data(event_id):
        event_request = {
            "tourneyId": event_id
        }

        r = s.get(f'{base_url_2}/api/tourneys/getFormattedEvents?tourneyId={event_id}&activityId=&playerName=', json=event_request)
        return r.json()