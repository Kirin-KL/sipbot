import pjsua as pj
import time
import threading

# ======== Настройки SIP ========
SIP_DOMAIN = "181571.voice.plusofon.ru"      # твой SIP сервер
SIP_USER = "21261774115582"                  # логин
SIP_PASS = "your_password_here"              # пароль


# ======== Логирование ========
def log_cb(level, msg, length):
    print(msg.strip())


# ======== Инициализация библиотеки ========
lib = pj.Lib()

try:
    # Инициализация с логированием
    lib.init(log_cfg=pj.LogConfig(level=3, callback=log_cb))

    # Для VPS без аудио (можно заменить на аудиоустройства)
    lib.set_null_snd_dev()

    # Создаём транспорт UDP
    transport = lib.create_transport(pj.TransportType.UDP)

    # Запуск библиотеки
    lib.start()

    # ======== Настройка аккаунта ========
    acc_cfg = pj.AccountConfig()
    acc_cfg.id = f"sip:{SIP_USER}@{SIP_DOMAIN}"
    acc_cfg.reg_uri = f"sip:{SIP_DOMAIN}"
    acc_cfg.auth_cred = [pj.AuthCred(realm="*", username=SIP_USER, data=SIP_PASS)]

    # Создаём аккаунт
    acc = lib.create_account(acc_cfg)

    # ======== Callback для звонков ========
    class CallCallback(pj.CallCallback):
        def __init__(self, call):
            super().__init__(call)

        def on_state(self):
            print("Call state:", self.call.info().state_text)

        def on_media_state(self):
            if self.call.info().media_state == pj.MediaState.ACTIVE:
                print("📞 Call answered, waiting 10 seconds...")
                # Сбрасываем через поток, чтобы не блокировать pjsua
                threading.Thread(target=self.delayed_hangup).start()

        def delayed_hangup(self):
            time.sleep(10)
            print("❌ Hanging up")
            self.call.hangup()

    # ======== Callback для аккаунта ========
    class AccountCallback(pj.AccountCallback):
        def __init__(self, account):
            super().__init__(account)

        def on_incoming_call(self, call):
            print("📞 Incoming call")
            call_cb = CallCallback(call)
            call.set_callback(call_cb)
            call.answer(200)  # автоматически отвечаем

    acc.set_callback(AccountCallback(acc))

    print("✅ SIP bot ready and registered. Waiting for calls...")

    # ======== Основной цикл ========
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    lib.destroy()
    lib = None