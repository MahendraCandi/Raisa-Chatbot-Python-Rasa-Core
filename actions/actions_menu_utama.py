import json
from typing import Text

from linebot.models import TemplateSendMessage, CarouselTemplate, CarouselColumn, MessageAction
from rasa_sdk import Action


class MenuUtama(Action):
    def name(self) -> Text:
        return 'action.menu_utama'

    def run(self, dispatcher, tracker, domain):
        if tracker.get_latest_input_channel() == 'facebook':
            message = {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [
                            {
                                "title": "Dialog",
                                "image_url": "https://image.ibb.co/iox0eK/Super-Cub-C125.jpg",
                                "subtitle": "Tanya angsuran motor kamu",
                                "buttons": [{
                                    "type": "postback",
                                    "title": "Informasi Tenor",
                                    "payload": "informasi tenor"
                                }, {
                                    "type": "postback",
                                    "title": "Nomor Kontrak",
                                    "payload": "nomor kontrak"
                                }]
                            },
                            {
                                "title": "Feature",
                                "image_url": "https://i.ibb.co/5G023yb/eunha.jpg",
                                "subtitle": "Apa yang bisa aku lakukan",
                                "buttons": [{
                                    "type": "postback",
                                    "title": "Quick Reply",
                                    "payload": "demo quick reply"
                                }, {
                                    "type": "postback",
                                    "title": "Show Image",
                                    "payload": "show image"
                                }]
                            }
                        ]
                    }
                }
            }
            bot_name = tracker.get_slot('bot_name')
            dispatcher.utter_message(f'Hai, perkenalkan aku {bot_name}. Assistant Virtual yang bakal temenin kamu')
            dispatcher.utter_message(f'Cari informasi tentang demo {bot_name} dibawah ini ya :D')
            dispatcher.utter_custom_json(json_message=message)
        elif tracker.get_latest_input_channel() == 'line':
            carousel_template_message = TemplateSendMessage(
                alt_text="Carousel Template",
                template=CarouselTemplate(
                    columns=[
                        CarouselColumn(
                            thumbnail_image_url="https://i.ibb.co/5G023yb/eunha.jpg",
                            title="Dialog",
                            text="Tanya angsuran motor kamu",
                            actions=[
                                MessageAction(
                                    label="Informasi Tenor",
                                    text="informasi tenor"
                                ),
                                MessageAction(
                                    label="Nomor Kontrak",
                                    text="nomor kontrak"
                                )
                            ]
                        ),
                        CarouselColumn(
                            thumbnail_image_url="https://i.ibb.co/5G023yb/eunha.jpg",
                            title="Feature",
                            text="Apa yang bisa aku lakukan",
                            actions=[
                                MessageAction(
                                    label="Quick Reply",
                                    text="demo quick reply"
                                ),
                                MessageAction(
                                    label="Show Image",
                                    text="show image"
                                )
                            ]
                        )
                    ]
                )
            )
            # print(f'TYPE: {type(str(carousel_template_message))}')
            data = json.loads(str(carousel_template_message))
            # print(f'TYPE: {type(data)}')
            dispatcher.utter_custom_json(data)
        else:
            dispatcher.utter_template('utter_sapaan', tracker=tracker)
        return []
