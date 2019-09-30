from rasa_sdk import Tracker
from rasa_sdk.forms import FormAction
from typing import Any, Text, Dict, List, Optional
from rasa_sdk.executor import CollectingDispatcher


class RestaurantForm(FormAction):
    def name(self):  # type: () -> Text
        return "restoran_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["cuisine", "num_people", "outdoor_seating", "preferences", "feedback"]

    def slot_mappings(self):
        _dict = {"cuisine": self.from_entity(entity="cuisine", not_intent="chitchat"),
                 "num_people": [
                     self.from_entity(entity="num_people", intent=["inform", "request_restaurant"]),
                     self.from_entity(entity="number")],
                 "outdoor_seating": [
                     self.from_entity(entity="seating"),
                     self.from_intent(intent='affirm', value=True),
                     self.from_intent(intent='deny', value=False)],
                 "preferences": [
                     self.from_intent(intent='deny', value="no additional preferences"),
                     self.from_text(not_intent="affirm")],
                 "feedback": [
                     self.from_entity(entity="feedback"),
                     self.from_text()]}
        return _dict

    @staticmethod
    def cuisine_db() -> List[Text]:
        _dict = ["padang", "cina", "perancis", "indonesia", "india", "arab"]
        return _dict

    @staticmethod
    def _is_int(string: Text) -> bool:
        try:
            int(string)
            return True
        except ValueError:
            return False

    def _validate_cuisine(self,
                          value: Text,
                          dispatcher: CollectingDispatcher,
                          tracker: Tracker,
                          domain: Dict[Text, Any]) -> Optional[Text]:
        if value.lower() in self.cuisine_db():
            return value
        else:
            dispatcher.utter_template("utter_wrong_cuisine", tracker)
            return None

    def _validate_num_people(self,
                             value: Text,
                             dispatcher: CollectingDispatcher,
                             tracker: Tracker,
                             domain: Dict[Text, Any]) -> Optional[Text]:
        if self._is_int(value) and value > 0:
            return value
        else:
            dispatcher.utter_template("utter_wrong_num_people", tracker)
            return None

    @staticmethod
    def _validate_outdoor_seating(self,
                                  value: Text,
                                  dispatcher: CollectingDispatcher,
                                  tracker: Tracker,
                                  domain: Dict[Text, Any]) -> Any:
        if isinstance(value, str):
            if 'luar' or 'out' in value:
                return True
            elif 'dalam' or 'in' in value:
                return False
            else:
                dispatcher.utter_template('utter_wrong_outdoor_seating', tracker)
                return None
        else:
            return value

    def submit(self,
               dispatcher,
               tracker,
               domain):  # type: (CollectingDispatcher, Tracker, Dict[Text, Any]) -> List[Dict]
        dispatcher.utter_template('utter_submit', tracker)
        return []
