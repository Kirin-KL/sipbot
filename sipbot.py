from baresipy import BareSIP
from time import sleep

# Передаём фиктивные данные — baresipy требует их, но мы НЕ даём ему создавать аккаунт
FAKE_USER = "dummy"
FAKE_PASS = "dummy"
FAKE_GATEWAY = "dummy"

class MyVoiceBot(BareSIP):
    def handle_incoming_call(self, number):
        print(f"Входящий звонок от: {number}")
        self.accept_call()

    def handle_call_established(self):
        print("Звонок установлен, говорю...")
        self.speak("Здравствуйте! Вас приветствует голосовой бот.")
        self.speak("Спасибо за звонок. До свидания.")
        self.hang()

    def handle_call_ended(self, reason):
        print(f"Вызов завершён: {reason}")

bot = MyVoiceBot(FAKE_USER, FAKE_PASS, FAKE_GATEWAY)

while bot.running:
    sleep(1)
