from typing import Tuple, List, Dict
from functools import wraps


def parse_input(user_input: str) -> Tuple[str, List[str]]:
    """
    Парсер команд:
    - приймає сирий рядок від користувача;
    - прибирає пробіли по краях;
    - розбиває на команду (перше слово) та аргументи (решта);
    - команда приводиться до нижнього регістру.
    """
    parts = user_input.strip().split()
    if not parts:
        return "", []
    cmd, *args = parts
    return cmd.lower(), args


# -----------------------------
# ДЕКОРАТОР ОБРОБКИ ПОМИЛОК
# -----------------------------
def input_error(func):
    """Перехоплює типові помилки вводу і повертає дружні повідомлення."""
    
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except IndexError:
            # зазвичай виникає, коли не передали обов'язковий аргумент (name)
            return "Enter user name."
        except TypeError:
            return "Wrong number of arguments."
        except ValueError as e:
            # неправильна кількість/формат аргументів
            return str(e) + "\n"+ "Enter the arguments for the command" if str(e) else "Give me name and phone please."
    return inner


# -----------------------------
# ХЕНДЛЕРИ КОМАНД (із декоратором)
# -----------------------------

@input_error
def add_contact(args: List[str], contacts: Dict[str, str]) -> str:
    """
    Додає новий контакт.
    Помилки:
      - ValueError: якщо передано не рівно 2 аргументи.
    """
    # if len(args) != 2:  # потрібна перевірка крім декоратора для більш дружнього повідомлення
     #   raise ValueError("Usage: add <name> <phone>")
    name, phone = args
    contacts[name] = phone
    return "Contact added."

@input_error
def change_contact(args: List[str], contacts: Dict[str, str]) -> str:
    """
    Змінює номер існуючого контакту.
    Помилки:
      - ValueError: якщо передано не рівно 2 аргументи.
      - KeyError: якщо контакту не існує.
    """
    # if len(args) != 2:   # потрібна перевірка крім декоратора для більш дружнього повідомлення
    #    raise ValueError("Usage: change <name> <new_phone>")
    name, phone = args
    if name not in contacts:
        raise KeyError(name)
    contacts[name] = phone
    return "Contact updated."

@input_error
def show_phone(args: List[str], contacts: Dict[str, str]) -> str:
    """
    Повертає номер телефону за ім'ям.
    Помилки:
      - IndexError: якщо не передали ім'я.
      - KeyError: якщо контакту з таким ім'ям немає.
    """
    name = args[0]              # IndexError, якщо args порожній -> спіймає декоратор
    return contacts[name]       # KeyError, якщо name відсутній -> спіймає декоратор

def show_all(contacts: Dict[str, str]) -> str:
    """Виводить усі контакти."""
    if not contacts:
        return "No contacts."
    return "\n".join(f"{name}: {phone}" for name, phone in contacts.items())


# -----------------------------
# ГОЛОВНИЙ ЦИКЛ ПРОГРАМИ (CLI)
# -----------------------------
def main() -> None:
    contacts: Dict[str, str] = {}
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ("close", "exit"):
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, contacts))
        elif command == "change":
            print(change_contact(args, contacts))
        elif command == "phone":
            print(show_phone(args, contacts))
        elif command == "all":
            print(show_all(contacts))
        elif command == "":
            continue
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
