import requests
from rasa_sdk import Action, Tracker
from typing import Any, Text, Dict, List, Optional
from rasa_sdk.executor import CollectingDispatcher


class ActionSlotReset(Action):
    def name(self):  # type: () -> Text
        return 'action_reset'

    def run(
        self,
        dispatcher,  # type: CollectingDispatcher
        tracker,  # type: Tracker
        domain,  # type:  Dict[Text, Any]
    ):  # type: (...) -> List[Dict[Text, Any]]
        slot_return = []
        slot_set = {}
        for slot in tracker.slots:
            if (slot != 'customer_name') or (slot != 'bot_name'):
                slot_set[slot] = None
                slot_return.append(slot_set)
        return slot_return
