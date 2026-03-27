from pysipp import SIPp, SIPpConfig

config = SIPpConfig(
    username="21261774115582",
    password="FlvUenbQ",
    domain="181571.voice.plusofon.ru",
    proxy="181571.voice.plusofon.ru",
    transport="tcp",
    local_ip="0.0.0.0",
    local_port=5060
)

ua = SIPp(config)

# Отправляем REGISTER
ua.register()
print("REGISTER sent")

# Делаем тестовый звонок
target = "sip:NUMBER@181571.voice.plusofon.ru"
ua.invite(target)
print("INVITE sent to", target)

# Ждём входящих сообщений
ua.listen()
