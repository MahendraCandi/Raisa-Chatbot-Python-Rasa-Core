import locale
import logging
import re
from typing import Text, Optional
from datetime import datetime as dt

from rasa_sdk import Tracker
from rasa_sdk.events import Restarted, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from typing import Dict
from typing import Any
from typing import List
from rasa_sdk.forms import FormAction

from builder.quick_reply_builder import QuickRepliesBuilder
from common import my_api as api


locale.setlocale(locale.LC_ALL, "id_ID")
_KENDALA_NOMOR_KONTRAK = "kendala_nomor_kontrak"
_IS_KONTRAK_AKTIF = "is_kontrak_aktif"
_NOMOR_KONTRAK = "nomor_kontrak"
_NOMOR_HP = "nomor_hp"
_IS_FOLLOW_UP_CABANG = "is_follow_up_cabang"
_NOMOR_KTP = "nomor_ktp"
_IS_KONTRAK_KENAL = "is_kontrak_kenal"
_TEMPO_PARSE = "%Y-%m-%d"
_TEMPO_FORMAT = "%d %B %Y"
_phoneRegex = "^(\\+62|0|62)\\s?[2-9]\\d{2,3}\\-?\\d{2,4}\\-?\\d{3,4}$"
_sixteen_digits = "\\d{16}"
_check_has_symbols = "[-$%^*()_+|~=`{}\\[\\]:\";'<>\\/#@]"
_check_has_numbers = "-?\\d+"
_skip = "SKIP"


