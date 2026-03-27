from baresipy import BareSIP
from time import sleep

# --- ВАЖНО: Замените на свои реальные данные от SIP-провайдера ---
MY_SIP_USER = "21261774115582"           # например, "alice"
MY_SIP_PASS = "FlvUenbQ"          # например, "strongpassword"
MY_SIP_GATEWAY = "181571.voice.plusofon.ru" # например, "sip.orange.com"
# ---------------------------------------------------------------

class MyVoiceBot(BareSIP):
    def handle_incoming_call(self, number):
        print(f"📞 Входящий звонок от: {number}")
        self.accept_call()

    def handle_call_established(self):
        print("✅ Звонок установлен, говорю...")
        self.speak("Здравствуйте! Вас приветствует голосовой бот.")
        # Добавьте паузу между фразами, чтобы не "наезжать" на речь
        sleep(1)
        self.speak("Спасибо за звонок. До свидания.")
        sleep(1)
        self.hang()

    def handle_call_ended(self, reason):
        print(f"❌ Вызов завершён: {reason}")

# Запуск бота с реальными данными
bot = MyVoiceBot(MY_SIP_USER, MY_SIP_PASS, MY_SIP_GATEWAY)

print("🤖 Бот запущен и ожидает звонки...")
while bot.running:
    sleep(1)