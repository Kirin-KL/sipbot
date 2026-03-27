from baresipy import BareSIP
from time import sleep

gateway = "181571.voice.plusofon.ru"
user = "21261774115582"
pswd = "FlvUenbQ"


class MyVoiceBot(BareSIP):
    # Входящий вызов
    def handle_incoming_call(self, number):
        print(f"Входящий звонок от: {number}")
        self.accept_call()  # автоответ

    # Вызов установлен
    def handle_call_established(self):
        print("Звонок установлен, говорю...")
        self.speak("Здравствуйте! Вас приветствует голосовой бот.")
        self.speak("Спасибо за звонок. До свидания.")
        self.hang()

    # Вызов завершён
    def handle_call_ended(self, reason):
        print(f"Вызов завершён: {reason}")


bot = MyVoiceBot(user, pswd, gateway)

while bot.running:
    sleep(1)
