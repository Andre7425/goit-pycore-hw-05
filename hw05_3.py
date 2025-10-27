#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from collections import Counter
from typing import Dict, List


# ---------- Парсинг однієї лінії логів ----------

def parse_log_line(line: str) -> dict:
    """
    Приймає рядок виду:
      YYYY-MM-DD HH:MM:SS LEVEL Message...
    Повертає словник: {"date": ..., "time": ..., "level": ..., "message": ...}
    Кидає ValueError для некоректного рядка.
    """
    # Прибираємо пробіли/переноси з країв — важливо, бо читаємо файл построково
    line = line.strip()
    # Порожню лінію вважаємо помилковою, щоб не намагатися її парсити
    if not line:
        raise ValueError("Empty log line")

    try:
        # Розбиваємо рядок на 4 частини:
        # 1) дата, 2) час, 3) рівень логування, 4) решта тексту — повідомлення
        # maxsplit=3 гарантує, що message залишиться «як є», навіть якщо містить пробіли
        date, time, level, message = line.split(maxsplit=3)
    except ValueError as e:
        # Якщо формат не відповідає очікуваному — видаємо інформативну помилку
        raise ValueError(f"Bad log line format: {line!r}") from e

    # Нормалізуємо рівень логування до ВЕРХНЬОГО регістру для уніфікації
    return {
        "date": date,
        "time": time,
        "level": level.upper(),
        "message": message,
    }


# ---------- Завантаження логів з файлу ----------

def load_logs(file_path: str) -> List[dict]:
    """
    Зчитує файл, парсить кожен рядок через parse_log_line.
    Порожні/пошкоджені рядки пропускає.
    """
    logs: List[dict] = []
    try:
        # utf-8-sig дозволяє прозоро читати файли з BOM (Windows-нотепад іноді додає)
        with open(file_path, encoding="utf-8-sig") as f:
            for raw in f:
                raw = raw.strip()
                # Ігноруємо порожні рядки між записами
                if not raw:
                    continue
                try:
                    # Парсимо лінію та додаємо готовий словник у колекцію
                    logs.append(parse_log_line(raw))
                except ValueError:
                    # Якщо рядок пошкоджено/непарситься — просто пропускаємо
                    continue
    except FileNotFoundError:
        # Немає файлу — повідомляємо у stderr і завершуємо з кодом 2
        print(f"Помилка: файл не знайдено: {file_path}", file=sys.stderr)
        sys.exit(2)
    except OSError as e:
        # Інші I/O проблеми (права доступу, блокування тощо)
        print(f"Помилка читання файлу: {e}", file=sys.stderr)
        sys.exit(3)

    return logs


# ---------- Фільтрація за рівнем ----------

def filter_logs_by_level(logs: List[dict], level: str) -> List[dict]:
    """
    Повертає всі записи, де log["level"] == level.upper().
    """
    # Нормалізуємо введений рівень, щоб «error» == «ERROR»
    lvl = level.upper()
    # Списковий вираз: залишаємо лише ті словники, де рівень збігається
    return [log for log in logs if log.get("level") == lvl]


# ---------- Підрахунок за рівнями ----------

def count_logs_by_level(logs: List[dict]) -> Dict[str, int]:
    """
    Рахує кількість записів для кожного рівня.
    Використовує Counter; повертає звичайний dict.
    """
    # Генератор рівнів із кожного запису -> Counter рахує частоти -> перетворюємо на звичайний dict
    return dict(Counter(log["level"] for log in logs))


# ---------- Форматований вивід таблиці ----------

def display_log_counts(counts: Dict[str, int]) -> None:
    """
    Друкує таблицю:
      Рівень логування | Кількість
    Показує INFO, DEBUG, ERROR, WARNING у такому порядку (як у прикладі).
    Інші рівні (якщо є у файлі) можна додати за бажанням.
    """
    # Фіксований порядок виводу — щоб результат був передбачуваним/зразковим
    order = ["INFO", "DEBUG", "ERROR", "WARNING"]

    # Шапка таблиці (проста ASCII-розмітка)
    print("Рівень логування | Кількість")
    print("-----------------|----------")

    # Для кожного «очікуваного» рівня беремо лічильник з dict (якщо немає — 0)
    # f"{lvl:<16}" — вирівнюємо назву рівня вліво на ширину 16 символів
    for lvl in order:
        print(f"{lvl:<16} | {counts.get(lvl, 0)}")


# ---------- Точка входу (CLI) ----------

def main() -> None:
    """
    Використання:
      python3 hw05_3.py /path/to/logfile.txt
      python3 hw05_3.py /path/to/logfile.txt error
    """
    # Перевіряємо, що передали принаймні 1 аргумент — шлях до файлу логів
    if len(sys.argv) < 2:
        print("Використання: python3 hw05_3.py <path/to/logfile.txt> [level]")
        sys.exit(1)

    # 1-й позиційний аргумент — шлях до лог-файлу
    file_path = sys.argv[1]
    # 2-й (необов’язковий) — рівень логування для детального виводу
    level = sys.argv[2] if len(sys.argv) >= 3 else None

    # Читаємо та парсимо логи
    logs = load_logs(file_path)
    # Рахуємо кількість записів за рівнями
    counts = count_logs_by_level(logs)
    # Друкуємо підсумкову таблицю
    display_log_counts(counts)

    # Якщо користувач запросив конкретний рівень — показуємо деталі
    if level:
        chosen = level.upper()
        details = filter_logs_by_level(logs, chosen)
        print(f"\nДеталі логів для рівня '{chosen}':")
        if not details:
            print("(немає записів)")
        else:
            # Списковий вираз: формуємо рядок «дата час - повідомлення» для кожного запису
            lines = [f"{d['date']} {d['time']} - {d['message']}" for d in details]
            # Виводимо усі рядки списком, кожен із нового рядка
            print("\n".join(lines))


# «Охоронець» модуля: main() виконається лише якщо файл запущено напряму,
# а не імпортовано як модуль у інший скрипт.
if __name__ == "__main__":
    main()
