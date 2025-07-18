# Демонстрация принципа единственной ответственности (SRP) на примере управления товарами в интернет-магазине.
# Код показывает, как нарушение SRP усложняет поддержку, и как его соблюдение делает код гибким и понятным.

from enum import Enum
from typing import List

"""
SRP (Single Responsibility Principle) — принцип, который говорит: каждый класс должен делать только одну вещь.
- Класс — это как работник в магазине: у него должна быть одна задача (например, хранить данные о товаре).
- Если класс делает много дел (хранит данные, отображает товары, отправляет письма), он становится сложным и хрупким.

Пример: Представь, что у тебя есть машина (объект). Один класс отвечает за двигатель, другой за колёса, третий за покраску.
Если один класс отвечает за всё сразу, то любое изменение (например, новый тип двигателя) потребует переписывать весь код.
SRP разделяет задачи, чтобы изменения в одной части не ломали другую.
"""


# --- Перечисления для атрибутов товара ---
class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


# --- Класс товара ---
class Product:
    """
    Класс, представляющий товар в магазине. Его единственная ответственность — хранить данные о товаре.
    Это соответствует SRP: если нужно изменить формат данных (например, добавить цену), меняется только этот класс.
    """

    def __init__(self, name: str, color: Color, price: float):
        self.name = name
        self.color = color
        self.price = price


# --- Пример нарушения SRP ---
class ProductManagerBad:
    """
    Плохой подход: класс делает слишком много вещей.
    - Хранит данные о товарах.
    - Отображает товары на сайте.
    - Отправляет уведомления о покупке.
    Это нарушает SRP, потому что у класса несколько причин для изменения:
    - Изменение формата данных товаров.
    - Изменение способа отображения (например, с HTML на JSON).
    - Изменение логики отправки уведомлений (например, с email на SMS).
    Проблемы:
    - Код сложный и трудно читаемый.
    - Изменение одной функции (например, отображения) может сломать другую (например, уведомления).
    - Трудно тестировать: нужно проверять всё сразу.
    """

    def __init__(self):
        self.products = []

    def add_product(self, name: str, color: Color, price: float):
        self.products.append(Product(name, color, price))

    def display_products(self) -> str:
        # Отображение товаров в формате HTML
        result = "<ul>"
        for product in self.products:
            result += f"<li>{product.name} ({product.color.name}, ${product.price})</li>"
        result += "</ul>"
        return result

    def send_purchase_notification(self, product_name: str):
        # Отправка уведомления (например, по email)
        print(f"Email sent: You purchased {product_name}! Thank you for shopping!")

    def process_purchase(self, product_name: str):
        # Обрабатывает покупку: отображает товары и отправляет уведомление
        print("Processing purchase...")
        print(self.display_products())
        self.send_purchase_notification(product_name)


# --- Пример соблюдения SRP ---
class ProductRepository:
    """
    Ответственность: хранить и управлять списком товаров.
    Если нужно изменить формат хранения (например, добавить базу данных), меняется только этот класс.
    """

    def __init__(self):
        self.products = []

    def add_product(self, product: Product):
        self.products.append(product)

    def get_products(self) -> List[Product]:
        return self.products


class ProductDisplay:
    """
    Ответственность: отображать товары в нужном формате (например, HTML).
    Если нужно изменить формат (например, на JSON), меняется только этот класс.
    """

    def display(self, products: List[Product]) -> str:
        result = "<ul>"
        for product in products:
            result += f"<li>{product.name} ({product.color.name}, ${product.price})</li>"
        result += "</ul>"
        return result


class NotificationService:
    """
    Ответственность: отправлять уведомления о покупке.
    Если нужно изменить способ отправки (например, с email на SMS), меняется только этот класс.
    """

    def send_purchase_notification(self, product_name: str):
        print(f"Email sent: You purchased {product_name}! Thank you for shopping!")


