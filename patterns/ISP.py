# Демонстрация принципа разделения интерфейсов (ISP) на примере обработки заказов в интернет-магазине.
# Код показывает, как нарушение ISP заставляет классы реализовывать ненужные методы, а соблюдение ISP делает код гибким и понятным.

from abc import ABC, abstractmethod
from enum import Enum
from typing import List

'''
ISP - Принцип разделения интерфейсов
ISP -> Interface Segregation Principle
      Клиенты не должны зависеть от интерфейсов, которые они не используют.
Пример: Если у тебя есть интерфейс для работы с заказом, включающий методы для оплаты и отображения,
          то класс, который только отображает заказ, не должен быть вынужден реализовывать метод оплаты.
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
    Это соответствует SRP и помогает в контексте ISP, так как товар не зависит от логики заказов.
    """
    def __init__(self, name: str, color: Color, price: float):
        self.name = name
        self.color = color
        self.price = price

# --- Класс заказа ---
class Order:
    """
    Класс, представляющий заказ. Хранит список товаров и статус оплаты.
    """
    def __init__(self, products: List[Product]):
        self.products = products
        self.is_paid = False

# --- Пример нарушения ISP ---
class OrderProcessorBad(ABC):
    """
    Широкий интерфейс, включающий методы для разных задач: отображение, оплата, уведомления.
    Проблема: классы, реализующие этот интерфейс, вынуждены реализовывать методы,
     которые им не нужны (например, UI не нужна оплата, а платёжная система не отображает заказ).
    Это нарушает ISP, так как клиенты зависят от ненужных методов.
    """
    @abstractmethod
    def display_order(self, order: Order) -> str:
        pass

    @abstractmethod
    def process_payment(self, order: Order) -> bool:
        pass

    @abstractmethod
    def send_notification(self, order: Order) -> None:
        pass

class UIDisplayBad(OrderProcessorBad):
    """
    Класс для отображения заказа в UI.
    Нарушение ISP: вынужден реализовывать process_payment и send_notification, которые ему не нужны.
    """
    def display_order(self, order: Order) -> str:
        result = "Order items:\n"
        for product in order.products:
            result += f"- {product.name} ({product.color.name}, ${product.price})\n"
        return result

    def process_payment(self, order: Order) -> bool:
        raise NotImplementedError("UI does not handle payments")

    def send_notification(self, order: Order) -> None:
        raise NotImplementedError("UI does not send notifications")

class PaymentSystemBad(OrderProcessorBad):
    """
    Класс для обработки оплаты.
    Нарушение ISP: вынужден реализовывать display_order и send_notification, которые ему не нужны.
    """
    def display_order(self, order: Order) -> str:
        raise NotImplementedError("Payment system does not display orders")

    def process_payment(self, order: Order) -> bool:
        order.is_paid = True
        return True

    def send_notification(self, order: Order) -> None:
        raise NotImplementedError("Payment system does not send notifications")

# --- Пример соблюдения ISP ---
class OrderDisplay(ABC):
    """
    Узкий интерфейс только для отображения заказа.
    Классы, которым нужно только отображение, реализуют только этот интерфейс.
    """
    @abstractmethod
    def display_order(self, order: Order) -> str:
        pass

class OrderPayment(ABC):
    """
    Узкий интерфейс только для обработки оплаты.
    Классы, которым нужна только оплата, реализуют только этот интерфейс.
    """
    @abstractmethod
    def process_payment(self, order: Order) -> bool:
        pass

class OrderNotification(ABC):
    """
    Узкий интерфейс только для отправки уведомлений.
    Классы, которым нужна только отправка уведомлений, реализуют только этот интерфейс.
    """
    @abstractmethod
    def send_notification(self, order: Order) -> None:
        pass

class UIDisplay(OrderDisplay):
    """
    Класс для отображения заказа в UI.
    Соблюдает ISP: реализует только display_order, так как UI не занимается оплатой или уведомлениями.
    """
    def display_order(self, order: Order) -> str:
        result = "Order items:\n"
        for product in order.products:
            result += f"- {product.name} ({product.color.name}, ${product.price})\n"
        return result

class PaymentSystem(OrderPayment):
    """
    Класс для обработки оплаты.
    Соблюдает ISP: реализует только process_payment, так как не занимается отображением или уведомлениями.
    """
    def process_payment(self, order: Order) -> bool:
        order.is_paid = True
        return True

class NotificationSystem(OrderNotification):
    """
    Класс для отправки уведомлений.
    Соблюдает ISP: реализует только send_notification, так как не занимается отображением или оплатой.
    """
    def send_notification(self, order: Order) -> None:
        print(f"Email sent: Order with {len(order.products)} items has been processed!")

class OrderProcessor:
    """
    Класс, координирующий работу с заказами.
    Работает с узкими интерфейсами (OrderDisplay, OrderPayment, OrderNotification), что соответствует ISP.
    """
    def __init__(self, display: OrderDisplay, payment: OrderPayment, notification: OrderNotification):
        self.display = display
        self.payment = payment
        self.notification = notification

    def process_order(self, order: Order):
        print(self.display.display_order(order))
        if self.payment.process_payment(order):
            self.notification.send_notification(order)

# --- Демонстрация использования ---
def main():
    """
    Показывает, как работают оба подхода:
    - UIDisplayBad, PaymentSystemBad: нарушают ISP, реализуя ненужные методы.
    - UIDisplay, PaymentSystem, NotificationSystem: соблюдают ISP, реализуя только нужные методы.
    """
    # Создаём тестовый заказ
    products = [
        Product("T-Shirt", Color.RED, 20.0),
        Product("Table", Color.GREEN, 150.0),
    ]
    order = Order(products)

    # --- Нарушение ISP ---
    print("=== Нарушение ISP (UIDisplayBad, PaymentSystemBad) ===")
    ui_bad = UIDisplayBad()
    payment_bad = PaymentSystemBad()

    print("UI пытается отобразить заказ:")
    print(ui_bad.display_order(order))
    try:
        ui_bad.process_payment(order)  # Ошибка: UI не должен заниматься оплатой
    except NotImplementedError as e:
        print(f"Ошибка: {e}")

    print("\nПлатёжная система пытается обработать оплату:")
    payment_bad.process_payment(order)
    try:
        payment_bad.display_order(order)  # Ошибка: платёжная система не должна отображать
    except NotImplementedError as e:
        print(f"Ошибка: {e}")

    # --- Соблюдение ISP ---
    print("\n=== Соблюдение ISP (UIDisplay, PaymentSystem, NotificationSystem) ===")
    ui = UIDisplay()
    payment = PaymentSystem()
    notification = NotificationSystem()
    processor = OrderProcessor(ui, payment, notification)
    processor.process_order(order)

if __name__ == "__main__":
    main()

'''
Принцип разделения интерфейсов (Interface Segregation Principle) — гласит:
  Клиенты не должны зависеть от интерфейсов, которые они не используют. Это означает, что интерфейсы должны быть
  узкими и содержать только те методы, которые нужны конкретному клиенту.

