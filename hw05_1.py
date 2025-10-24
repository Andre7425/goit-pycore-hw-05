

from typing import Callable, Dict

def caching_fibonacci() -> Callable[[int], int]:
    """
    Повертає функцію fibonacci(n), яка рахує n-те число Фібоначчі.
    Результати кешуються у словнику `cache`, що зберігається в замиканні.

    cache живе всередині caching_fibonacci і залишається доступним для внутрішньої 
    функції fibonacci — це і є замикання.
    Перед поверненням результат записується до cache, тому повторні виклики 
    з тим самим n працюють миттєво.
    Базові випадки {0: 0, 1: 1} зменшують глибину рекурсії та спрощують код.
    """
    cache: Dict[int, int] = {0: 0, 1: 1}  # базові значення

    def fibonacci(n: int) -> int:
        if n < 0:
            return 0 # raise ValueError("n має бути невід’ємним цілим числом")
        # якщо є в кеші — одразу повертаємо
        if n in cache:
            return cache[n]
        # рекурсивне обчислення з використанням уже збережених значень
        cache[n] = fibonacci(n - 1) + fibonacci(n - 2)
        return cache[n]

    return fibonacci

# приклад використання      
fib = caching_fibonacci()

print(fib(10))  # 55
print(fib(15))  # 610
print(fib(10))  # 55 (береться з кешу, без повторних рекурсій)
print(fib(1))   # 1
print(fib(0))   # 0
print(fib(-5))  # 0 (за умовою завдання)


