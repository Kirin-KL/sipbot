import time
import os
from python_sip_client import BareSIP

# --- КОНФИГУРАЦИЯ ---
# Путь к вашему аудиофайлу (рекомендуется формат .wav)
AUDIO_FILE_PATH = "/home/user/voice_message.wav" # ИЗМЕНИТЕ ЭТОТ ПУТЬ
SIP_USER = "your_username"    # ИЗМЕНИТЕ
SIP_PASSWORD = "your_password" # ИЗМЕНИТЕ
SIP_DOMAIN = "sip.provider.com" # ИЗМЕНИТЕ
# --------------------

# Флаг для отслеживания, был ли уже воспроизведен файл
# Чтобы не запустить воспроизведение повторно по лишним событиям
message_played = False

def handle_incoming_call(from_uri):
    """Функция, вызываемая при входящем звонке"""
    global message_played
    print(f"[СОБЫТИЕ] Входящий звонок от: {from_uri}")

    # Сбрасываем флаг для нового звонка
    message_played = False

    # Отвечаем на звонок
    print("-> Отвечаю на звонок...")
    bs.answer()

def handle_call_established():
    """Функция, вызываемая, когда звонок установлен (собеседник поднял трубку)"""
    global message_played
    print("[СОБЫТИЕ] Звонок установлен.")

    # Проверяем, существует ли файл
    if not os.path.exists(AUDIO_FILE_PATH):
        print(f"ОШИБКА: Аудиофайл не найден по пути {AUDIO_FILE_PATH}")
        return

    # Если сообщение еще не было воспроизведено в этом звонке
    if not message_played:
        print(f"-> Воспроизвожу аудиофайл: {AUDIO_FILE_PATH}")
        # Воспроизводим файл
        # Этот метод блокирует выполнение до окончания воспроизведения
        bs.play_audio(AUDIO_FILE_PATH)
        message_played = True
        print("-> Аудио воспроизведено.")

        # Небольшая пауза перед сбросом звонка
        time.sleep(1)
        print("-> Завершаю звонок.")
        bs.hangup()

# --- ИНИЦИАЛИЗАЦИЯ И ЗАПУСК ---
if __name__ == "__main__":
    # 1. Создаем экземпляр клиента
    # debug=True поможет увидеть детальные логи baresip для отладки
    bs = BareSIP(debug=True)

    # 2. Назначаем обработчики событий
    bs.on(BareSIP.Event.INCOMING_CALL, handle_incoming_call)
    bs.on(BareSIP.Event.CALL_ESTABLISHED, handle_call_established)

    try:
        # 3. Запускаем процесс baresip
        print("Запуск BareSIP...")
        bs.start()

        # 4. Регистрируем наш аккаунт на сервере
        print(f"Регистрация аккаунта {SIP_USER}@{SIP_DOMAIN}...")
        bs.create_user_agent(SIP_USER, SIP_PASSWORD, SIP_DOMAIN)

        # 5. Ждем успешной регистрации (необходимо для приема звонков)
        print("Ожидание регистрации...")
        # Простой цикл ожидания, пока не получим статус "зарегистрирован"
        # user_agents() возвращает список объектов UserAgent
        registered = False
        while not registered:
            uas = bs.user_agents()
            if uas and uas[0].registered:
                registered = True
                print("Регистрация успешна! Ожидание входящих звонков...")
            else:
                time.sleep(1)

        # 6. Бесконечный цикл для поддержания работы скрипта
        # Программа будет работать, пока мы не прервем ее (Ctrl+C)
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nОстановка скрипта...")
    finally:
        # 7. Корректно останавливаем baresip
        print("Остановка BareSIP...")
        bs.stop()
        print("Завершено.")