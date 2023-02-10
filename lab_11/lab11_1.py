import io
import sys
import psycopg2
from PIL import Image
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
    QPushButton,
    QLineEdit,
    QFileDialog, QLabel
)


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.connection = None
        self.cursor = None
        move_btn = 850
        self.con()

        # параметры окна
        self.setGeometry(1200, 1000, 1200, 1000)
        self.setWindowTitle('Журнал контактов / lab 11')
        self.tb = Tb(self)

        # кнопка "обновить"
        self.btn = QPushButton('Обновить', self)
        self.btn.resize(200, 40)
        self.btn.move(move_btn, 10)
        self.btn.clicked.connect(self.upd)

        # first_name
        self.fn = QLineEdit(self)
        self.fn.resize(200, 40)
        self.fn.move(move_btn, 110)

        # здесь surname
        self.sn = QLineEdit(self)
        self.sn.resize(200, 40)
        self.sn.move(move_btn, 160)

        # здесь phone
        self.ph = QLineEdit(self)
        self.ph.resize(200, 40)
        self.ph.move(move_btn, 210)

        # id
        self.idp = QLineEdit(self)
        self.idp.resize(200, 40)
        self.idp.move(move_btn, 60)
        self.idp.setReadOnly(True)

        # кнопка добавить запись
        self.btn = QPushButton('Добавить', self)
        self.btn.resize(200, 40)
        self.btn.move(move_btn, 260)
        self.btn.clicked.connect(self.ins)

        # кнопка удалить запись
        self.btn = QPushButton('Удалить', self)
        self.btn.resize(200, 40)
        self.btn.move(move_btn, 320)
        self.btn.clicked.connect(self.dels)

    # соединение с базой данных
    def con(self):
        self.connection = psycopg2.connect(
            user="postgres",
            password="postgres",
            host="0.0.0.0",
            port="5432",
            database="postgres"
        )
        self.cursor = self.connection.cursor()

    # обновить таблицу
    def upd(self):
        self.connection.commit()
        self.tb.updt()
        self.fn.setText('')
        self.sn.setText('')
        self.ph.setText('')

    # добавить таблицу новую строку
    def ins(self):
        fn, sn, ph = self.fn.text(), self.sn.text(), self.ph.text()

        self.cursor.execute(f"insert into contats (first_name, surname, phone) values ('{fn}','{sn}', '{ph}')")

        self.upd()

    # удалить из таблицы строку
    def dels(self):
        try:
            ids = int(self.idp.text())  # идентификатор строки
        except:
            return
        self.cursor.execute(f"delete from contats where id={ids}")
        self.upd()


# класс - таблица
class Tb(QTableWidget):
    def __init__(self, wg):
        self.another_window = None
        self.wg = wg  # запомнить окно, в котором эта таблица показывается
        super().__init__(wg)
        self.setGeometry(10, 10, 800, 500)
        self.setColumnCount(5)

        self.updt()  # обновить таблицу
        self.setEditTriggers(QTableWidget.NoEditTriggers)  # запретить изменять поля
        self.cellClicked.connect(self.cell_click)  # установить обработчик щелка мыши в таблице

    # обновление таблицы
    def updt(self):
        self.clear()
        self.setRowCount(0)
        self.setHorizontalHeaderLabels(['Имя', 'Фамилия', 'Телефон', 'Фото', 'id'])  # заголовки столбцов
        self.wg.cursor.execute("select * from contats order by id")
        rows = self.wg.cursor.fetchall()
        i = 0
        for elem in rows:
            self.setRowCount(self.rowCount() + 1)
            j = 0
            for t in elem:  # заполняем внутри строки
                if j % 10 == 3:
                    self.setItem(i, j, QTableWidgetItem('Фото' if t is not None else str(t)))
                else:
                    self.setItem(i, j, QTableWidgetItem(str(t).strip()))
                j += 1

            i += 1
        self.resizeColumnsToContents()

    # обработка щелчка мыши по таблице
    def cell_click(self, row, col):
        if col == 3:
            id = self.item(row, 4).text()
            if self.item(row, 3).text() == 'None':
                img_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "~", "Images (*.png *.jpg)")
                if img_path:
                    fin = open(img_path, "rb")
                    img_file = fin.read()
                    binary = psycopg2.Binary(img_file)
                    self.wg.cursor.execute(f"UPDATE contats SET photo = %s where id = {id}", (binary,))
                    self.wg.connection.commit()
                    fin.close()
                    self.updt()
            else:
                self.wg.cursor.execute(f"select photo from contats where id = {id}")
                self.another_window = AnotherWindow(self.wg.cursor.fetchone()[0])
                self.another_window.show()

        else:
            self.wg.fn.setText(self.item(row, 0).text().strip())
            self.wg.sn.setText(self.item(row, 1).text().strip())
            self.wg.ph.setText(self.item(row, 2).text().strip())
            self.wg.idp.setText(self.item(row, 4).text())


class AnotherWindow(QWidget):
    def __init__(self, binary_img):
        super(AnotherWindow, self).__init__()

        self.setWindowTitle('Painter Board')
        self.label = QLabel(self)

        qp = QPixmap()
        qp.loadFromData(binary_img)
        img = Image.open(io.BytesIO(binary_img))
        self.resize(img.width, img.height)
        self.label.setPixmap(qp)


app = QApplication(sys.argv)
ex = MyWidget()
ex.show()
app.exec()