class PurchaseProcessor:
    """
    Ответственность: координировать процесс покупки (использовать другие классы).
    Этот класс связывает другие, но сам не делает лишнего.
    """

    def __init__(self, repository: ProductRepository, display: ProductDisplay, notification: NotificationService):
        self.repository = repository # хранить и управлять списком товаров
        self.display = display # отображать товары в нужном формате
        self.notification = notification # отправлять уведомления о покупке

    def process_purchase(self, product_name: str):
        print("Processing purchase...")
        products = self.repository.get_products()
        print(self.display.display(products))
        self.notification.send_purchase_notification(product_name)


# --- Демонстрация использования ---
def main():
    """
    Показывает, как работают оба подхода:
    - ProductManagerBad: нарушает SRP, делая всё в одном классе.
    - ProductRepository, ProductDisplay, NotificationService, PurchaseProcessor: соблюдают SRP,
      разделяя ответственность.
    """
    # --- Нарушение SRP ---
    print("=== Плохой подход (ProductManagerBad) ===")
    bad_manager = ProductManagerBad()
    bad_manager.add_product("T-Shirt", Color.RED, 20.0)
    bad_manager.add_product("Table", Color.GREEN, 150.0)
    bad_manager.process_purchase("T-Shirt")

    # --- Соблюдение SRP ---
    print("\n=== Хороший подход (разделение ответственности) ===")
    repository = ProductRepository()
    repository.add_product(Product("T-Shirt", Color.RED, 20.0))
    repository.add_product(Product("Table", Color.GREEN, 150.0))

    display = ProductDisplay()
    notification = NotificationService()
    processor = PurchaseProcessor(repository, display, notification)
    processor.process_purchase("T-Shirt")


if __name__ == "__main__":
    main()

