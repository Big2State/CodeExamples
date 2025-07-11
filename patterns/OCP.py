# Демонстрация принципа открытости/закрытости (OCP) на примере фильтрации продуктов.

from abc import ABC, abstractmethod
from enum import Enum

'''
OCP - Принцип открытости/закрытости
OCP -> open for extension, closed for modification | (Open/Closed Principle)
      (открытость для расширения, закрытость для модификации)
OCP гласит, что программные сущности (классы, модули, функции) должны быть 
 - Открыты для расширения: можно добавлять новую функциональность (например, новые фильтры).
 - Закрыты для модификации: существующий код не нужно изменять при добавлении новых возможностей.
'''

# --- Перечисления для атрибутов продукта ---
# Используем Enum для строгого определения возможных значений цвета и размера.
# Это делает код безопасным и читаемым, но сами по себе Enum не связаны с OCP.
class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

class Size(Enum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3

class Material(Enum):
    WOOD = 1
    METAL = 2
    PLASTIC = 3

# --- Класс продукта ---
# Класс Product хранит информацию о продукте
class Product:
    """
        Простой класс, представляющий продукт с атрибутами: имя, цвет, размер и материал.
        Этот класс не зависит от логики фильтрации, что соответствует принципу разделения
        ответственности (SRP) и помогает в контексте OCP.
    """
    def __init__(self, name: str, color: Color, size: Size, material: Material):
        self.name = name
        self.color = color
        self.size = size
        self.material = material

# --- Пример нарушения OCP ---
# Этот класс показывает, как НЕ следует проектировать систему, если вы хотите следовать OCP.
class ProductFilter_2:
    """
        Проблема:
            Этот класс нарушает OCP, так как для каждого нового критерия фильтрации
            (например, по материалу filter_by_material) нужно добавлять новый метод или изменять существующие.
            Это приводит к:
            - Увеличению риска ошибок при модификации.
            - Сложности поддержки кода, если критериев становится много.
            - Нарушению принципа "закрытости для модификации".
    """
    def filter_by_color(self, products: list[Product], color: Color) -> list[Product]:
        return [p for p in products if p.color == color]

    def filter_by_size(self, products: list[Product], size: Size) -> list[Product]:
        return [p for p in products if p.size == size]

    def filter_by_color_and_size(self, products: list[Product], color: Color, size: Size) -> list[Product]:
        return [p for p in products if p.color == color and p.size == size]

    # Если добавить фильтр по материалу, нужно модифицировать класс:
    def filter_by_material(self, products: list[Product], material: Material) -> list[Product]:
        return [p for p in products if p.material == material]



# --- Пример соблюдения OCP ---
# Интерфейс спецификации (абстрактный класс) для фильтрации
class Specification(ABC):
    """
        Абстрактный класс Specification определяет интерфейс для проверки, удовлетворяет ли
        продукт заданному критерию. Это ключевая часть соблюдения OCP, так как позволяет
        создавать новые критерии фильтрации (спецификации) без изменения других классов.
    """
    @abstractmethod
    def is_satisfied(self, item: Product) -> bool:
        pass

# Конкретные спецификации для фильтрации
class ColorSpecification(Specification):
    """
        Спецификация для фильтрации по цвету.
        Реализует метод is_satisfied, проверяющий, соответствует ли цвет продукта заданному.
    """
    def __init__(self, color: Color):
        self.color = color

    def is_satisfied(self, item: Product) -> bool:
        return item.color == self.color

class SizeSpecification(Specification):
    """
        Спецификация для фильтрации по размеру.
        Каждая спецификация изолирована и отвечает только за один критерий.
    """
    def __init__(self, size: Size):
        self.size = size

    def is_satisfied(self, item: Product) -> bool:
        return item.size == self.size

class MaterialSpecification(Specification):
    """
        Новая спецификация для фильтрации по материалу.
        Демонстрирует, как легко расширить систему, добавив новый критерий без изменения
        других классов (например, ProductFilter).
    """
    def __init__(self, material: Material):
        self.material = material

    def is_satisfied(self, item: Product) -> bool:
        return item.material == self.material


# Комбинированная спецификация для сложных фильтров (логическое И)
class AndSpecification(Specification):
    """
        Комбинирует две спецификации, проверяя, что продукт удовлетворяет обеим.
        Это позволяет создавать сложные фильтры (например, цвет И размер) без изменения
        основного кода фильтрации.
    """
    def __init__(self, spec1, spec2):
        self.spec1 = spec1
        self.spec2 = spec2

    def is_satisfied(self, item): #FIXME проверить по видео
        return self.spec1.is_satisfied(item) and self.spec2.is_satisfied(item)

    def __and__(self, other): #FIXME проверить по видео
        return AndSpecification(self, other)

# Класс фильтра, следующий OCP
class ProductFilter:
    """
        Этот класс отвечает за фильтрацию продуктов по заданной спецификации.
        Он закрыт для модификации: для добавления нового критерия (например, по материалу)
        не нужно менять этот класс. Достаточно создать новую спецификацию.
        Открыт для расширения: новые спецификации (как MaterialSpecification) легко
        интегрируются через интерфейс Specification.
    """
    def filter(self, products: list[Product], specification: Specification) -> list[Product]:
        return [p for p in products if specification.is_satisfied(p)]

# --- Демонстрация использования ---
def main():
    """
        Демонстрирует работу обоих подходов:
        - ProductFilter_2 (нарушение OCP): показывает, как добавление нового фильтра требует
          изменения кода.
        - ProductFilter (соблюдение OCP): показывает, как новые фильтры добавляются без
          модификации существующих классов.
    """
    # Создаём тестовые продукты
    products = [
        Product("Apple", Color.RED, Size.SMALL, Material.PLASTIC),
        Product("Tree", Color.GREEN, Size.LARGE, Material.WOOD),
        Product("House", Color.BLUE, Size.LARGE, Material.METAL),
        Product("Chair", Color.RED, Size.MEDIUM, Material.WOOD),
    ]

    # --- Нарушение OCP ---
    print("=== Нарушение OCP (ProductFilter_2) ===")
    bad_filter = ProductFilter_2()
    print("Products with RED color:")
    for p in bad_filter.filter_by_color(products, Color.RED):
        print(f"- {p.name}")
    print("\nProducts with LARGE size:")
    for p in bad_filter.filter_by_size(products, Size.LARGE):
        print(f"- {p.name}")
    print("\nProducts with WOOD material (требует новый метод):")
    for p in bad_filter.filter_by_material(products, Material.WOOD):
        print(f"- {p.name}")

    # --- Соблюдение OCP ---
    print("\n=== Соблюдение OCP (ProductFilter) ===")
    good_filter = ProductFilter()
    # Фильтр по цвету
    red_spec = ColorSpecification(Color.RED)
    print("Products with RED color:")
    for p in good_filter.filter(products, red_spec):
        print(f"- {p.name}")
    # Фильтр по размеру
    large_spec = SizeSpecification(Size.LARGE)
    print("\nProducts with LARGE size:")
    for p in good_filter.filter(products, large_spec):
        print(f"- {p.name}")
    # Фильтр по материалу (новый критерий, добавлен без изменения ProductFilter)
    wood_spec = MaterialSpecification(Material.WOOD)
    print("\nProducts with WOOD material:")
    for p in good_filter.filter(products, wood_spec):
        print(f"- {p.name}")
    # Комбинированный фильтр (красный цвет И большой размер)
    red_and_large_spec = AndSpecification(red_spec, large_spec)
    print("\nProducts with RED color and LARGE size:")
    for p in good_filter.filter(products, red_and_large_spec):
        print(f"- {p.name}")

if __name__ == "__main__":
    main()