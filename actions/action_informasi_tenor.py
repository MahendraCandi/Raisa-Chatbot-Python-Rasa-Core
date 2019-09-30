import logging
import re
from typing import Any, Text, Dict, List, Optional

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, Restarted
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from common import my_api

reg_12_num = '\\d{12}'
BOT_NAME = 'bot_name'


class ValidateKontrakKtp(Action):
    def name(self):  # type: () -> Text
        return 'action.informasi_tenor.validateKontrakKtp'

    def run(self, dispatcher, tracker, domain):
        kontrak = tracker.get_slot('nomor_kontrak')
        ktp = tracker.get_slot('nomor_ktp')
        installment = my_api.API(tracker.get_latest_input_channel()).get_api_1(kontrak=kontrak, ktp=ktp)
        if installment is not None:
            dispatcher.utter_message('Terima kasih atas ketersediaanya')
            if tracker.get_latest_input_channel() == 'facebook':
                message = {
                    "text": "Apakah Anda sudah menerima salinan dokumen kontrak Anda?",
                    "quick_replies": [
                        {
                            "content_type": "text",
                            "image_url": "https://i.ibb.co/5G023yb/eunha.jpg",
                            "title": "Ya, sudah",
                            "payload": "/konfirmasi{\"is_terima_salinan_kontrak\": true}"
                        },
                        {
                            "content_type": "text",
                            "image_url": "https://i.ibb.co/5G023yb/eunha.jpg",
                            "title": "Tidak, belum",
                            "payload": "/tolak{\"is_terima_salinan_kontrak\": false}"
                        }
                    ]
                }
                dispatcher.utter_custom_json(json_message=message)
            else:
                dispatcher.utter_template('utter_konfirmasi_salinan_dokumen_kontrak', tracker)
            return []
        else:
            SlotSet('nomor_kontrak', value=None)
            SlotSet('nomor_ktp', value=None)
            dispatcher.utter_message(f'Maaf {tracker.get_slot(BOT_NAME)} tidak menemukan data yang dimasukan :(')
            return [Restarted()]


class ShowTenor(Action):
    def name(self):  # type: () -> Text
        return 'action.informasi_tenor.showTenor'

    def run(
        self,
        dispatcher,  # type: CollectingDispatcher
        tracker,  # type: Tracker
        domain,  # type:  Dict[Text, Any]
    ):  # type: (...) -> List[Dict[Text, Any]]
        kontrak = tracker.get_slot('nomor_kontrak')
        ktp = tracker.get_slot('nomor_ktp')
        installment = my_api.API().get_api_1(kontrak=kontrak, ktp=ktp)
        if installment is not None:
            tenor = installment[0]['tenor']
            is_terima_salinan_kontrak = tracker.get_slot("is_terima_salinan_kontrak")
            if is_terima_salinan_kontrak:
                msg = f'Jumlah tenor sesuai dengan salinan dokumen kontrak Anda adalah {tenor}'
                dispatcher.utter_message(msg)
            else:
                msg = f'Jumlah tenor atas nomor kontrak yang Anda submit adalah {tenor} bulan'
                dispatcher.utter_message(msg)
                if tracker.get_latest_input_channel() == 'facebook':
                    message = {
                        "text": "Apakah Anda bersedia cabang kami melakukan follow up kepada Anda maksimal 2x24 jam?",
                        "quick_replies": [
                            {
                                "content_type": "text",
                                "image_url": "https://i.ibb.co/5G023yb/eunha.jpg",
                                "title": "Iya",
                                "payload": "/konfirmasi{\"is_talk_to_cs\": true}"
                            },
                            {
                                "content_type": "text",
                                "image_url": "https://i.ibb.co/5G023yb/eunha.jpg",
                                "title": "Tidak",
                                "payload": "/tolak{\"is_talk_to_cs\": false}"
                            }
                        ]
                    }

                    dispatcher.utter_custom_json(json_message=message)
                else:
                    dispatcher.utter_template('utter_follow_up_cabang', tracker)
        return []


class TalkToLiveAgent(Action):
    def name(self):  # type: () -> Text
        return 'action.informasi_tenor.talkToLiveAgent'

    def run(
        self,
        dispatcher,  # type: CollectingDispatcher
        tracker,  # type: Tracker
        domain,  # type:  Dict[Text, Any]
    ):  # type: (...) -> List[Dict[Text, Any]]
        is_talk_to_live_agent = tracker.get_slot('is_talk_to_cs')
        if is_talk_to_live_agent:
            dispatcher.utter_message('Anda sedang berada diantrian agent kami')
        return []


class informasiTenorAsk(Action):
    def name(self):  # type: () -> Text
        return 'actions.informasi_tenor.ask'


class InformasiTenorForm(FormAction):
    def name(self):  # type: () -> Text
        return 'informasi_tenor_form'

    @staticmethod
    def required_slots(tracker):  # type: (Tracker) -> List[Text]
        _dict = ["nomor_kontrak", "nomor_ktp"]
        return _dict

    def slot_mappings(self):  # type: () -> Dict[Text: Union[Dict, List[Dict]]]
        _dict = {
            "nomor_kontrak": [
                self.from_entity(
                    entity="nomor_kontrak",
                    intent="ketik_nomor_kontrak"
                ),
                self.from_entity(
                    entity="nomor_kontrak",
                    intent="cek_informasi_tenor"
                ),
                self.from_text()
            ],
            "nomor_ktp": [
                self.from_entity(
                    entity="nomor_ktp",
                    intent="ketik_nomor_ktp"
                ),
                self.from_text()
            ]
        }
        return _dict

    def validate_nomor_kontrak(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> Dict[Text: Any]:
        valid = re.search(reg_12_num, value)
        intent = tracker.latest_message.get('intent', {}).get('name')
        if valid:
            return {'nomor_kontrak': value}
        else:
            if intent != 'cancel':
                dispatcher.utter_template("utter_invalid_value", tracker=tracker)
            return {'nomor_kontrak': None}

    def validate_nomor_ktp(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> Optional[Dict]:
        valid = re.search(reg_12_num, value)
        if valid:
            return {'nomor_ktp': value}
        else:
            intent = tracker.latest_message.get('intent', {}).get('name')
            if intent != 'cancel':
                dispatcher.utter_template("utter_invalid_value", tracker=tracker)
            return {'nomor_ktp': None}

    def request_next_slot(
        self,
        dispatcher,  # type: CollectingDispatcher
        tracker,  # type: Tracker
        domain,  # type: Dict[Text, Any]
    ):
        # type: (...) -> Optional[List[Dict]]
        """Request the next slot and utter template if needed,
            else return None"""
        intent = tracker.latest_message.get('intent', {}).get('name')
        if intent == 'cancel':
            dispatcher.utter_template('utter_cancel_response', tracker=tracker)
            return [Restarted()]
        else:
            for slot in self.required_slots(tracker):
                if self._should_request_slot(tracker, slot):
                    logging.debug("Request next slot '{}'".format(slot))
                    dispatcher.utter_template(
                        "utter_ask_{}".format(slot),
                        tracker,
                        silent_fail=False,
                        **tracker.slots
                    )
                    return [SlotSet("requested_slot", slot)]
            return None

    def submit(self, dispatcher, tracker, domain):
        # type: (CollectingDispatcher, Tracker, Dict[Text, Any]) -> List[Dict]
        return []


