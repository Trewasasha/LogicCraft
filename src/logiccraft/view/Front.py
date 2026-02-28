import flet as ft
import random


def main(page: ft.Page):
    page.title = "UML Редактор с Drag-and-Drop"
    page.window_width = 800
    page.window_height = 600
    page.padding = 5
    page.bgcolor = "#fafafa"

    cards = []  # Список карточек
    selected_card = None  # Выделенная карточка
    drag_offset = {"x": 0, "y": 0}  # Смещение при перетаскивании

    def create_card(x, y, text):
        """Создание карточки"""
        # Контейнер с содержимым карточки
        card_content = ft.Container(
            width=160,
            height=100,
            bgcolor="#f5f5dc",
            border=ft.border.all(2, "#4169E1"),  # Используем border.all для старой версии
            border_radius=5,
            content=ft.Stack([
                # Заголовок
                ft.Container(
                    width=160,
                    height=30,
                    bgcolor="#4169E1",
                    border_radius=ft.border_radius.only(top_left=5, top_right=5),  # Для старой версии
                    content=ft.Text(
                        text,
                        color="white",
                        size=10,
                        weight=ft.FontWeight.BOLD,
                        left=10,
                        top=7
                    )
                ),
                # Контент
                ft.Container(
                    top=35,
                    left=10,
                    content=ft.Text(
                        "поле: тип\n+ метод(): тип",
                        size=9,
                        color="black"
                    )
                )
            ])
        )

        # Создаем карточку с обработчиками
        card = ft.GestureDetector(
            left=x,
            top=y,
            content=card_content,
            on_pan_start=lambda e: start_drag(e, card),
            on_pan_update=lambda e: drag_update(e, card),
            on_pan_end=lambda e: end_drag(e, card),
        )

        return card

    def start_drag(e, card):
        """Начало перетаскивания"""
        nonlocal selected_card, drag_offset
        selected_card = card
        # Меняем обводку
        card.content.border = ft.border.all(3, "#DC143C")
        # Запоминаем смещение
        drag_offset["x"] = e.local_x
        drag_offset["y"] = e.local_y
        # Поднимаем карточку
        stack.controls.remove(card)
        stack.controls.append(card)
        card.update()

    def drag_update(e, card):
        """Процесс перетаскивания"""
        if selected_card == card:
            # Новые координаты
            new_left = max(0, card.left + e.delta_x)
            new_top = max(0, card.top + e.delta_y)

            # Ограничиваем в пределах окна
            new_left = min(new_left, page.window_width - 180)
            new_top = min(new_top, page.window_height - 180)

            card.left = new_left
            card.top = new_top
            card.update()

    def end_drag(e, card):
        """Конец перетаскивания"""
        nonlocal selected_card
        selected_card = None
        card.content.border = ft.border.all(2, "#4169E1")
        card.update()

    def add_card(e):
        """Добавление новой карточки"""
        x = random.randint(30, 400)
        y = random.randint(30, 300)

        # Создаем карточку
        card = create_card(x, y, f"Класс{len(cards)}")

        stack.controls.append(card)
        cards.append(card)
        update_counter()
        page.update()

    def clear_all(e):
        """Очистка всех карточек"""
        stack.controls.clear()
        cards.clear()
        selected_card = None
        update_counter()
        page.update()

    def update_counter():
        """Обновление счетчика"""
        counter_label.value = f"Карточек: {len(cards)}"
        page.update()

    # Верхняя панель - используем ElevatedButton для старой версии
    toolbar = ft.Container(
        bgcolor="#eae6ca",
        height=50,
        padding=5,
        content=ft.Row([
            ft.ElevatedButton(
                text="➕ Добавить класс",
                on_click=add_card,
                bgcolor="#4169E1",
                color="white",
            ),
            ft.ElevatedButton(
                text="🗑️ Очистить",
                on_click=clear_all,
                bgcolor="#DC143C",
                color="white",
            ),
            ft.Container(width=20),
            ft.Text("Карточек: 0", size=14)
        ])
    )

    counter_label = toolbar.content.controls[3]

    # Стек для карточек (как Canvas)
    stack = ft.Stack(
        width=780,
        height=450,
        controls=[]
    )

    # Контейнер для стека (как Canvas с рамкой)
    canvas_container = ft.Container(
        content=stack,
        border=ft.border.all(2, "#3d1f18"),
        bgcolor="white",
        padding=5,
        margin=ft.margin.only(top=5, bottom=5),
        expand=True
    )

    # Нижняя панель
    status_bar = ft.Container(
        bgcolor="#eae6ca",
        height=30,
        content=ft.Row([
            ft.Text(
                "Просто перетащите карточку мышкой!",
                size=12
            )
        ], alignment=ft.MainAxisAlignment.CENTER)
    )

    # Собираем страницу
    page.add(
        toolbar,
        canvas_container,
        status_bar
    )


# ЗАПУСК
if __name__ == "__main__":
    ft.app(target=main)