class FormNomorKontrak(FormAction):
    def __init__(self):
        self.__data = {}

    def name(self):  # type: () -> Text
        return 'form_kendala_nomor_kontrak'

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        slots = [_KENDALA_NOMOR_KONTRAK, _IS_KONTRAK_AKTIF, _NOMOR_KONTRAK,
                 _NOMOR_HP, _IS_FOLLOW_UP_CABANG, _NOMOR_KTP, _IS_KONTRAK_KENAL]
        if tracker.get_slot(_KENDALA_NOMOR_KONTRAK) == "1":
            if tracker.get_slot(_IS_KONTRAK_AKTIF) is True:
                slots = [_KENDALA_NOMOR_KONTRAK, _IS_KONTRAK_AKTIF, _NOMOR_KONTRAK]
            elif tracker.get_slot(_IS_KONTRAK_AKTIF) is False:
                slots = [_KENDALA_NOMOR_KONTRAK, _IS_KONTRAK_AKTIF, _NOMOR_KONTRAK, _NOMOR_HP, _IS_FOLLOW_UP_CABANG]
        elif tracker.get_slot(_KENDALA_NOMOR_KONTRAK) == "2":
            slots = [_KENDALA_NOMOR_KONTRAK, _NOMOR_KTP, _IS_KONTRAK_KENAL, _IS_FOLLOW_UP_CABANG]
        '''
            tracker.get_slot(_KENDALA_NOMOR_KONTRAK) == "3":
                connect to live agent, validate in validate_kendala_nomor_kontrak
        '''
        return slots

    def slot_mappings(self):  # type: () -> Dict[Text: Union[Dict, List[Dict]]]
        mapping = {
            _KENDALA_NOMOR_KONTRAK: [
                self.from_entity(entity="pilih_nomor", intent="pilih_nomor"),
                self.from_entity(
                    entity=_KENDALA_NOMOR_KONTRAK,
                    not_intent=[
                        "ketik_nomor_kontrak",
                        "ketik_nomor_ktp",
                        "ketik_nomor_handphone"]
                ),
                self.from_text(intent=None)
            ],
            _IS_KONTRAK_AKTIF: [
                self.from_intent(intent="konfirmasi", value=True),
                self.from_intent(intent="tolak", value=False),
                self.from_text(intent=None)
            ],
            _NOMOR_KONTRAK: [
                self.from_entity(entity=_NOMOR_KONTRAK, not_intent=[
                        "ketik_nomor_ktp",
                        "ketik_nomor_handphone"]),
                self.from_text(intent=None)
            ],
            _NOMOR_HP: [
                self.from_entity(entity=_NOMOR_HP, intent="ketik_nomor_handphone"),
                self.from_text(intent=None)
            ],
            _IS_FOLLOW_UP_CABANG: [
                self.from_intent(intent="konfirmasi", value=True),
                self.from_intent(intent="tolak", value=False),
                self.from_text(intent=None)
            ],
            _NOMOR_KTP: [
                self.from_entity(entity=_NOMOR_KTP, intent="ketik_nomor_ktp"),
                self.from_text(intent=None)
            ],
            _IS_KONTRAK_KENAL: [
                self.from_entity(entity="pilih_nomor", intent="pilih_nomor"),
                self.from_intent(intent="konfirmasi", value=True),
                self.from_intent(intent="tolak", value=False),
                self.from_text(intent=None)
            ]
        }
        return mapping

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
            self.pop_data_user(self.get_sender_id(tracker=tracker))
            return [Restarted()]
        else:
            for slot in self.required_slots(tracker):
                if self._should_request_slot(tracker, slot):
                    logging.debug("Request next slot '{}'".format(slot))
                    msg = self.check_slot(slot=slot, tracker=tracker, dispatcher=dispatcher)
                    if msg is not None:
                        dispatcher.utter_custom_json(msg)
                    else:
                        dispatcher.utter_template(
                            "utter_ask_{}".format(slot),
                            tracker=tracker,
                            silent_fail=False,
                            **tracker.slots
                        )
                    return [SlotSet("requested_slot", slot)]
            return None

    def validate_kendala_nomor_kontrak(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> Optional[Dict]:
        slots = {}
        if tracker.latest_message.get('intent', {}).get('name') != 'cancel':
            if value not in ["1", "2", "3"]:
                value = None
                dispatcher.utter_template("utter_invalid_value", tracker=tracker)
            else:
                if value == "3":
                    slots.update({
                        _IS_KONTRAK_AKTIF: _skip,
                        _NOMOR_KONTRAK: _skip,
                        _NOMOR_HP: _skip,
                        _IS_FOLLOW_UP_CABANG: _skip,
                        _NOMOR_KTP: _skip,
                        _IS_KONTRAK_KENAL: _skip
                    })
        slots.update({_KENDALA_NOMOR_KONTRAK: value})
        return slots

    def validate_is_kontrak_aktif(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> Optional[Dict]:
        if tracker.latest_message.get('intent', {}).get('name') != 'cancel':
            if value is True:
                dispatcher.utter_custom_json(
                    json_message={"text": "Mohon dapat menyebutkan nomor kontrak yang sebenarnya"})
            elif value is False:
                dispatcher.utter_custom_json(
                    json_message={"text": "Mohon masukan nomor kontrak yang terakhir ditagihkan kepada Anda"})
            else:
                value = None
                dispatcher.utter_template("utter_invalid_value", tracker=tracker)
        return {_IS_KONTRAK_AKTIF: value}

    def validate_nomor_hp(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> Optional[Dict]:
        if tracker.latest_message.get('intent', {}).get('name') != 'cancel':
            if not re.search(pattern=_phoneRegex, string=value):
                value = None
                dispatcher.utter_template("utter_invalid_value", tracker=tracker)
        return {_NOMOR_HP: value}

    def validate_is_follow_up_cabang(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> Optional[Dict]:
        if tracker.latest_message.get('intent', {}).get('name') != 'cancel':
            if not isinstance(value, bool):
                value = None
                dispatcher.utter_template("utter_invalid_value", tracker=tracker)
        return {_IS_FOLLOW_UP_CABANG: value}


    def validate_nomor_ktp(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> Optional[Dict]:
        if tracker.latest_message.get('intent', {}).get('name') != 'cancel':
            if re.search(_sixteen_digits, value) is False:
                value = None
                dispatcher.utter_template("utter_invalid_value", tracker=tracker)
            else:
                sender_id = self.get_sender_id(tracker)
                token = self.is_sender_id_token_exist(sender_id=sender_id, tracker=tracker)
                sum_contract_list = token.get_api_3(value)
                data_user = DataUser(sender_id=sender_id,
                                     token=token,
                                     sum_contract_list=sum_contract_list,
                                     index=0, nomor_dipilih=[])
                self.update_user_data(data_user=data_user)

                if (not sum_contract_list) or (sum_contract_list is None):
                    value = None
                    dispatcher.utter_message("Maaf, kami tidak menemukan data berdasarkan nomor "
                                             "KTP yang Anda masukan. Silakan ulang kembali ya")
        return {_NOMOR_KTP: value}

    def validate_is_kontrak_kenal(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> Optional[Dict]:
        slots = {}
        if tracker.latest_message.get('intent', {}).get('name') != 'cancel':
            if not isinstance(value, bool):
                data_user = self.get_user_data(tracker)
                if isinstance(value, list):
                    data_user.nomor_dipilih = value
                else:
                    if not re.search(_check_has_symbols, value):
                        nomor_dipilih = re.findall(_check_has_numbers, value)
                        if nomor_dipilih:
                            for nomor in nomor_dipilih:
                                for i in range(1, data_user.index, 1):
                                    if int(nomor) == i:
                                        data_user.nomor_dipilih.append(nomor)
                            if not data_user.nomor_dipilih:
                                value = None
                        else:
                            value = None
                    else:
                        value = None
                self.update_user_data(data_user)
            else:
                '''
                    def required_slots:
                        if _IS_KONTRAK_KENAL is False:
                            slots = [_KENDALA_NOMOR_KONTRAK, _NOMOR_KTP, _IS_KONTRAK_KENAL]
                    
                    menggunakana cara ini untuk mengakhiri form tidak berlaku, karena required
                    slot diproses ketika mau masuk ke slot berikutnya. Casenya adalah ketika forms sedang
                    berasda pada slot _IS_KONTRAK_KENAL, kemudian jika disini user merespon dengan 'tidak' 
                    (value = False), maka form harusnya langsung tersubmit. Karena ini tidak bisa
                    maka slot berikutnya diisi dengan 'SKIP'.
                '''
                if value is False:
                    slots.update({_IS_FOLLOW_UP_CABANG: _skip})
        if value is None:
            dispatcher.utter_template("utter_invalid_value", tracker=tracker)
        slots.update({_IS_KONTRAK_KENAL: value})
        return slots

    def submit(self, dispatcher, tracker, domain):
        # type: (CollectingDispatcher, Tracker, Dict[Text, Any]) -> List[Dict]
        kendala = tracker.get_slot(_KENDALA_NOMOR_KONTRAK)
        is_kontrak_aktif = tracker.get_slot(_IS_KONTRAK_AKTIF)
        is_follow_up_cabang = tracker.get_slot(_IS_FOLLOW_UP_CABANG)
        is_kontrak_kenal = tracker.get_slot(_IS_KONTRAK_KENAL)
        if kendala == "1":
            if is_kontrak_aktif is True:
                data_user = self.get_user_data(tracker=tracker)
                nomor_kontrak = tracker.get_slot(_NOMOR_KONTRAK)
                installment = data_user.token.get_api_2(nomor_kontrak=nomor_kontrak)
                tempo = installment[0]['next_due_date']
                tgl_parse = dt.strptime(tempo, _TEMPO_PARSE)
                tempo = tgl_parse.strftime(_TEMPO_FORMAT)
                msg = f"Mohon melakukan pembayaran angsuran sesuai nominal tsb setiap " \
                    f"bulannnya sebelum jatuh tempo pada tgl {tempo} berikutnya"
                dispatcher.utter_message(msg)
            elif is_kontrak_aktif is False:
                if is_follow_up_cabang is True:
                    dispatcher.utter_message("Terima kasih atas kesediaannya, Tim cabang kami akan melakukan "
                                             "follow up dan data Anda akan kami hapus dari sistem kami "
                                             "agar tidak menerima sms penagihan kembali maksimal 2x24 jam")
                elif is_follow_up_cabang is False:
                    dispatcher.utter_message("Sesi percakapan Anda telah selesai. Terima kasih telah mengunjungi"
                                             " website Kami")
        if kendala == "2":
            if is_kontrak_kenal is False:
                dispatcher.utter_message("Anda akan dihubungkan ke live agent kami. Mohon menunggu sebentar")
            else:
                if is_follow_up_cabang is True:
                    dispatcher.utter_message("Anda akan dihubungkan ke live agent kami. Mohon menunggu sebentar")
                else:
                    dispatcher.utter_message("Sesi percakapan Anda telah selesai. Terima kasih telah mengunjungi"
                                             " website Kami")
        self.pop_data_user(self.get_sender_id(tracker=tracker))
        return []

    def check_slot(self, slot, tracker: Tracker, dispatcher: CollectingDispatcher) -> {}:
        message = None
        if slot == _KENDALA_NOMOR_KONTRAK:
            text = "Silakan ketik angka di bawah apabila sesuai dengan kendala Anda\n"\
                "1. penagihan atas kontrak orang lain\n"\
                "2. nomor kontrak belum diterima\n"\
                "3. lainnya, sambungkan Live Agent"
            message = QuickRepliesBuilder()\
                .set_text(value=text)\
                .set_content(title="1", payload="1")\
                .set_content(title="2", payload="2")\
                .set_content(title="3", payload="3")\
                .channel(channel=tracker.get_latest_input_channel())\
                .build()
        elif slot == _IS_KONTRAK_AKTIF:
            message = QuickRepliesBuilder()\
                .set_text("Apakah Anda memiliki kontrak aktif?") \
                .set_content(title="Iya", payload="iya") \
                .set_content(title="Tidak", payload="tidak") \
                .channel(channel=tracker.get_latest_input_channel()) \
                .build()
        elif slot == _NOMOR_KONTRAK:
            message = {}
        elif slot == _IS_FOLLOW_UP_CABANG:
            if tracker.get_slot(_KENDALA_NOMOR_KONTRAK) == '2':
                data_user = self.get_user_data(tracker)
                is_kontrak_kenal = tracker.get_slot(_IS_KONTRAK_KENAL)
                if isinstance(is_kontrak_kenal, bool):
                    if is_kontrak_kenal is True:
                        message_list_bucket = self.generate_contract(show_nomor_kontrak=True, data_user=data_user)
                        for message_list in message_list_bucket:
                            dispatcher.utter_message(''.join(message_list))
                else:
                    data_user.nomor_dipilih.sort()
                    contract_list = []
                    sum_contract_list = data_user.sum_contract_list
                    for i in data_user.nomor_dipilih:
                        contract_list.append(sum_contract_list[int(i) - 1])
                    data_user.sum_contract_list = contract_list
                    self.update_user_data(data_user=data_user)
                    message_list_bucket = self.generate_contract(show_nomor_kontrak=True, data_user=data_user)
                    for message_list in message_list_bucket:
                        dispatcher.utter_message(''.join(message_list))
            message = QuickRepliesBuilder() \
                .set_text("Apakah Anda bersedia cabang kami melakukan follow up kepada Anda maksimal 2x24 jam?") \
                .set_content(title="Iya", payload="iya") \
                .set_content(title="Tidak", payload="tidak") \
                .channel(channel=tracker.get_latest_input_channel()) \
                .build()
        elif slot == _NOMOR_KTP:
            message = {
                "text": "Kami membutuhkan data Anda untuk melakukan pencocokan data terlebih dulu "
                        "sebagai keamanan data. Silakan ketik NIK Anda"
            }
        elif slot == _IS_KONTRAK_KENAL:
            message = {}
            data_user = self.get_user_data(tracker)
            dispatcher.utter_message("Apakah Anda mengenal kontrak dibawah ini?")
            data_user.index = 1
            message_list_bucket = self.generate_contract(data_user=data_user)
            for message_list in message_list_bucket:
                dispatcher.utter_message(''.join(message_list))

            qr_content = []
            if data_user.index > 1:
                for i in range(1, data_user.index, 1):
                    qr_content.append({"title": str(i), "payload": str(i)})
            qr_message = QuickRepliesBuilder()\
                .set_text("Silakan ketik pilihan Anda")\
                .set_content_by_dictionary(qr_content)\
                .set_content(title="Iya, semua", payload="iya, semua")\
                .set_content(title="Tidak", payload="tidak")\
                .channel(tracker.get_latest_input_channel())\
                .build()
            dispatcher.utter_custom_json(qr_message)
        logging.debug(f'message: {message}')
        return message

    def generate_contract(self, show_nomor_kontrak=False, data_user=None):
        message_list_bucket = []
        for sum_contract in data_user.sum_contract_list:
            message_list = []
            installments = data_user.token.get_api_2(sum_contract['contract_no'])
            bisnis_unit = installments[0]['buss_unit']
            contract_active_date = dt.strptime(sum_contract['contract_active_date'], "%Y-%m-%d %H:%M:%S.%f")
            contract_active = contract_active_date.strftime(_TEMPO_FORMAT)
            if show_nomor_kontrak is False:
                message_list.append(f"Ketik {data_user.index} untuk kontrak aktif Anda dibawah ini\n")
            else:
                contract_number = sum_contract['contract_no']
                message_list.append(f"Nomor kontrak: {contract_number}\n \n")
            message_list.append(f"Bisnis unit: {bisnis_unit}\n")
            if len(installments) > 1:
                index_in = 1
                for installment in installments:
                    tipe_barang = f"{installment['obj_brand']} {installment['obj_model']} " \
                        f"{installment['obj_type']}"
                    message_list.append(f"Tipe barang {index_in}: {tipe_barang}\n")
                    index_in += 1
            else:
                tipe_barang = f"{installments[0]['obj_brand']} {installments[0]['obj_model']} " \
                    f"{installments[0]['obj_type']}"
                message_list.append(f"Tipe barang: {tipe_barang}\n")

            message_list.append(f"Tanggal kontrak awal terbentuk: {contract_active}\n")
            message_list_bucket.append(message_list)
            data_user.index += 1
        self.update_user_data(data_user)
        return message_list_bucket

    def is_sender_id_token_exist(self, sender_id, tracker: Tracker):
        data_user = self.__data.get(sender_id)
        if data_user is None:
            return api.API(tracker.get_latest_input_channel())
        return data_user.token

    def update_user_data(self, data_user):
        self.__data.update({data_user.sender_id: data_user})

    def get_user_data(self, tracker):
        return self.__data[self.get_sender_id(tracker)]

    @staticmethod
    def get_sender_id(tracker: Tracker):
        return tracker.current_state()['sender_id']

    def check_instance_variable(self):
        logging.debug(f'all data in memory: {self.__data}')

    def pop_data_user(self, sender_id):
        logging.debug(f'{sender_id}, has been pop out')


class DataUser:
    def __init__(self, sender_id: Text, sum_contract_list: [], index: int, nomor_dipilih: [], token):
        self.sender_id = sender_id
        self.sum_contract_list = sum_contract_list
        self.index = index
        self.nomor_dipilih = nomor_dipilih
        self.token = token
