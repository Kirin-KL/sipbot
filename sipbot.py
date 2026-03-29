import pjsua as pj
import time

# ======== Настройки SIP ========
SIP_DOMAIN = "181571.voice.plusofon.ru"
SIP_USER = "21261774115582"
SIP_PASS = "FlvUenbQ"

# ======== Логирование ========
def log_cb(level, msg, length):
    print(msg.strip())

# ======== Глобальный список звонков ========
active_calls = []

# ======== Callback для звонков ========
class CallCallback(pj.CallCallback):
    def __init__(self, call):
        super().__init__(call)
        self.hangup_time = None

    def on_state(self):
        print("Call state:", self.call.info().state_text)

    def on_media_state(self):
        if self.call.info().media_state == pj.MediaState.ACTIVE:
            print("📞 Call answered, will hangup in 10 sec")
            self.hangup_time = time.time() + 10

# ======== Callback для аккаунта ========
class AccountCallback(pj.AccountCallback):
    def __init__(self, account):
        super().__init__(account)

    def on_incoming_call(self, call):
        print("📞 Incoming call")

        call_cb = CallCallback(call)
        call.set_callback(call_cb)

        call.answer(200)
        active_calls.append(call_cb)

# ======== Инициализация ========
lib = pj.Lib()

try:
    lib.init(log_cfg=pj.LogConfig(level=3, callback=log_cb))

    # Без аудиоустройства (но медиа работает)
    lib.set_null_snd_dev()

    # Транспорт
    transport = lib.create_transport(pj.TransportType.UDP)

    lib.start()

    # ======== Кодеки (рекомендуется) ========
    lib.set_codec_priority("PCMU/8000", 255)
    lib.set_codec_priority("PCMA/8000", 255)
    lib.set_codec_priority("opus/48000/2", 200)

    # ======== Аккаунт ========
    acc_cfg = pj.AccountConfig()
    acc_cfg.id = f"sip:{SIP_USER}@{SIP_DOMAIN}"
    acc_cfg.reg_uri = f"sip:{SIP_DOMAIN}"
    acc_cfg.auth_cred = [
        pj.AuthCred("*", SIP_USER, SIP_PASS)
    ]

    acc = lib.create_account(acc_cfg)
    acc.set_callback(AccountCallback(acc))

    print("✅ SIP bot ready and registered. Waiting for calls...")

    # ======== Основной цикл ========
    while True:
        lib.handle_events(50)

        now = time.time()

        for call_cb in active_calls[:]:
            if call_cb.hangup_time and now >= call_cb.hangup_time:
                try:
                    print("❌ Hanging up")
                    call_cb.call.hangup()
                except pj.Error as e:
                    print("Hangup error:", e)

                active_calls.remove(call_cb)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    lib.destroy()
    lib = None