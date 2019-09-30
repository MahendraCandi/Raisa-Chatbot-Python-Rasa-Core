from datetime import datetime

import requests
from rasa_sdk import Action, Tracker
from typing import Any, Text, Dict, List
from rasa_sdk.executor import CollectingDispatcher


API_URL = "https://cricapi.com/api/"
API_KEY = "wd8FbQFHUrgI6yyaWlJivgST72q1"


class ActionHelloWorld(Action):
    def name(self) -> Text:
        return "action_hit_pertandingan"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        res = requests.get(API_URL + "matches?apikey=" + API_KEY)
        if res.status_code == 200:
            data = res.json()["matches"]
            recent_match = data[0]
            upcoming_match = data[1]
            upcoming_match["date"] = datetime.strptime(upcoming_match["date"], "%Y-%m-%dT%H:%M:%S.%fZ")
            next_date = upcoming_match["date"].strftime("%d %B %Y")

            out_message = f"Ini info mengenai pertandingan kriket.\n1. Pertandingan antara {recent_match['team-1']} dan" \
                f"{recent_match['team-2']} dimenangkan oleh {recent_match['winner_team']}"
            dispatcher.utter_message(out_message)

            out_message = f"2. Pertandingan selanjutnya antara {upcoming_match['team-1']} " \
                f"dengan {upcoming_match['team-2']} pada {next_date}"
            dispatcher.utter_message(out_message)
        return []
