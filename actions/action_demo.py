import random
from typing import Text, List, Dict


from rasa_sdk import Action
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any


class Demo(Action):
    def name(self) -> Text:
        return 'action.show_quick_reply'

    def run(
        self,
        dispatcher,  # type: CollectingDispatcher
        tracker,  # type: Tracker
        domain,  # type:  Dict[Text, Any]
    ):  # type: (...) -> List[Dict[Text, Any]]
        bot_name = tracker.get_slot('bot_name')
        if tracker.get_latest_input_channel() == 'facebook':
            message = {
                "text": f"{bot_name} punya beberapa menu pilihan, silakan dicoba salah satu ya",
                "quick_replies": [
                    {
                        "content_type": "text",
                        "image_url": "https://i.ibb.co/5G023yb/eunha.jpg",
                        "title": "link attachment",
                        "payload": "link attachment"
                    },
                    {
                        "content_type": "text",
                        "image_url": "https://i.ibb.co/5G023yb/eunha.jpg",
                        "title": "octocat",
                        "payload": "octocat"
                    },
                    {
                        "content_type": "text",
                        "image_url": "https://i.ibb.co/5G023yb/eunha.jpg",
                        "title": "monyet lucu",
                        "payload": "monyet lucu"
                    },
                    {
                        "content_type": "text",
                        "image_url": "https://i.ibb.co/5G023yb/eunha.jpg",
                        "title": "kucing lucu",
                        "payload": "kucing lucu"
                    },
                    {
                        "content_type": "text",
                        "image_url": "https://i.ibb.co/5G023yb/eunha.jpg",
                        "title": "avatar bot",
                        "payload": "avatar bot"
                    }
                ]
            }
            dispatcher.utter_custom_json(json_message=message)
        else:
            dispatcher.utter_template('utter_ask_demo_quick_reply', tracker=tracker)

        return []


class RandomImage(Action):
    def name(self):  # type: () -> Text
        return 'action.random_image'

    def run(
        self,
        dispatcher,  # type: CollectingDispatcher
        tracker,  # type: Tracker
        domain,  # type:  Dict[Text, Any]
    ):  # type: (...) -> List[Dict[Text, Any]]
        the_number = random.randrange(0, 4, 1)
        if the_number is 0:
            msg = "https://i.ibb.co/7CsMrpv/Octocat.png"
        elif the_number is 1:
            msg = "https://i.ibb.co/QKcvDxN/kucing-lucu.jpg"
        elif the_number is 2:
            msg = "https://i.ibb.co/19YYgNp/monyet-lucu.jpg"
        elif the_number is 3:
            msg = "https://i.ibb.co/5G023yb/eunha.jpg"
        else:
            msg = 'Oopps, gambar tidak bisa ditampilkan :D'

        # dispatcher.utter_message(msg)
        dispatcher.utter_image_url(msg)
        print(f'DISPATCHER MESSAGE: {dispatcher.messages}')
        return []


class LinkAttachment(Action):
    def name(self):  # type: () -> Text
        return 'action.link_attachment'

    def run(
        self,
        dispatcher,  # type: CollectingDispatcher
        tracker,  # type: Tracker
        domain,  # type:  Dict[Text, Any]
    ):  # type: (...) -> List[Dict[Text, Any]]
        dispatcher.utter_attachment(
            attachment="https://drive.google.com/file/d/154xg034lu9GouCOgtP9SI0Ev-HzhFuUx/view?usp=sharing",
            text="Contoh dokumen")
        return []
