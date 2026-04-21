# 💡 Примеры использования LogicCraft

Практические примеры создания UML диаграмм для различных сценариев.

## Содержание

1. [Простая система пользователей](#простая-система-пользователей)
2. [Интернет-магазин](#интернет-магазин)
3. [Система управления задачами](#система-управления-задачами)
4. [Паттерн Observer](#паттерн-observer)
5. [Библиотечная система](#библиотечная-система)

## Простая система пользователей

### Описание
Базовая система с пользователями и ролями.

### Классы
1. **User** (Пользователь)
   - Атрибуты: `+id: int`, `+name: str`, `+email: str`, `-password: str`
   - Методы: `+login(email: str, password: str): bool`, `+logout(): void`

2. **Admin** (Администратор)
   - Наследует от User
   - Методы: `+deleteUser(userId: int): bool`, `+createUser(userData: dict): User`

### Связи
- **Inheritance**: Admin → User (Admin наследует от User)

### Сгенерированный Python код
```python
class User:
    def __init__(self):
        self.id: int = 0
        self.name: str = ""
        self.email: str = ""
        self._password: str = ""
    
    def login(self, email: str, password: str) -> bool:
        # TODO: Implement login
        return False
    
    def logout(self) -> None:
        # TODO: Implement logout
        pass

class Admin(User):
    def __init__(self):
        super().__init__()
    
    def delete_user(self, user_id: int) -> bool:
        # TODO: Implement delete_user
        return False
    
    def create_user(self, user_data: dict) -> 'User':
        # TODO: Implement create_user
        return User()
```

## Интернет-магазин

### Описание
Система интернет-магазина с товарами, заказами и корзиной.

### Классы

1. **Product** (Товар)
   - Атрибуты: `+id: int`, `+name: str`, `+price: float`, `+stock: int`
   - Методы: `+updatePrice(newPrice: float): void`, `+isAvailable(): bool`

2. **ShoppingCart** (Корзина)
   - Атрибуты: `+items: List[CartItem]`, `+totalAmount: float`
   - Методы: `+addItem(product: Product, quantity: int): void`, `+removeItem(productId: int): void`, `+calculateTotal(): float`

3. **CartItem** (Элемент корзины)
   - Атрибуты: `+product: Product`, `+quantity: int`, `+subtotal: float`
   - Методы: `+updateQuantity(newQuantity: int): void`

4. **Order** (Заказ)
   - Атрибуты: `+id: int`, `+customer: User`, `+items: List[CartItem]`, `+status: str`, `+totalAmount: float`
   - Методы: `+processPayment(): bool`, `+updateStatus(newStatus: str): void`

### Связи
- **Composition**: ShoppingCart ♦→ CartItem (корзина содержит элементы)
- **Association**: CartItem →  Product (элемент ссылается на товар)
- **Association**: Order → User (заказ принадлежит пользователю)
- **Composition**: Order ♦→ CartItem (заказ содержит элементы)

### Пошаговое создание в LogicCraft

1. **Создайте классы:**
   - Добавьте 4 класса: Product, ShoppingCart, CartItem, Order
   - Расположите их логично на диаграмме

2. **Добавьте атрибуты и методы:**
   - Откройте каждый класс через правый клик → Edit
   - Добавьте атрибуты и методы согласно списку выше

3. **Создайте связи:**
   - ShoppingCart → CartItem (Composition)
   - CartItem → Product (Association)
   - Order → User (Association)
   - Order → CartItem (Composition)

## Система управления задачами

### Описание
Простая система управления задачами (Task Manager).

### Классы

1. **Task** (Задача)
   - Атрибуты: `+id: int`, `+title: str`, `+description: str`, `+status: TaskStatus`, `+priority: int`, `+dueDate: Date`
   - Методы: `+markCompleted(): void`, `+updatePriority(newPriority: int): void`

2. **TaskStatus** (Статус задачи)
   - Атрибуты: `+PENDING: str`, `+IN_PROGRESS: str`, `+COMPLETED: str`, `+CANCELLED: str`

3. **Project** (Проект)
   - Атрибуты: `+id: int`, `+name: str`, `+tasks: List[Task]`, `+owner: User`
   - Методы: `+addTask(task: Task): void`, `+removeTask(taskId: int): void`, `+getCompletedTasks(): List[Task]`

4. **TaskManager** (Менеджер задач)
   - Атрибуты: `+projects: List[Project]`, `+users: List[User]`
   - Методы: `+createProject(name: str, owner: User): Project`, `+assignTask(task: Task, user: User): void`

### Связи
- **Composition**: Project ♦→ Task (проект содержит задачи)
- **Association**: Task → TaskStatus (задача имеет статус)
- **Association**: Project → User (проект принадлежит пользователю)
- **Aggregation**: TaskManager ◇→ Project (менеджер управляет проектами)
- **Aggregation**: TaskManager ◇→ User (менеджер управляет пользователями)

## Паттерн Observer

### Описание
Реализация паттерна Observer для системы уведомлений.

### Классы

1. **Observable** (Наблюдаемый) - абстрактный класс
   - Атрибуты: `#observers: List[Observer]`
   - Методы: `+addObserver(observer: Observer): void`, `+removeObserver(observer: Observer): void`, `#notifyObservers(): void`

2. **Observer** (Наблюдатель) - интерфейс
   - Методы: `+update(data: Any): void`

3. **NewsPublisher** (Издатель новостей)
   - Наследует от Observable
   - Атрибуты: `+latestNews: str`
   - Методы: `+publishNews(news: str): void`

4. **EmailSubscriber** (Email подписчик)
   - Реализует Observer
   - Атрибуты: `+email: str`
   - Методы: `+update(news: str): void`, `+sendEmail(message: str): void`

5. **SMSSubscriber** (SMS подписчик)
   - Реализует Observer
   - Атрибуты: `+phoneNumber: str`
   - Методы: `+update(news: str): void`, `+sendSMS(message: str): void`

### Связи
- **Inheritance**: NewsPublisher → Observable
- **Realization**: EmailSubscriber → Observer (реализация интерфейса)
- **Realization**: SMSSubscriber → Observer (реализация интерфейса)
- **Association**: Observable → Observer (один ко многим)

## Библиотечная система

### Описание
Система управления библиотекой с книгами, читателями и выдачей книг.

### Классы

1. **Book** (Книга)
   - Атрибуты: `+isbn: str`, `+title: str`, `+author: str`, `+isAvailable: bool`, `+publishYear: int`
   - Методы: `+checkOut(): bool`, `+checkIn(): void`, `+getInfo(): str`

2. **Reader** (Читатель)
   - Атрибуты: `+id: int`, `+name: str`, `+email: str`, `+borrowedBooks: List[Book]`, `+maxBooks: int`
   - Методы: `+borrowBook(book: Book): bool`, `+returnBook(book: Book): void`, `+canBorrowMore(): bool`

3. **Librarian** (Библиотекарь)
   - Атрибуты: `+id: int`, `+name: str`, `+employeeId: str`
   - Методы: `+issueBook(book: Book, reader: Reader): bool`, `+receiveBook(book: Book, reader: Reader): void`, `+addNewBook(book: Book): void`

4. **Library** (Библиотека)
   - Атрибуты: `+name: str`, `+books: List[Book]`, `+readers: List[Reader]`, `+librarians: List[Librarian]`
   - Методы: `+findBook(isbn: str): Book`, `+registerReader(reader: Reader): void`, `+generateReport(): str`

5. **BorrowRecord** (Запись о выдаче)
   - Атрибуты: `+id: int`, `+book: Book`, `+reader: Reader`, `+borrowDate: Date`, `+returnDate: Date`, `+isReturned: bool`
   - Методы: `+markReturned(): void`, `+calculateFine(): float`

### Связи
- **Aggregation**: Library ◇→ Book (библиотека содержит книги)
- **Aggregation**: Library ◇→ Reader (библиотека обслуживает читателей)
- **Aggregation**: Library ◇→ Librarian (в библиотеке работают библиотекари)
- **Association**: Reader → Book (читатель берет книги)
- **Association**: BorrowRecord → Book (запись связана с книгой)
- **Association**: BorrowRecord → Reader (запись связана с читателем)
- **Dependency**: Librarian → BorrowRecord (библиотекарь создает записи)

### Особенности реализации

1. **Множественные связи**: Reader может иметь несколько Book
2. **Временные связи**: BorrowRecord отслеживает историю
3. **Бизнес-правила**: Reader имеет ограничение на количество книг

## Советы по созданию диаграмм

### 1. Планирование
- Начните с основных сущностей
- Определите их атрибуты и методы
- Подумайте о связях между ними

### 2. Именование
- Используйте понятные имена классов (PascalCase)
- Атрибуты и методы в camelCase
- Добавляйте префиксы видимости (+, -, #)

### 3. Организация на диаграмме
- Размещайте связанные классы рядом
- Базовые классы — сверху, производные — снизу
- Избегайте пересечения линий связей

### 4. Типы связей
- **Association** (→) — простая связь "использует"
- **Inheritance** (→◁) — наследование "является"
- **Composition** (→♦) — сильная связь "часть от"
- **Aggregation** (→◇) — слабая связь "имеет"

### 5. Генерация кода
- Проверьте диаграмму перед генерацией
- Выберите подходящий язык программирования
- Дополните сгенерированный код бизнес-логикой

---

Эти примеры помогут вам освоить LogicCraft и создавать качественные UML диаграммы! 💡✨