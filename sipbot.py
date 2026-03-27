from pybaresip import Baresip
import time

gateway = "181571.voice.plusofon.ru"
user = "21261774115582"
pswd = "FlvUenbQ"


class MyVoiceBot(Baresip):
    def on_incoming_call(self, call, number):
        print(f"Входящий звонок от: {number}")
        call.answer()  # отвечаем на вызов

    def on_call_established(self, call):
        print("Звонок установлен, говорю...")
        call.speak("Здравствуйте! Вас приветствует голосовой бот.")
        call.speak("Спасибо за звонок. До свидания.")
        call.hangup()

    def on_call_ended(self, call, reason):
        print(f"Вызов завершён: {reason}")


bot = MyVoiceBot(
    username=user,
    password=pswd,
    domain=gateway,
    proxy=gateway,
    transport="tcp"
)

bot.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    bot.stop()