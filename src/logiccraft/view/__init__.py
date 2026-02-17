import tkinter as tk
import random

class UMLCard:
    """Класс карточки UML"""
    def __init__(self, canvas, x, y, text):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = 160
        self.height = 100
        self.text = text
        self.selected = False

        # Создаем карточку (прямоугольник + текст)
        self.rect = canvas.create_rectangle(
            x, y, x + self.width, y + self.height,
            fill="#f5f5dc", outline="#4169E1", width=2
        )

        # Заголовок карточки
        self.title_bg = canvas.create_rectangle(
            x, y, x + self.width, y + 30,
            fill="#4169E1", outline="#4169E1"
        )

        self.title = canvas.create_text(
            x + 10, y + 15,
            text=text,
            fill="white",
            font=("Arial", 10, "bold"),
            anchor="w"
        )

        # Текст полей и методов
        self.content = canvas.create_text(
            x + 10, y + 45,
            text="поле: тип\n+ метод(): тип",
            fill="black",
            font=("Arial", 9),
            anchor="nw"
        )

        # Привязываем события мыши
        for item in [self.rect, self.title_bg, self.title, self.content]:
            canvas.tag_bind(item, "<Button-1>", self.on_click)
            canvas.tag_bind(item, "<B1-Motion>", self.on_drag)
            canvas.tag_bind(item, "<ButtonRelease-1>", self.on_release)

    def on_click(self, event):
        """Начало перетаскивания"""
        self.selected = True
        # Меняем обводку на красную
        self.canvas.itemconfig(self.rect, outline="#DC143C", width=3)
        # Запоминаем смещение мыши относительно карточки
        self.drag_offset_x = event.x - self.x
        self.drag_offset_y = event.y - self.y
        # Поднимаем карточку над другими
        self.canvas.tag_raise(self.rect)
        self.canvas.tag_raise(self.title_bg)
        self.canvas.tag_raise(self.title)
        self.canvas.tag_raise(self.content)

    def on_drag(self, event):
        """Процесс перетаскивания"""
        if self.selected:
            # Новые координаты с учетом смещения
            new_x = event.x - self.drag_offset_x
            new_y = event.y - self.drag_offset_y

            # Ограничиваем перемещение в пределах канвы
            new_x = max(0, min(new_x, self.canvas.winfo_width() - self.width))
            new_y = max(0, min(new_y, self.canvas.winfo_height() - self.height))

            # Вычисляем смещение
            dx = new_x - self.x
            dy = new_y - self.y

            # Перемещаем все элементы карточки
            self.canvas.move(self.rect, dx, dy)
            self.canvas.move(self.title_bg, dx, dy)
            self.canvas.move(self.title, dx, dy)
            self.canvas.move(self.content, dx, dy)

            # Обновляем координаты
            self.x = new_x
            self.y = new_y

    def on_release(self, event):
        """Конец перетаскивания"""
        self.selected = False
        # Возвращаем обычную обводку
        self.canvas.itemconfig(self.rect, outline="#4169E1", width=2)


class UMLApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UML Редактор с Drag-and-Drop")
        self.root.geometry("800x600")

        # Список карточек
        self.cards = []

        # Создаем интерфейс
        self.create_widgets()

    def create_widgets(self):
        # Верхняя панель с кнопками
        toolbar = tk.Frame(self.root, bg="#eae6ca", height=50)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        # Кнопка добавления карточки
        add_btn = tk.Button(
            toolbar,
            text="➕ Добавить класс",
            command=self.add_card,
            bg="#4169E1",
            fg="white",
            font=("Arial", 10),
            padx=10
        )
        add_btn.pack(side=tk.LEFT, padx=5)

        # Кнопка очистки
        clear_btn = tk.Button(
            toolbar,
            text="🗑️ Очистить",
            command=self.clear_all,
            bg="#DC143C",
            fg="white",
            font=("Arial", 10),
            padx=10
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        # Счетчик карточек
        self.counter_label = tk.Label(
            toolbar,
            text="Карточек: 0",
            bg="#eae6ca",
            font=("Arial", 10)
        )
        self.counter_label.pack(side=tk.LEFT, padx=20)

        # Канва для рисования
        self.canvas = tk.Canvas(
            self.root,
            bg="#fafafa",
            highlightbackground="#3d1f18",
            highlightthickness=2
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Привязываем событие изменения размера окна
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        # Нижняя панель с подсказкой
        status_bar = tk.Frame(self.root, bg="#eae6ca", height=30)
        status_bar.pack(fill=tk.X, padx=5, pady=5)

        hint = tk.Label(
            status_bar,
            text="Просто перетащите карточку мышкой!",
            bg="#eae6ca",
            font=("Arial", 10)
        )
        hint.pack(pady=5)

    def add_card(self):
        """Добавление новой карточки"""
        # Генерируем случайные координаты
        x = random.randint(30, 400)
        y = random.randint(30, 300)

        # Создаем карточку
        card = UMLCard(self.canvas, x, y, f"Класс{len(self.cards)}")
        self.cards.append(card)

        # Обновляем счетчик
        self.update_counter()

    def clear_all(self):
        """Очистка всех карточек"""
        for card in self.cards:
            self.canvas.delete(card.rect)
            self.canvas.delete(card.title_bg)
            self.canvas.delete(card.title)
            self.canvas.delete(card.content)

        self.cards.clear()
        self.update_counter()

    def update_counter(self):
        """Обновление счетчика карточек"""
        self.counter_label.config(text=f"Карточек: {len(self.cards)}")

    def on_canvas_resize(self, event):
        """Обработка изменения размера канвы"""
        pass


# Запуск приложения (ТОЛЬКО ОДИН РАЗ)
if __name__ == "__init__":
    root = tk.Tk()
    app = UMLApp(root)
    root.mainloop()