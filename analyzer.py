import re
import os
from datetime import datetime

# --- Цвета для Linux консоли ---
class Colors:
    HEADER = '\033[95m'    # Фиолетовый
    OKBLUE = '\033[94m'    # Синий
    OKCYAN = '\033[96m'    # Голубой
    OKGREEN = '\033[92m'   # Зеленый
    WARNING = '\033[93m'   # Желтый
    FAIL = '\033[91m'      # Красный
    ENDC = '\033[0m'       # Сброс цвета
    BOLD = '\033[1m'       # Жирный

def c_print(text, color=Colors.ENDC):
    print(f"{color}{text}{Colors.ENDC}")

def parse_logs():
    log_filename = 'log.txt'

    if not os.path.exists(log_filename):
        c_print(f"Ошибка: Файл {log_filename} не найден.", Colors.FAIL)
        return

    c_print(f"--- Чтение файла {log_filename} (поиск успешных потоков) ---", Colors.HEADER)
    c_print("Идет обработка...\n", Colors.OKCYAN)

    # Регулярка: ID блока (необязательно), Время, Поток №
    log_pattern = re.compile(r'(?:\[\d+\]\s*)?\[(\d{2}:\d{2}:\d{2})\].*Поток №(\d+)\s*:')

    # Регулярка для очистки строки от ID блока при выводе
    cleanup_pattern = re.compile(r'^\[\d+\]\s*')

    success_marker = "Поток выполнен успешно"
    # Новый маркер начала потока
    start_marker = "Setting up proxy"

    try:
        with open(log_filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        found_count = 0

        # Идем с конца файла к началу
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()

            if not line:
                continue

            # 1. Ищем строку с успешным завершением
            if success_marker in line:
                match = log_pattern.search(line)
                
                if match:
                    end_time_str = match.group(1)
                    thread_id = match.group(2)

                    c_print("="*60, Colors.WARNING)
                    c_print(f"🎉 НАЙДЕН УСПЕШНЫЙ ПОТОК №{thread_id}", Colors.OKGREEN + Colors.BOLD)
                    c_print("="*60, Colors.WARNING)

                    thread_log_buffer = []
                    start_time_str = None
                    found_start = False

                    # Флаг для сбора многострочных сообщений
                    inside_target_block = False

                    # 2. Идем НАЗАД по логу, пока не найдем маркер начала
                    k = i - 1

                    while k >= 0:
                        prev_line = lines[k].strip()

                        if not prev_line:
                            k -= 1
                            continue

                        match_prev = log_pattern.search(prev_line)

                        if match_prev:
                            curr_thread_id = match_prev.group(2)
                            curr_time_str = match_prev.group(1)

                            # Если строка принадлежит нашему потоку
                            if curr_thread_id == thread_id:
                                inside_target_block = True
                                thread_log_buffer.append(prev_line)

                                # ПРОВЕРКА НАЧАЛА ПОТОКА
                                if start_marker in prev_line:
                                    start_time_str = curr_time_str
                                    found_start = True
                                    break  # Нашли старт - прерываем поиск
                                
                            else:
                                # Встретили другой поток - прерываем сбор (логи вперемешку)
                                inside_target_block = False
                        else:
                            # Строка без заголовка (продолжение предыдущей)
                            # Добавляем только если мы уже внутри блока нашего потока
                            if inside_target_block:
                                thread_log_buffer.append(prev_line)

                        k -= 1

                    # 3. Выводим результат
                    if thread_log_buffer:
                        c_print(f"\n--- Хронология событий (от {start_marker} к успеху) ---", Colors.OKBLUE)
                        # Разворачиваем список, чтобы показать от старта к успеху
                        for log_line in reversed(thread_log_buffer):
                            clean_line = cleanup_pattern.sub('', log_line)
                            
                            # Подсветка
                            if "Ошибка" in clean_line:
                                c_print(clean_line, Colors.FAIL)
                            elif "Поток выполнен успешно" in clean_line:
                                c_print(clean_line, Colors.OKGREEN)
                            elif start_marker in clean_line:
                                c_print(clean_line, Colors.WARNING)
                            else:
                                print(clean_line)
                    else:
                        c_print("(Лог не восстановлен)", Colors.FAIL)

                    # 4. Статистика
                    c_print(f"\n--- Статистика ---", Colors.BOLD)

                    try:
                        t_end = datetime.strptime(end_time_str, "%H:%M:%S")
                        
                        if found_start and start_time_str:
                            t_start = datetime.strptime(start_time_str, "%H:%M:%S")
                            duration = t_end - t_start
                            
                            # Обработка перехода через полночь (если скрипт работает сутками)
                            if duration.total_seconds() < 0:
                                from datetime import timedelta
                                duration += timedelta(days=1)

                            c_print(f"Старт (Proxy): {start_time_str}", Colors.WARNING)
                            c_print(f"Успех:         {end_time_str}", Colors.OKGREEN)
                            print(f"Длительность:   {duration}")
                        else:
                            c_print(f"Успех:         {end_time_str}", Colors.OKGREEN)
                            c_print(f"Старт:         Маркер '{start_marker}' НЕ НАЙДЕН в логах этого потока", Colors.FAIL)
                            print("Длительность:   Неизвестно")

                    except Exception as e:
                        c_print(f"Ошибка расчета времени: {e}", Colors.FAIL)

                    print("\n")
                    found_count += 1

        if found_count == 0:
            c_print("Успешных завершений не найдено.", Colors.FAIL)

    except Exception as e:
        c_print(f"Критическая ошибка: {e}", Colors.FAIL)

if __name__ == "__main__":
    parse_logs()
    