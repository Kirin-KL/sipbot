import pjsua as pj

def log_cb(level, msg, length):
    print(msg)

lib = pj.Lib()

lib.init(log_cfg=pj.LogConfig(level=4, callback=log_cb))

transport = lib.create_transport(
    pj.TransportType.TCP,
    pj.TransportConfig(5060)
)

lib.start()

acc_cfg = pj.AccountConfig(
    domain="181571.voice.plusofon.ru",
    username="21261774115582",
    password="FlvUenbQ",
    proxy=["sip:181571.voice.plusofon.ru;transport=tcp"],
)

acc = lib.create_account(acc_cfg)

print("Регистрация отправлена. Нажми Enter для выхода.")
input()

lib.destroy()