Пример из кода:
  В плохом подходе (OrderProcessorBad) интерфейс включает методы display_order, process_payment и send_notification.
  Класс UIDisplayBad вынужден реализовывать process_payment и send_notification, хотя они ему не нужны,
    что приводит к NotImplementedError. То же с PaymentSystemBad, который не должен отображать заказ.
  В хорошем подходе интерфейсы разделены:
    - OrderDisplay — только для отображения.
    - OrderPayment — только для оплаты.
    - OrderNotification — только для уведомлений.
  Это делает код чище, так как каждый класс реализует только нужные методы.

Почему нужно использовать ISP?
  ISP помогает создавать понятные и гибкие системы. Без ISP классы вынуждены реализовывать ненужные методы,
  что увеличивает сложность, риск ошибок и затрудняет поддержку.

Когда ISP особенно важен:
  - Разные клиенты: Если разные части системы (UI, платёжная система, уведомления) используют один объект
      (например, заказ), ISP гарантирует, что каждая часть зависит только от нужных методов.
  - Большие проекты: В крупных системах широкие интерфейсы приводят к запутанному коду и ненужным зависимостям.
  - Командная разработка: Когда разные разработчики работают над разными частями системы, ISP снижает конфликты,
      так как каждый работает с узким интерфейсом.
  - Тестирование: Узкие интерфейсы легче тестировать, так как классы реализуют только необходимые методы.

