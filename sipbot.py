from python_sip_client import BareSIP

def on_call(from_uri):
    print("Входящий звонок:", from_uri)
    bs.answer()
    bs.play("/path/to/your.wav")   # можно проиграть TTS-файл
    # или позже: bs.hangup()

bs = BareSIP(debug=False)
bs.on(BareSIP.Event.INCOMING_CALL, on_call)

bs.start()
bs.create_user_agent("login", "password", "sip.server.com")

# держим процесс живым
while True:
    pass
