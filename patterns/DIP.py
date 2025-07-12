# Демонстрация принципа инверсии зависимостей (DIP) на примере отправки уведомлений в интернет-магазине.
# Код показывает, как нарушение DIP привязывает код к конкретным реализациям, а соблюдение DIP делает его гибким и независимым.

from abc import ABC, abstractmethod
from enum import Enum
from typing import List

'''
DIP - Принцип инверсии зависимостей
DIP -> Dependency Inversion Principle
  Модули высокого уровня не должны зависеть от модулей низкого уровня. Оба должны зависеть от абстракций.
  Абстракции не должны зависеть от деталей реализации. Детали реализации должны зависеть от абстракций.
Пример: Если у тебя есть класс для обработки заказа, он не должен зависеть от конкретной системы отправки уведомлений
    (например, EmailService). Вместо этого он должен зависеть от абстрактного интерфейса уведомлений.
Более детальное описание в конце кода.
'''

# --- Перечисления для атрибутов товара ---
class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

# --- Класс товара ---
class Product:
    """
    Класс, представляющий товар в магазине.
    Его единственная ответственность — хранить данные о товаре (название, цвет, цена).
    Это соответствует SRP и помогает в контексте DIP, так как товар не зависит от логики уведомлений.
    """
    def __init__(self, name: str, color: Color, price: float):
        self.name = name
        self.color = color
        self.price = price

# --- Класс заказа ---
class Order:
    """
    Класс, представляющий заказ. Хранит список товаров.
    """
    def __init__(self, products: List[Product]):
        self.products = products

# --- Пример нарушения DIP ---
class EmailServiceBad:
    """
    Конкретная реализация отправки уведомлений по email.
    """
    def send_email(self, order: Order) -> None:
        print(f"Email sent: Order with {len(order.products)} items has been processed!")

class OrderProcessorBad:
    """
    Класс для обработки заказа.
    Нарушение DIP: зависит от конкретного класса EmailServiceBad, а не от абстракции.
    Проблема: если нужно добавить SMS-уведомления, придётся менять код OrderProcessorBad.
    """
    def __init__(self):
        self.email_service = EmailServiceBad()  # Жёсткая зависимость от конкретной реализации

    def process_order(self, order: Order):
        print(f"Processing order with {len(order.products)} items...")
        self.email_service.send_email(order)

# --- Пример соблюдения DIP ---
class NotificationService(ABC):
    """
    Абстрактный интерфейс для отправки уведомлений.
    Это абстракция, от которой зависят высокоуровневые классы (OrderProcessor).
    """
    @abstractmethod
    def send_notification(self, order: Order) -> None:
        pass

class EmailService(NotificationService):
    """
    Реализация отправки уведомлений по email.
    Зависит от абстракции NotificationService, что соответствует DIP.
    """
    def send_notification(self, order: Order) -> None:
        print(f"Email sent: Order with {len(order.products)} items has been processed!")

class SmsService(NotificationService):
    """
    Реализация отправки уведомлений по SMS.
    Зависит от абстракции NotificationService, что позволяет легко добавить новый способ уведомления.
    """
    def send_notification(self, order: Order) -> None:
        print(f"SMS sent: Order with {len(order.products)} items has been processed!")

class OrderProcessor:
    """
    Класс для обработки заказа.
    Соблюдает DIP: зависит от абстракции NotificationService, а не от конкретной реализации.
    Можно передать любой класс, реализующий NotificationService (например, EmailService или SmsService).
    """
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service  # Зависимость от абстракции

    def process_order(self, order: Order):
        print(f"Processing order with {len(order.products)} items...")
        self.notification_service.send_notification(order)

# --- Демонстрация использования ---
def main():
    """
    Показывает, как работают оба подхода:
    - OrderProcessorBad: нарушает DIP, завися от конкретного класса EmailServiceBad.
    - OrderProcessor: соблюдает DIP, завися от абстракции NotificationService.
    """
    # Создаём тестовый заказ
    products = [
        Product("T-Shirt", Color.RED, 20.0),
        Product("Table", Color.GREEN, 150.0),
    ]
    order = Order(products)

    # --- Нарушение DIP ---
    print("=== Нарушение DIP (OrderProcessorBad) ===")
    bad_processor = OrderProcessorBad()
    bad_processor.process_order(order)

    # --- Соблюдение DIP ---
    print("\n=== Соблюдение DIP (OrderProcessor) ===")
    email_service = EmailService()
    sms_service = SmsService()

    processor_email = OrderProcessor(email_service)
    print("Обработка заказа с email-уведомлением:")
    processor_email.process_order(order)

    processor_sms = OrderProcessor(sms_service)
    print("\nОбработка заказа с SMS-уведомлением:")
    processor_sms.process_order(order)

