import pjsua as pj
import time
import speech_recognition as sr
import re

def clean_text(text):
    return re.sub(r"[^а-я0-9 ]", "", text.lower())

# ======== текст → цифры ========
def text_to_digits(text):
    text = text.lower()
    result = ""

    for word in text.split():
        if word in NUM_MAP:
            result += NUM_MAP[word]
        elif word.isdigit():
            result += word

    return result

# ======== SIP ========
SIP_DOMAIN = "181571.voice.plusofon.ru"
SIP_USER = "21261774115582"
SIP_PASS = "FlvUenbQ"

# ======== Speech-to-Text ========
def recognize(filename):
    r = sr.Recognizer()

    with sr.AudioFile(filename) as source:
        audio = r.record(source)

    try:
        text = r.recognize_google(audio, language="ru-RU")
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print("STT error:", e)
        return ""

# ======== текст → цифры ========
NUM_MAP = {
    "ноль": "0", "один": "1", "два": "2",
    "три": "3", "четыре": "4", "пять": "5",
    "шесть": "6", "семь": "7",
    "восемь": "8", "девять": "9"
}

def text_to_digits(text):
    result = ""
    for word in text.lower().split():
        if word in NUM_MAP:
            result += NUM_MAP[word]
    return result

# ======== лог ========
def log_cb(level, msg, length):
    print(msg.strip())

active_calls = []

# ======== Call ========
class CallCallback(pj.CallCallback):
    def __init__(self, call):
        super().__init__(call)
        self.state = "start"
        self.record_until = None
        self.recorder_id = None

    def on_state(self):
        print("Call state:", self.call.info().state_text)

    def on_media_state(self):
        if self.call.info().media_state == pj.MediaState.ACTIVE:
            print("📞 Call started")
            self.ask_account()

    # ======== проигрывание ========
    def play(self, file):
        player_id = lib.create_player(file, loop=False)
        slot = lib.player_get_slot(player_id)
        call_slot = self.call.info().conf_slot
        lib.conf_connect(slot, call_slot)

    # ======== запись ========
    def start_record(self, filename="input.wav", duration=7):
        print("🎤 Recording...")
        self.recorder_id = lib.create_recorder(filename)
        rec_slot = lib.recorder_get_slot(self.recorder_id)
        call_slot = self.call.info().conf_slot
        lib.conf_connect(call_slot, rec_slot)

        self.record_until = time.time() + duration

    def stop_record_and_recognize(self):
        print("🛑 Stop recording")
        lib.recorder_destroy(self.recorder_id)
        self.recorder_id = None

        text = recognize("input.wav")
        print("🧠 Recognized:", text)

        digits = text_to_digits(text)
        print("🔢 Digits:", digits)

        return digits

    # ======== сценарий ========
    def ask_account(self):
        self.play("aydio/account.wav")
        self.state = "wait_account"
        self.record_until = time.time() + 2  # пауза перед записью

    def ask_cold(self):
        self.play("aydio/cold_water.wav")
        self.state = "wait_cold"
        self.record_until = time.time() + 2

    def ask_hot(self):
        self.play("aydio/hot_water.wav")
        self.state = "wait_hot"
        self.record_until = time.time() + 2

    def say_bye(self):
        self.play("aydio/end.wav")
        self.state = "done"
        self.record_until = time.time() + 3


# ======== Account ========
class AccountCallback(pj.AccountCallback):
    def __init__(self, acc):
        super().__init__(acc)

    def on_incoming_call(self, call):
        print("📞 Incoming call")
        cb = CallCallback(call)
        call.set_callback(cb)
        call.answer(200)
        active_calls.append(cb)


# ======== init ========
lib = pj.Lib()

try:
    lib.init(log_cfg=pj.LogConfig(level=3, callback=log_cb))
    lib.set_null_snd_dev()
    lib.create_transport(pj.TransportType.UDP)
    lib.start()

    acc_cfg = pj.AccountConfig()
    acc_cfg.id = f"sip:{SIP_USER}@{SIP_DOMAIN}"
    acc_cfg.reg_uri = f"sip:{SIP_DOMAIN}"
    acc_cfg.auth_cred = [pj.AuthCred("*", SIP_USER, SIP_PASS)]

    acc = lib.create_account(acc_cfg)
    acc.set_callback(AccountCallback(acc))

    print("✅ Ready")

    # ======== MAIN LOOP ========
    while True:
        lib.handle_events(50)

        now = time.time()

        for c in active_calls[:]:

            # старт записи после паузы
            if c.record_until and now >= c.record_until:
                if c.recorder_id is None:
                    c.start_record()
                else:
                    digits = c.stop_record_and_recognize()

                    if c.state == "wait_account":
                        print("Account:", digits)
                        c.ask_cold()

                    elif c.state == "wait_cold":
                        print("Cold:", digits)
                        c.ask_hot()

                    elif c.state == "wait_hot":
                        print("Hot:", digits)
                        c.say_bye()

                    elif c.state == "done":
                        print("❌ Hanging up")
                        c.call.hangup()
                        active_calls.remove(c)

                    c.record_until = None

except KeyboardInterrupt:
    pass

finally:
    lib.destroy()