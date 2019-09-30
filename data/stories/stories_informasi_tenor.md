## informasi tenor happy path
* cek_informasi_tenor
    - informasi_tenor_form
    - form{"name":"informasi_tenor_form"}
    - form{"name":"null"}
    - action.informasi_tenor.validateKontrakKtp
* konfirmasi
    - slot{"is_terima_salinan_kontrak": true}
    - action.informasi_tenor.showTenor
    - utter_terima_kasih
    - action_restart
    
## informasi tenor kontrak belum terima sambungkan ke agent
* cek_informasi_tenor
    - informasi_tenor_form
    - form{"name":"informasi_tenor_form"}
    - form{"name":"null"}
    - action.informasi_tenor.validateKontrakKtp
* tolak
    - slot{"is_terima_salinan_kontrak": false}
    - action.informasi_tenor.showTenor
* konfirmasi
    - slot{"is_talk_to_cs": true}
    - utter_affirm_talk_to_agent
    - action.informasi_tenor.talkToLiveAgent
    - action_restart

## informasi tenor kontrak belum terima tidak ke agent
* cek_informasi_tenor
    - informasi_tenor_form
    - form{"name":"informasi_tenor_form"}
    - form{"name":"null"}
    - action.informasi_tenor.validateKontrakKtp
* tolak
    - slot{"is_terima_salinan_kontrak": false}
    - action.informasi_tenor.showTenor
* tolak
    - slot{"is_talk_to_cs": false}
    - utter_end_dialog
    - action_restart
    
## informasi tenor cancel scenario
* cek_informasi_tenor
    - informasi_tenor_form
    - form{"name":"informasi_tenor_form"}
    - form{"name":"null"}
    - action.informasi_tenor.validateKontrakKtp
> check_user_cancel

## informasi tenor kontrak belum terima sambungkan ke agent
* cek_informasi_tenor
    - informasi_tenor_form
    - form{"name":"informasi_tenor_form"}
    - form{"name":"null"}
    - action.informasi_tenor.validateKontrakKtp
* tolak
    - slot{"is_terima_salinan_kontrak": false}
    - action.informasi_tenor.showTenor
> check_user_cancel
