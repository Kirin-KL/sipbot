import pjsua as pj
import time
import speech_recognition as sr
import subprocess
import re
from webhook import send_to_n8n

# ======== SIP ========
SIP_DOMAIN = "181571.voice.plusofon.ru"
SIP_USER = "21261774115582"
SIP_PASS = "FlvUenbQ"

# ======== Проверка длинны  ========
def validate_digits(digits: str, expected_len: int) -> bool:
    return digits.isdigit() and len(digits) == expected_len

# ======== STT ========
def recognize(filename):
    r = sr.Recognizer()

    with sr.AudioFile(filename) as source:
        audio = r.record(source)

    try:
        return r.recognize_google(audio, language="ru-RU")
    except:
        return ""

# ======== FIX WAV через FFmpeg ========
def convert_wav(input_file, output_file):
    subprocess.run([
        "ffmpeg", "-y", "-i", input_file,
        "-ar", "8000", "-ac", "1", output_file
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ======== извлечение цифр ========
def extract_digits(text):
    # если уже цифры
    digits = re.findall(r"\d", text)
    if digits:
        return "".join(digits)

    NUM_MAP = {
        "ноль": "0", "один": "1", "два": "2",
        "три": "3", "четыре": "4", "пять": "5",
        "шесть": "6", "семь": "7",
        "восемь": "8", "девять": "9"
    }

    result = ""
    for word in text.lower().split():
        if word in NUM_MAP:
            result += NUM_MAP[word]

    return result

# ======== лог ========
def log_cb(level, msg, length):
    print(msg.strip())

active_calls = []

# ======== парсинг номера телефона ========
def parse_phone(uri: str) -> str:
    """
    Извлекает номер телефона из SIP URI.
    Возвращает только цифры.
    """
    if not uri:
        return ""

    # 1. Ищем номер внутри sip:...@
    m = re.search(r"sip:(\+?\d+)", uri)
    if m:
        return m.group(1)

    # 2. Ищем номер внутри tel:...
    m = re.search(r"tel:(\+?\d+)", uri)
    if m:
        return m.group(1)

    # 3. Если ничего не нашли — вытаскиваем все цифры
    digits = re.findall(r"\d+", uri)
    if digits:
        return digits[0]

    return ""


# ======== Call ========
class CallCallback(pj.CallCallback):
    def __init__(self, call):
        super().__init__(call)

        self.state = "account"
        self.phase = "idle"

        self.wait_until = None
        self.record_until = None
        self.recorder_id = None
        self.player_id = None

        self.phone = parse_phone(call.info().remote_uri)
        self.account = ""
        self.cold = ""
        self.hot = ""

    def on_state(self):
        print("Call state:", self.call.info().state_text)

    def on_media_state(self):
        if self.call.info().media_state == pj.MediaState.ACTIVE:
            print("📞 Call started")
            self.ask("aydio/account.wav")

    # ======== проигрывание ========
    def play(self, file):
        if self.player_id:
            try:
                lib.player_destroy(self.player_id)
            except:
                pass

        self.player_id = lib.create_player(file, loop=False)
        slot = lib.player_get_slot(self.player_id)
        call_slot = self.call.info().conf_slot
        lib.conf_connect(slot, call_slot)

    # ======== задать вопрос ========
    def ask(self, file):
        self.play(file)
        self.phase = "wait"
        self.wait_until = time.time() + 3  # ждать пока проиграется

    # ======== запись ========
    def start_record(self):
        print("🎤 Recording...")
        self.recorder_id = lib.create_recorder("input.wav")

        rec_slot = lib.recorder_get_slot(self.recorder_id)
        call_slot = self.call.info().conf_slot

        lib.conf_connect(call_slot, rec_slot)

        self.phase = "record"
        self.record_until = time.time() + 10

    def stop_record(self):
        print("🛑 Stop recording")

        if self.recorder_id:
            lib.recorder_destroy(self.recorder_id)
            self.recorder_id = None

        convert_wav("input.wav", "clean.wav")

        text = recognize("clean.wav")
        print("🧠 Recognized:", text)

        digits = extract_digits(text)
        print("🔢 Digits:", digits)

        return digits


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


# ======== INIT ========
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

            # ===== ЖДЕМ ПОСЛЕ ВОПРОСА =====
            if c.phase == "wait" and now >= c.wait_until:
                c.start_record()

            # ===== ЗАПИСЬ ЗАКОНЧЕНА =====
            elif c.phase == "record" and now >= c.record_until:
                digits = c.stop_record()

                # ===== ВАЛИДАЦИЯ =====
                if c.state == "account":
                    if not validate_digits(digits, 10):
                        print("❌ Account digits invalid, repeating...")
                        c.ask("aydio/repeat.wav")
                        continue
                    c.account = digits
                    print("Account:", digits)
                    c.state = "cold"
                    c.ask("aydio/cold_water.wav")

                elif c.state == "cold":
                    if not validate_digits(digits, 8):
                        print("❌ Cold water digits invalid, repeating...")
                        c.ask("aydio/repeat.wav")
                        continue
                    c.cold = digits
                    print("Cold:", digits)
                    c.state = "hot"
                    c.ask("aydio/hot_water.wav")

                elif c.state == "hot":
                    if not validate_digits(digits, 8):
                        print("❌ Hot water digits invalid, repeating...")
                        c.ask("aydio/repeat.wav")
                        continue
                    c.hot = digits
                    print("Hot:", digits)
                    c.state = "done"
                    c.ask("aydio/end.wav")

                elif c.state == "done":
                    print("📤 Sending data to n8n...")

                    status, text = send_to_n8n(
                        phone=c.phone,
                        account=c.account,
                        hotWater=c.hot,
                        coldWater=c.cold
                    )

                    print("n8n response:", status, text)

                    print("❌ Hanging up")
                    c.call.hangup()
                    active_calls.remove(c)
                    continue



except KeyboardInterrupt:
    print("Exiting...")

finally:
    lib.destroy()
    lib = None