Пример из реальной жизни:
  В интернет-магазине UI отображает заказ, платёжная система обрабатывает оплату, а система уведомлений
    отправляет письма. Если все они используют один широкий интерфейс, UI вынужден "знать" про оплату,
    что бессмысленно и усложняет код. ISP разделяет интерфейсы, чтобы каждая система работала только
    с нужными методами.

Преимущества ISP
  - Простота: Классы реализуют только те методы, которые им нужны, что делает код понятнее.
  - Меньше ошибок: Нет ненужных методов, которые могут быть вызваны по ошибке или требуют заглушек (
      NotImplementedError).
  - Гибкость: Можно добавлять новые интерфейсы и классы без изменения существующих.
  - Лёгкость тестирования: Тестировать классы проще, так как они реализуют только релевантные методы.
  - Модульность: Код разделён на независимые части, каждая из которых отвечает за свою задачу.

Пример из кода:
  Класс UIDisplay реализует только display_order, PaymentSystem — только process_payment,
    NotificationSystem — только send_notification. OrderProcessor использует эти узкие интерфейсы,
  что делает систему гибкой и понятной.

Недостатки и ограничения ISP
  - Больше интерфейсов: Вместо одного широкого интерфейса нужно создавать несколько узких,
      что увеличивает количество кода.
  - Сложность проектирования: Нужно заранее продумать, какие интерфейсы понадобятся разным клиентам,
      что требует опыта.
  - Усложнение для маленьких проектов: Если система простая (например, только UI и никаких оплат),
      ISP может быть избыточным.

Когда ISP не нужен:
  - Если проект маленький и использует только один тип клиента (например, только UI).
  - Если ты пишешь прототип, где важна скорость, а не поддержка.
  - Если интерфейсы не будут расширяться или разделяться.

Как понять, что ISP нарушен?
  - Классы реализуют ненужные методы (например, UIDisplayBad реализует process_payment).
  - Часто встречаются заглушки (NotImplementedError) или пустые методы.
  - Клиенты зависят от методов, которые им не нужны, что усложняет код и увеличивает риск ошибок.

Пример из кода:
  В OrderProcessorBad классы UIDisplayBad и PaymentSystemBad вынуждены реализовывать ненужные методы,
    что приводит к ошибкам и заглушкам. В хорошем подходе каждый класс реализует только то,
    что ему нужно, благодаря узким интерфейсам.

Как применять ISP?
  - Разделять интерфейсы: Создавай узкие интерфейсы для каждой задачи (например, OrderDisplay для отображения,
      OrderPayment для оплаты).
  - Определять нужды клиентов: Подумай, какие методы нужны конкретному классу, и создавай интерфейс только для них.
  - Использовать композицию: Класс OrderProcessor комбинирует узкие интерфейсы, чтобы координировать работу.
  - Избегать широких интерфейсов: Не создавай интерфейсы, включающие методы, которые не нужны всем клиентам.

Пример из кода:
  Интерфейсы OrderDisplay, OrderPayment и OrderNotification разделены по задачам.
  UIDisplay реализует только отображение, PaymentSystem — только оплату, NotificationSystem — только уведомления.
  Это делает код гибким и понятным.
'''