if __name__ == "__main__":
    main()

'''
Принцип инверсии зависимостей (Dependency Inversion Principle) — гласит:
  Модули высокого уровня не должны зависеть от модулей низкого уровня. Оба должны зависеть от абстракций.
  Абстракции не должны зависеть от деталей реализации. Детали реализации должны зависеть от абстракций.
  Это означает, что высокоуровневый класс (например, OrderProcessor) должен зависеть от интерфейса
  (NotificationService), а не от конкретной реализации (EmailService или SmsService).

Пример из кода:
  В плохом подходе (OrderProcessorBad) класс напрямую зависит от EmailServiceBad.
  Если нужно добавить SMS-уведомления, придётся менять код OrderProcessorBad.
  В хорошем подходе (OrderProcessor) класс зависит от абстракции NotificationService.
  Это позволяет легко добавить SmsService или другие способы уведомлений без изменения OrderProcessor.

Почему нужно использовать DIP?
  DIP помогает создавать гибкие и независимые системы. Без DIP высокоуровневые классы привязаны к конкретным
  реализациям, что затрудняет добавление новых функций и увеличивает риск ошибок.

Когда DIP особенно важен:
  - Частые изменения требований: Если в интернет-магазине нужно добавить новый способ уведомлений
      (например, push-уведомления), DIP позволяет сделать это без изменения высокоуровневого кода.
  - Большие проекты: В крупных системах жёсткие зависимости от конкретных реализаций усложняют поддержку.
  - Командная разработка: Когда разные разработчики работают над разными модулями, DIP снижает конфликты,
      так как модули зависят от абстракций.
  - Тестирование: Код, следующий DIP, легче тестировать, так как можно подставить заглушки (mocks)
      вместо реальных реализаций.

Пример из реальной жизни:
  В интернет-магазине система отправляет уведомления о покупке (email, SMS, push).
  Если класс обработки заказа зависит от конкретного EmailService, добавление SMS потребует изменения кода.
  DIP позволяет зависеть от абстракции NotificationService, так что новый способ уведомлений
  (например, PushService) добавляется без изменения высокоуровневого кода.

Преимущества DIP
  - Гибкость: Можно добавлять новые реализации (например, SmsService) без изменения высокоуровневых классов.
  - Меньше ошибок: Изменение деталей реализации не ломает высокоуровневый код.
  - Тестирование: Легко подставить заглушки или моки для тестирования, так как зависимости инжектируются.
  - Модульность: Код разделён на независимые части, каждая из которых зависит от абстракций.
  - Переиспользуемость: Абстракции (как NotificationService) можно использовать в разных контекстах.

Пример из кода:
  Класс OrderProcessor зависит от абстракции NotificationService.
  Это позволяет использовать EmailService, SmsService или любую другую реализацию без изменения кода.

Недостатки и ограничения DIP
  - Усложнение кода: Создание абстракций и инжектирование зависимостей увеличивает количество кода.
  - Сложность проектирования: Нужно заранее продумать абстракции, что требует опыта.
  - Избыточность для маленьких проектов: Если система простая (например, только email-уведомления),
      DIP может быть избыточным.

Когда DIP не нужен:
  - Если проект маленький и не предполагает изменения реализаций (например, всегда только email).
  - Если ты пишешь прототип, где важна скорость, а не поддержка.
  - Если зависимости стабильны и не будут меняться.

Как понять, что DIP нарушен?
  - Высокоуровневый класс зависит от конкретной реализации (например, OrderProcessorBad зависит от EmailServiceBad).
  - Добавление новой функциональности требует изменения высокоуровневого кода.
  - Трудно заменить реализацию (например, EmailService на SmsService) без правки кода.

Пример из кода:
  В OrderProcessorBad высокоуровневый класс зависит от конкретного EmailServiceBad.
  В хорошем подходе OrderProcessor зависит от абстракции NotificationService, что позволяет легко добавить SmsService.

Как применять DIP?
  - Создавать абстракции: Используй интерфейсы или абстрактные классы (как NotificationService)
      для определения контрактов.
  - Инжектировать зависимости: Передавай зависимости через конструктор или методы, а не создавай их внутри класса.
  - Избегать жёстких зависимостей: Не используй конкретные классы (например, EmailService) в высокоуровневых модулях.
  - Использовать DI-контейнеры: В крупных проектах можно применять библиотеки (например, Python's `dependency-injector`)
      для управления зависимостями.

Пример из кода:
  Класс OrderProcessor принимает NotificationService через конструктор.
  Это позволяет передавать EmailService, SmsService или любую другую реализацию, не меняя код OrderProcessor.
'''