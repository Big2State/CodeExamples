#FIXME !!!НАПИСАЛ GROK, НЕ ПРОВЕРЯЛ!!!

# discount_ocp.py
# Демонстрация принципа открытости/закрытости (OCP) на примере расчёта скидок для клиентов.
# Этот код показывает, как нарушение OCP приводит к проблемам и как его соблюдение улучшает дизайн.

from abc import ABC, abstractmethod
from enum import Enum
from typing import List

# Перечисление для типов клиентов (используется для демонстрации данных)
class CustomerType(Enum):
    REGULAR = "Regular"  # Обычный клиент
    PREMIUM = "Premium"  # Премиум-клиент
    CORPORATE = "Corporate"  # Корпоративный клиент

# Класс клиента
class Customer:
    def __init__(self, name: str, customer_type: CustomerType):
        self.name = name
        self.customer_type = customer_type
        self.purchase_amount = 0.0  # Сумма покупки

    def set_purchase_amount(self, amount: float):
        self.purchase_amount = amount

# --- Пример нарушения OCP ---
# Этот класс демонстрирует, как НЕ следует проектировать систему, если вы хотите следовать OCP.
class DiscountCalculatorBad:
    """
    Проблема:
        Метод calculate_discount использует условные конструкции (if-elif) для определения скидки
        в зависимости от типа клиента. Если нужно добавить новый тип клиента (например, VIP),
        придётся модифицировать этот метод, добавляя новое условие.
        Это нарушает OCP, так как класс не закрыт для модификации.
    """
    def calculate_discount(self, customer: Customer) -> float:
        if customer.customer_type == CustomerType.REGULAR:
            return customer.purchase_amount * 0.05  # 5% скидка для обычных клиентов
        elif customer.customer_type == CustomerType.PREMIUM:
            return customer.purchase_amount * 0.15  # 15% скидка для премиум-клиентов
        elif customer.customer_type == CustomerType.CORPORATE:
            return customer.purchase_amount * 0.20  # 20% скидка для корпоративных клиентов
        else:
            return 0.0  # Нет скидки для неизвестных типов

# --- Пример соблюдения OCP ---
# Интерфейс (абстрактный класс) для стратегии расчёта скидки
class DiscountStrategy(ABC):
    """
    Интерфейс определяет метод для расчёта скидки.
    Каждый конкретный тип скидки будет реализовывать этот метод.
    Это позволяет добавлять новые стратегии без изменения существующего кода.
    """
    @abstractmethod
    def calculate_discount(self, purchase_amount: float) -> float:
        pass

# Конкретные стратегии скидок
class RegularDiscount(DiscountStrategy):
    """Скидка для обычных клиентов: 5% от суммы покупки."""
    def calculate_discount(self, purchase_amount: float) -> float:
        return purchase_amount * 0.05

class PremiumDiscount(DiscountStrategy):
    """Скидка для премиум-клиентов: 15% от суммы покупки."""
    def calculate_discount(self, purchase_amount: float) -> float:
        return purchase_amount * 0.15

class CorporateDiscount(DiscountStrategy):
    """Скидка для корпоративных клиентов: 20% от суммы покупки."""
    def calculate_discount(self, purchase_amount: float) -> float:
        return purchase_amount * 0.20

# Класс клиента с поддержкой OCP
class CustomerWithDiscount:
    """
    Класс клиента, который использует стратегию скидки.
    Вместо жёстко закодированных условий скидка определяется через объект DiscountStrategy.
    """
    def __init__(self, name: str, discount_strategy: DiscountStrategy):
        self.name = name
        self.discount_strategy = discount_strategy
        self.purchase_amount = 0.0

    def set_purchase_amount(self, amount: float):
        self.purchase_amount = amount

    def get_discount(self) -> float:
        """Делегирует расчёт скидки стратегии."""
        return self.discount_strategy.calculate_discount(self.purchase_amount)

# Класс для обработки скидок (аналог фильтра в предыдущем примере)
class DiscountProcessor:
    """
    Этот класс отвечает за применение скидок к списку клиентов.
    Он работает с любой стратегией скидки, что делает его закрытым для модификации.
    """
    def process_discounts(self, customers: List[CustomerWithDiscount]) -> None:
        for customer in customers:
            discount = customer.get_discount()
            print(f"{customer.name} gets a discount of ${discount:.2f}")

# --- Демонстрация использования ---
def main():
    """
    Пример использования обоих подходов: с нарушением OCP и с соблюдением OCP.
    Сравнение показывает, как OCP упрощает расширение системы.
    """
    print("=== Нарушение OCP ===")
    # Используем плохой подход
    customers = [
        Customer("Alice", CustomerType.REGULAR),
        Customer("Bob", CustomerType.PREMIUM),
        Customer("Charlie", CustomerType.CORPORATE),
    ]
    calculator = DiscountCalculatorBad()
    for customer in customers:
        customer.set_purchase_amount(100.0)  # Устанавливаем сумму покупки
        discount = calculator.calculate_discount(customer)
        print(f"{customer.name} gets a discount of ${discount:.2f}")

    print("\n=== Соблюдение OCP ===")
    # Используем правильный подход
    customers_with_discount = [
        CustomerWithDiscount("Alice", RegularDiscount()),
        CustomerWithDiscount("Bob", PremiumDiscount()),
        CustomerWithDiscount("Charlie", CorporateDiscount()),
    ]
    processor = DiscountProcessor()
    for customer in customers_with_discount:
        customer.set_purchase_amount(100.0)  # Устанавливаем сумму покупки
    processor.process_discounts(customers_with_discount)

    print("\n=== Добавление нового типа скидки (расширение) ===")
    # Добавляем новую скидку без изменения существующего кода
    class VipDiscount(DiscountStrategy):
        """Скидка для VIP-клиентов: 25% от суммы покупки."""
        def calculate_discount(self, purchase_amount: float) -> float:
            return purchase_amount * 0.25

    vip_customer = CustomerWithDiscount("David", VipDiscount())
    vip_customer.set_purchase_amount(100.0)
    processor.process_discounts([vip_customer])

if __name__ == "__main__":
    main()