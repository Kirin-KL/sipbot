from baresipy import BareSIP
from time import sleep

gateway = "181571.voice.plusofon.ru"
user = "21261774115582"
pswd = "FlvUenbQ"

class MyVoiceBot(BareSIP):
    def handle_incoming_call(self, number):
        print(f"Входящий звонок от {number}")
        self.accept_call()

    def handle_call_established(self):
        print("Звонок установлен, говорю...")
        self.speak("Здравствуйте! Вас приветствует голосовой бот.")
        self.speak("Спасибо за звонок. До свидания.")
        self.hang()

bot = MyVoiceBot(user, pswd, gateway)

while bot.running:
    sleep(1)
