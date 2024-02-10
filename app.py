import flet as ft
from PIL import Image
from ultralytics import YOLO
import os


# Словарь с метками классов
classes_dict = {
    0: '0',
    1: '1',
    2: '2',
    3: '3',
    4: '4',
    5: '5',
    6: '6',
    7: '7',
    8: '8',
    9: '9',
    10: 'A',
    11: 'B',
    12: 'D',
    13: 'E',
    14: 'G',
    15: 'H',
    16: 'J',
    17: 'K',
    18: 'L',
    19: 'N',
    20: 'R',
    21: 'S',
    22: 'T',
    23: 'U',
    24: 'V',
    25: 'X',
    26: 'Z'
}

# Загрузка модели
try:
    model = YOLO(os.path.join(os.getcwd(), 'weights', 'best.pt'))
except:
    raise NameError("Не могу загрузить модель, возможно ошибка в пути к файлу...")

class CustomButton(ft.ElevatedButton):
    def __init__(self, text, width=220, height=80, size=20, disable=False):
        super().__init__()
        self.content = ft.Text(value=text, size=size, color="#FFFFFF")
        self.style = ft.ButtonStyle(
            animation_duration=500,
            side={
                ft.MaterialState.DEFAULT: ft.BorderSide(4, "#FFFFFF"),
                ft.MaterialState.HOVERED: ft.BorderSide(4, "#BF36FF"),
            },
            bgcolor={ft.MaterialState.DEFAULT: "#006FF1"},
            shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=40)}
        )
        self.width, self.height = width, height
        self.disabled = disable
        if disable:
            self.opacity = 0.3
            self.content.opacity = 0.3

        self.animate_opacity = 300
        self.content.animate_opacity = 300


class Image_Window(ft.UserControl):
    def __init__(self, text_value, btn_text=None, btn_width=220, btn_height=80, btn_text_size=20, btn_disable=False,
                 width=600, height=600):
        super().__init__()
        # Размеры виджета
        self.width = width
        self.height = height

        # Элементы
        # Панель с текстом
        self.text = ft.Container(
            content=ft.Text(value=text_value, size=30, text_align="CENTER",
                            color="#FFFFFF"),
            alignment=ft.alignment.center,
            height=120,
            bgcolor="#006FF1"
        )

        # Кнопка либо изображение в окне
        self.container = ft.Container(
            content=CustomButton(btn_text, width=btn_width, height=btn_height, size=btn_text_size, disable=btn_disable),
            alignment=ft.alignment.center,
            height=self.height - self.text.height,
            visible=False if btn_text is None else True
        )

    def build(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    self.text,
                    self.container
                ],
                spacing=0
            ),
            width=self.width, height=self.height,
            alignment=ft.alignment.center,
            border=ft.border.all(2, color="#006FF1")
        )


def main(page: ft.Page):
    # ==================================================================
    #                               Функции                            #
    # ==================================================================
    def select_files(e):
        file_picker.pick_files(allowed_extensions=['jpeg', 'jpg', 'png'])

    def on_dialog_result(e: ft.FilePickerResultEvent):
        if e.files is not None:
            file_name = e.files[0].name
            left_block.text.content.value = f"Файл - {file_name}"
            left_block.text.content.update()
        page.update()

        # Загрузка файла
        upload_list = []
        for f in e.files:
            upload_list.append(
                ft.FilePickerUploadFile(
                    f.name,
                    upload_url=page.get_upload_url(f.name, 600)
                )
            )
            file_picker.upload(upload_list)

    def on_upload_progress(e: ft.FilePickerUploadEvent):
        if e.progress == 1.0:
            # Путь до папки с загруженным изображением
            src = f"assets/uploads/{file_picker.result.files[0].name}"
            # Добавляю вместо кнопки 'Загрузить' загруженное изображение
            left_block.container.content = ft.Image(src, width=600, height=600, fit=ft.ImageFit.COVER)
            # Делаю активной кнопку 'Предсказать'
            right_block.container.content.disabled = False
            right_block.container.content.opacity = 1.0
            right_block.container.content.content.opacity = 1.0


            # Обновляю страницу
            left_block.update()
            right_block.update()


    def predict(e, model=model, classes_dict=classes_dict):
        # Предсказание модели
        file_name = file_picker.result.files[0].name
        source = f"assets/uploads/{file_name}"
        results = model(source)

        for r in results:
            im_array = r.plot(conf=False, line_width=3)  # plot a BGR numpy array of predictions
            im = Image.fromarray(im_array[..., ::-1])  # RGB PIL image
            # im.show()  # show image
            im.resize((600, 600))

            # Сохранение файла
            im.save(f"assets/uploads/res_{file_name}")

            # Все предсказанные классы
            labels = r.boxes.cls.tolist()

            # Создаем словарь, чтобы отсортировать предсказания по порядку
            # слева-направо
            ordered_dict = {}

            # Добавляем название класса в labels
            for i in range(len(labels)):
                x_cord = r.boxes[i].xywh[0].tolist()[0]
                ordered_dict[x_cord] = classes_dict.get(labels[i])

            ordered_dict = {k: v for k, v in sorted(ordered_dict.items())}

            title = ''.join(ordered_dict.values())
            title = title[:4] + ' ' + title[4:]

            # Обновляем виджеты
            src = f"assets/uploads/res_{file_name}"
            # Добавляю вместо кнопки 'Загрузить' загруженное изображение
            right_block.container.content = ft.Image(src, width=600, height=600, fit=ft.ImageFit.COVER)
            # Обновляю текст Image_Window у правого блока
            right_block.text.content.value = f"Номер - {title}"

            # Обновляю страницу
            right_block.update()

            #


    # ==================================================================
    #                               Фронт                              #
    # ==================================================================
    # Настройки для всей страницы
    page.title = "Детектор автомобильных номеров"
    page.scroll = True
    page.bgcolor = "#C7BBC3"

    # Текст с названием приложения
    title = ft.Container(
        content=ft.Text("Детектор автомобильных номеров",
                        size=48, color="#006FF1"),
        alignment=ft.alignment.top_center,
        height=100
    )

    # Левый блок
    left_block = Image_Window("Исходное изображение", "Загрузить файл")
    left_block.container.content.on_click = select_files

    # Правый блок
    right_block = Image_Window("Результат", "Предсказать", btn_disable=True)
    # Нажатие на кнопку 'Предсказать'
    right_block.container.content.on_click = predict

    # FilePicker
    file_picker = ft.FilePicker(on_result=on_dialog_result, on_upload=on_upload_progress)
    page.overlay.append(file_picker)

    # Поместим все виджеты в строку (друг за другом)
    main_body = ft.Container(
        content=ft.Row(
            controls=[
                left_block,
                right_block
            ],
            alignment=ft.MainAxisAlignment.SPACE_AROUND
        )
    )

    # Добавляем виджеты на главную страницу приложения и обновляем
    page.add(title, main_body)
    page.update()


ft.app(target=main, assets_dir="assets", upload_dir="assets/uploads", view=ft.WEB_BROWSER,
       port=54734)
