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
Более детальное описание в конце кода
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
                (Красный цвет И большой размер) ИЛИ (Синий цвет И малый размер)
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

    # Бинарный оператор И (&) (амперсанд)  "красные И большие"
    def __and__(self, other):
        return AndSpecification(self, other)

    # Бинарный оператор ИЛИ (|)  "красные ИЛИ большие"
    def __or__(self, other):
        return OrSpecification(self, other)

    # Унарный оператор НЕ (~)  "НЕ большие"
    def __invert__(self):
        return NotSpecification(self)

# Каждая наследуемая спецификация от Specification изолирована и отвечает только за один критерий.

# Фильтрация по цвету
class ColorSpecification(Specification):
    """
        Спецификация для фильтрации по цвету.
        Реализует метод is_satisfied, проверяющий, соответствует ли цвет продукта заданному в self.color.
    """

    def __init__(self, color: Color):
        self.color = color

    def is_satisfied(self, item: Product) -> bool:
        return item.color == self.color

# Фильтрация по размеру
class SizeSpecification(Specification):
    """
        Спецификация для фильтрации по размеру.
        Реализует метод is_satisfied, проверяющий, соответствует ли размер продукта заданному в self.size.
    """

    def __init__(self, size: Size):
        self.size = size

    def is_satisfied(self, item: Product) -> bool:
        return item.size == self.size

# Фильтрация по материалу
class MaterialSpecification(Specification):
    """
        Новая спецификация для фильтрации по материалу.
        Демонстрирует, как легко расширить систему, добавив новый критерий без изменения
        других классов (например, ProductFilter).
        Реализует метод is_satisfied, проверяющий, соответствует ли материал продукта заданному в self.material.
    """

    def __init__(self, material: Material):
        self.material = material

    def is_satisfied(self, item: Product) -> bool:
        return item.material == self.material


# Комбинированная спецификация для сложных фильтров (логическое И, ИЛИ, НЕ)
class AndSpecification(Specification):
    """
        Комбинатор - это паттерн, который позволяет объединить две или более спецификации.
          Или по другому говоря - это некая структура, которая объеденяет другие структуры.
        Комбинирует две спецификации, проверяя, что продукт удовлетворяет обеим спецификациям.
        Это позволяет создавать сложные фильтры (например, цвет И размер) без изменения
        основного кода фильтрации.
    """

    def __init__(self, *args):
        self.args = args
        # [SizeSpecification(Size.LARGE), ColorSpecification(Color.BLUE)]

    def is_satisfied(self, item: Product) -> bool:
        # item = Product("Apple", Color.RED, Size.SMALL, Material.PLASTIC)
        # self.args = [SizeSpecification(Size.LARGE), ColorSpecification(Color.BLUE)]
        results = []
        for spec in self.args:
            results.append(spec.is_satisfied(item))
        return all(results)
        # return all([spec.is_satisfied(item) for spec in self.args])
        # return all(map(lambda spec: spec.is_satisfied(item), self.args))

class OrSpecification(Specification):
    """Комбинирует две спецификации, проверяя, что продукт удовлетворяет хотя бы одной из них."""
    def __init__(self, *args):
        self.args = args

    def is_satisfied(self, item: Product) -> bool:
        return any(spec.is_satisfied(item) for spec in self.args)

class NotSpecification(Specification):
    """Инвертирует результат спецификации."""
    def __init__(self, spec):
        self.spec = spec

    def is_satisfied(self, item: Product) -> bool:
        return not self.spec.is_satisfied(item)

# Класс фильтра, следующий OCP
class ProductFilter:
    """
        Этот класс отвечает за фильтрацию продуктов по заданной спецификации.
        - Он закрыт для модификации: для добавления нового критерия (например, по материалу)
            не нужно менять этот класс. Достаточно создать новую спецификацию.
        - Открыт для расширения: новые спецификации (как MaterialSpecification) легко
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

    print("\nProducts with LARGE size and BLUE color:")
    large_blue = AndSpecification(large_spec, ColorSpecification(Color.BLUE))
    # К сожалению в питоне нельзя перегрузить оператор and, зато можно перегрузить бинарный and -> & (амперсанд)
    # large_blue = large_blue and ColorSpecification(Color.BLUE) # Красный цвет И большой размер
    # Реализация бинарных операторов:
    # large_blue = large_blue & ColorSpecification(Color.BLUE) # Красный цвет И большой размер
    # red_or_blue = ColorSpecification(Color.RED) | ColorSpecification(Color.BLUE) # Красный ИЛИ Синий
    # not_red = ~ColorSpecification(Color.RED) # Не красный
    # complex_condition = (
    #         (ColorSpecification(Color.RED) & SizeSpecification(Size.LARGE)) |
    #         (ColorSpecification(Color.BLUE) & SizeSpecification(Size.SMALL))
    # ) # (Красный цвет И большой размер) ИЛИ (Синий цвет И малый размер)
    for p in good_filter.filter(products, large_blue):
        print(f"- {p.name}")



if __name__ == "__main__":
    main()


"""
Принцип открытости/закрытости (Open/Closed Principle) — это один из пяти принципов SOLID, который гласит: 
  программные сущности должны быть открыты для расширения, но закрыты для модификации. Это означает, что вы можете 
  добавлять новую функциональность (например, новый критерий фильтрации, такой как Material) без изменения 
  существующего кода.
  - Открыт для расширения: В коде выше мы добавили фильтр по материалу (MaterialSpecification), не трогая класс 
     ProductFilter.
  - Закрыт для модификации: Класс ProductFilter остаётся неизменным, даже когда мы добавляем новые критерии фильтрации.
  
