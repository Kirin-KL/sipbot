import pjsua as pj
import time

SIP_DOMAIN = "sip:21261774115582@181571.voice.plusofon.ru"
SIP_USER = "21261774115582"
SIP_PASS = "FlvUenbQ"


def log_cb(level, msg, length):
    print(msg)


lib = pj.Lib()

try:
    lib.init(log_cfg=pj.LogConfig(level=3, callback=log_cb))

    # для VPS без аудио
    lib.set_null_snd_dev()

    transport = lib.create_transport(pj.TransportType.UDP)
    lib.start()

    acc = lib.create_account(pj.AccountConfig(
        domain=SIP_DOMAIN,
        username=SIP_USER,
        password=SIP_PASS
    ))

    class CallCallback(pj.CallCallback):
        def __init__(self, call):
            super().__init__(call)

        def on_state(self):
            print("Call state:", self.call.info().state_text)

        def on_media_state(self):
            if self.call.info().media_state == pj.MediaState.ACTIVE:
                print("📞 Call answered, waiting 10 seconds...")

                time.sleep(10)

                print("❌ Hanging up")
                self.call.hangup()

    class AccountCallback(pj.AccountCallback):
        def __init__(self, account):
            super().__init__(account)

        def on_incoming_call(self, call):
            print("📞 Incoming call")

            call_cb = CallCallback(call)
            call.set_callback(call_cb)

            # отвечаем
            call.answer(200)

    acc.set_callback(AccountCallback(acc))

    print("✅ Ready...")

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    lib.destroy()