"""
Что такое SRP?
    Принцип единственной ответственности (Single Responsibility Principle) — гласит:
      Каждый класс должен иметь только одну причину для изменения, то есть выполнять только одну задачу.
      Это означает, что класс должен отвечать за что-то одно: например, хранить данные, отображать их или 
        отправлять уведомления.

    Пример из кода:
      В ProductManagerBad (нарушение SRP) класс делает три вещи: хранит товары, отображает их и отправляет уведомления.
      Если нужно изменить формат отображения (например, с HTML на JSON), придётся лезть в класс, рискуя сломать логику уведомлений.
      В хорошем подходе (ProductRepository, ProductDisplay, NotificationService) каждая задача разделена 
      (каждый класс отвечает за одну задачу, и изменения в одной области не трогают другие):
      - ProductRepository хранит товары.
      - ProductDisplay отображает товары.
      - NotificationService отправляет уведомления.
      Это делает код проще, надёжнее и легче для тестирования.

    Почему нужно использовать SRP?
      SRP помогает создавать понятные, поддерживаемые и масштабируемые системы. В реальной разработке классы часто 
        обрастают лишними обязанностями. Например, класс `Product` начинает не только хранить данные, но и 
        фильтровать товары или отправлять письма. Это приводит к:
        - Сложности в поддержке: изменение одной функции (например, отображения) может сломать другую (например, уведомления).
        - Трудностям в тестировании: нужно тестировать весь класс, даже если изменилась только одна часть.
        - Конфликтам в команде: несколько разработчиков могут одновременно менять один класс, создавая баги.

    SRP разделяет обязанности на отдельные классы и мы получаем такие преимущства:
      - Частые изменения требований (Гибкость): Если в интернет-магазине нужно часто менять формат отображения
          (например, HTML, JSON, XML) или способ отправки уведомлений (email, SMS, push), SRP позволяет
          менять только один класс, не трогая другие.
      - Большие проекты: В крупных системах классы с множеством обязанностей усложняют поддержку и увеличивают
          риск багов.
      - Командная разработка (Масштабируемость): Когда несколько разработчиков работают над кодом, SRP снижает
          вероятность конфликтов, так как каждый класс отвечает за одну задачу.
      - Тестирование: Код, следующий SRP, легче тестировать, так как каждая задача (например, отображение)
          изолирована в отдельном классе.

    Преимущества SRP
      1. Простота поддержки:
         - Каждый класс делает одну вещь, поэтому его легче понять и изменить.
         - Например, изменение формата отображения затрагивает только `ProductDisplay`.
      2. Легче тестировать:
         - `NotificationService` тестируется отдельно от `ProductRepository`, что упрощает написание тестов.
      3. Меньше багов:
         - Изменения в одном классе не ломают другие, потому что обязанности разделены.
      4. Гибкость:
         - Хочешь добавить новый способ отображения (например, JSON)? Создай новый класс `JsonProductDisplay`, 
        не трогая старый код.
      5. Командная работа:
         - Один разработчик работает над `ProductDisplay`, другой над `NotificationService`, без конфликтов.

    Недостатки SRP
      1. Больше кода:
         - Вместо одного класса (`ProductManagerBad`) ты пишешь несколько (`ProductRepository`, `ProductDisplay`, и т.д.).
         - Для маленького проекта это может быть избыточно.
      2. Сложность для новичков:
         - Много классов могут запутать, если ты привык писать всё в одном месте.
      3. Время на проектирование:
         - Нужно заранее продумать, как разделить обязанности, что требует опыта.

    Когда SRP не нужен:
      - Если проект маленький (например, скрипт для 10 товаров без сложной логики).
      - Если ты пишешь прототип, где важна скорость, а не поддержка.
      - Если требования стабильны и не будут меняться.

    Как понять, что SRP нарушен?
      - Класс делает несколько вещей: например, `ProductManagerBad` хранит данные, отображает товары и отправляет 
         уведомления.
      - Изменение одной функции требует править весь класс (например, изменение формата отображения ломает уведомления).
      - Класс становится большим и сложным, с методами, которые не связаны между собой.

    Пример из кода:
      `ProductManagerBad` нарушает SRP, потому что у него три причины для изменения:
        - Изменение формата хранения товаров.
        - Изменение способа отображения (HTML → JSON).
        - Изменение логики уведомлений (email → SMS).
      В хорошем подходе каждая причина для изменения соответствует отдельному классу.

    Как применять SRP?
    1. Определи ответственность:
       - Задай вопрос: "За что отвечает этот класс?" Если ответов несколько, разбей класс.
       - Например, `ProductRepository` — за хранение, `ProductDisplay` — за отображение.
    2. Разделяй задачи:
       - Создай отдельный класс для каждой функции: хранение, отображение, уведомления.
    3. Используй композицию:
       - `PurchaseProcessor` связывает классы (`ProductRepository`, `ProductDisplay`, `NotificationService`), но сам не делает лишнего.
    4. Держи классы маленькими:
       - Каждый класс должен быть простым и отвечать за одну задачу.

    Пример из кода:
      - `ProductRepository` хранит товары.
      - `ProductDisplay` отвечает за их отображение.
      - `NotificationService` отправляет уведомления.
      - `PurchaseProcessor` координирует работу, но не выполняет задачи сам.

    Пример из реальной разработки
      Ты пишешь интернет-магазин. У тебя есть:
        - Товары (хранятся в базе данных).
        - Страница с товарами (HTML или JSON для API).
        - Уведомления о покупке (email, SMS, push).
      Без SRP ты пишешь один класс, который делает всё. Если заказчик просит изменить отображение (например, 
        добавить фильтры), ты лазаешь в код, который также отправляет письма, и рискуешь всё сломать. С SRP ты меняешь 
        только `ProductDisplay`, не трогая `NotificationService`.

    Как это помогает в проекте?
      - Быстрее вносить изменения**: Хочешь отправлять SMS вместо email? Меняй только `NotificationService`.
      - Легче тестировать: Тестируй `ProductDisplay` отдельно от `ProductRepository`.
      - Меньше конфликтов: Разные разработчики работают над разными классами.
      - Гибкость: Хочешь добавить новый формат отображения? Пишешь новый класс, не трогая старый код.


"""