Пример из кода:
  - В ProductFilter_2 (нарушение OCP) для фильтрации по материалу пришлось добавить новый метод filter_by_material. Это 
     требует изменения кода.
  - В ProductFilter (соблюдение OCP) мы просто создали новый класс MaterialSpecification, и ProductFilter продолжил 
     работать без изменений.

Почему нужно использовать OCP?
  OCP помогает создавать гибкие, поддерживаемые и масштабируемые системы. Без OCP код становится хрупким: 
    каждое изменение (например, новый критерий фильтрации) требует правок в существующих классах, 
    что увеличивает риск ошибок и усложняет поддержку.
  
  Когда OCP особенно важен:
  - Частые изменения требований (Гибкость): Если в интернет-магазине регулярно добавляются новые критерии фильтрации 
     (например, по бренду, цене, категории), OCP позволяет добавлять их без переписывания кода.
  - Большие проекты: В крупных системах изменения в одном классе могут повлиять на другие части. OCP минимизирует 
     такие риски.
  - Командная разработка (Масштабируемость): Когда несколько разработчиков работают над кодом, OCP снижает 
     вероятность конфликтов, так как новый функционал добавляется через новые классы.
  - Тестирование: Код, следующий OCP, легче тестировать, так как новые спецификации 
     (например, MaterialSpecification) можно тестировать независимо.
     
  Пример из реальной жизни:
    В интернет-магазине пользователи могут фильтровать товары по цвету, размеру, материалу, бренду и т.д. Если каждый 
      новый фильтр требует изменения основного класса фильтрации (ProductFilter_2), это замедлит разработку и увеличит 
      вероятность багов. OCP позволяет добавлять новые фильтры как отдельные классы.
     
  Преимущества OCP
  - Гибкость: Новые критерии фильтрации добавляются через новые классы спецификаций, не трогая существующий код.
  - Снижение риска ошибок: Модификация старого кода может сломать уже работающую функциональность. OCP устраняет эту 
     проблему.
  - Переиспользуемость: Интерфейс Specification позволяет использовать спецификации в разных контекстах (например, 
     для фильтрации или валидации).
  - Лёгкость тестирования: Каждая спецификация (например, ColorSpecification) изолирована и тестируется отдельно.
  - Читаемость и модульность: Код разделён на небольшие, понятные классы, каждый из которых отвечает за одну задачу.

  Пример из кода:
    Класс ProductFilter работает с любым объектом, реализующим интерфейс Specification. Это делает его универсальным: 
      мы добавили MaterialSpecification, и ProductFilter продолжил работать без изменений.

  Недостатки и ограничения OCP
  - Усложнение кода: Для небольших проектов создание интерфейсов и множества классов может быть избыточным. 
      Например, если у вас всегда будет только фильтр по цвету и размеру, ProductFilter_2 с if-else проще и быстрее.
      ( Если ваш магазин продаёт только три продукта, и фильтры никогда не меняются, ProductFilter_2 может быть 
      достаточным, так как он проще для понимания и реализации.)
  - Дополнительные абстракции: OCP требует использования абстрактных классов или интерфейсов, что увеличивает 
      количество кода и может затруднить понимание.
  - Первоначальные затраты: Проектирование системы с учётом OCP требует больше времени на этапе планирования, 
      так как нужно продумать абстракции (например, интерфейс Specification).

  Как понять, что OCP нарушен?
  - Частое использование if-elif или switch-case для обработки разных типов данных или поведения (как в 
     ProductFilter_2).
  - Необходимость добавлять новые методы или изменять существующие при добавлении новой функциональности (например, 
     filter_by_material в ProductFilter_2).
  - Код становится "хрупким": изменение в одном месте (например, добавление нового условия) ломает другие части системы.
    
  Пример из кода:
    В ProductFilter_2 добавление фильтра по материалу потребовало нового метода filter_by_material. Если позже 
      добавить фильтр по бренду, придётся снова менять класс, что увеличивает риск ошибок.    
      
  Как применять OCP?
  - Создавать абстракции: Используйте интерфейсы или абстрактные классы (как Specification) для определения поведения.
  - Использовать полиморфизм: Делегируйте конкретную реализацию подклассам (как ColorSpecification, SizeSpecification).
  - Избегать жёсткой привязки: Не кодируйте конкретные критерии в логике (например, вместо проверки 
     product.color == Color.RED используйте спецификацию). Здесь мы "зашили" конкретные условия проверки прямо в 
     метод ProductFilter_2.filter_by_color_and_size. Если завтра понадобится изменить условие, придётся лезть в этот метод.
     if product.color == Color.RED and product.size == Size.LARGE:
        filtered_products.append(product)
    Гибкая привязка через спецификации:
      red_spec = ColorSpecification(Color.RED)
      large_spec = SizeSpecification(Size.LARGE)
      red_large_spec = AndSpecification(red_spec, large_spec)
      И потом передаём в ProductFilter для фильтрации:
      filtered_products = product_filter.filter(products, red_large_spec)
  - Применять паттерны проектирования: OCP часто реализуется через паттерны, такие как Specification (как в нашем примере), 
     Strategy, State или Factory.
     
  Пример из кода:
    Класс ProductFilter принимает объект Specification, что позволяет ему работать с любым критерием фильтрации. 
      Добавление MaterialSpecification не потребовало изменений в ProductFilter.
     
     
"""
