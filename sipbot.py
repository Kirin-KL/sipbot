import time
import os
from python_sip_client import BareSIP
from python_sip_client import CallState

# --- КОНФИГУРАЦИЯ ---
# Путь к вашему аудиофайлу (рекомендуется формат .wav)
AUDIO_FILE_PATH = "/home/user/voice_message.wav" # ИЗМЕНИТЕ ЭТОТ ПУТЬ
SIP_USER = "21261774115582"    # ИЗМЕНИТЕ
SIP_PASSWORD = "FlvUenbQ" # ИЗМЕНИТЕ
SIP_DOMAIN = "181571.voice.plusofon.ru" # ИЗМЕНИТЕ

# --------------------

# Глобальные переменные
current_call = None
message_played = False


def handle_incoming_call(call):
    """Функция, вызываемая при входящем звонке"""
    global current_call, message_played

    print(f"[СОБЫТИЕ] Входящий звонок!")
    print(f"  От: {call.from_uri}")
    print(f"  Кому: {call.to_uri}")
    print(f"  Call ID: {call.id}")

    # Сохраняем информацию о звонке
    current_call = call
    message_played = False

    # Отвечаем на звонок
    print("-> Отвечаю на звонок...")
    call.answer()


def handle_call_state_changed(call, state):
    """Функция, вызываемая при изменении состояния звонка"""
    global message_played

    print(f"[СОБЫТИЕ] Состояние звонка изменилось: {state}")

    # Проверяем, установлено ли соединение (звонок активен)
    if state == CallState.ESTABLISHED:
        print("[СОБЫТИЕ] Звонок установлен (собеседник поднял трубку)")

        # Проверяем, существует ли файл
        if not os.path.exists(AUDIO_FILE_PATH):
            print(f"ОШИБКА: Аудиофайл не найден по пути {AUDIO_FILE_PATH}")
            return

        # Если сообщение еще не было воспроизведено
        if not message_played:
            print(f"-> Воспроизвожу аудиофайл: {AUDIO_FILE_PATH}")

            try:
                # Воспроизводим файл через call
                call.play_audio(AUDIO_FILE_PATH)
                message_played = True
                print("-> Аудио воспроизведено")

                # Небольшая пауза после воспроизведения
                time.sleep(2)

                # Завершаем звонок
                print("-> Завершаю звонок")
                call.hangup()

            except Exception as e:
                print(f"ОШИБКА при воспроизведении: {e}")

    # Если звонок завершен
    elif state == CallState.TERMINATED:
        print("[СОБЫТИЕ] Звонок завершен")
        global current_call
        current_call = None
        message_played = False


# --- ИНИЦИАЛИЗАЦИЯ И ЗАПУСК ---
if __name__ == "__main__":
    # 1. Создаем экземпляр клиента
    # debug=True поможет увидеть детальные логи baresip для отладки
    bs = BareSIP(debug=True)

    # 2. Назначаем обработчики событий
    # Используем правильные названия событий
    bs.on(BareSIP.Event.INCOMING_CALL, handle_incoming_call)
    bs.on(BareSIP.Event.CALL_STATE_CHANGED, handle_call_state_changed)

    try:
        # 3. Запускаем процесс baresip
        print("Запуск BareSIP...")
        bs.start()

        # 4. Регистрируем наш аккаунт на сервере
        print(f"Регистрация аккаунта {SIP_USER}@{SIP_DOMAIN}...")
        ua = bs.create_user_agent(SIP_USER, SIP_PASSWORD, SIP_DOMAIN)

        # 5. Ждем успешной регистрации
        print("Ожидание регистрации...")
        registered = False
        timeout = 30  # таймаут в секундах
        start_time = time.time()

        while not registered and (time.time() - start_time) < timeout:
            uas = bs.user_agents()
            if uas and len(uas) > 0:
                if uas[0].registered:
                    registered = True
                    print("✓ Регистрация успешна!")
                    print("Ожидание входящих звонков...")
                    print("Нажмите Ctrl+C для выхода\n")
                else:
                    print("  Статус: регистрация в процессе...")
                    time.sleep(2)
            else:
                print("  Ожидание создания User Agent...")
                time.sleep(1)

        if not registered:
            print("ОШИБКА: Не удалось зарегистрироваться за отведенное время")
            print("Проверьте:")
            print("  1. Правильность логина и пароля")
            print("  2. Доступность SIP-сервера")
            print("  3. Файл конфигурации accounts")
            bs.stop()
            exit(1)

        # 6. Бесконечный цикл для поддержания работы
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\nПолучен сигнал остановки...")
    except Exception as e:
        print(f"\nОШИБКА: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # 7. Корректно останавливаем baresip
        print("\nОстановка BareSIP...")
        if 'bs' in locals():
            bs.stop()
        print("Скрипт завершен")