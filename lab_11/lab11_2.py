import sys
from PyQt5.QtWidgets import (
    QApplication,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
    QPushButton,
    QLabel,
    QLineEdit, QMessageBox
)
from sqlalchemy import create_engine, select, insert, delete

from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from lab_11.lab11_2_table import Teams, FootballPlayers

engine: Engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres")
session = sessionmaker(bind=engine, expire_on_commit=False, future=True)
session = session()


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.connection = None
        self.cursor = None
        move_btn = 350
        self.team_table = Teams.__table__

        # параметры окна
        self.setGeometry(1500, 500, 1500, 500)
        self.setWindowTitle('Футбол / lab 11_2')

        self.tb_team = Tb(
            self, x=10, y=10, wight=300, height=400,
            labels=['id', 'name', 'raiting'],
            db_table=Teams
        )

        self.label = QLabel(self)
        self.label.setText('Поля для заполнения')
        self.label.move(320, 10)

        self.id = QLineEdit(self)
        self.id.resize(200, 40)
        self.id.move(move_btn, 60)

        self.name = QLineEdit(self)
        self.name.resize(200, 40)
        self.name.move(move_btn, 110)

        self.raiting = QLineEdit(self)
        self.raiting.resize(200, 40)
        self.raiting.move(move_btn, 160)

        # кнопка добавить запись
        self.btn = QPushButton('Добавить team', self)
        self.btn.resize(200, 40)
        self.btn.move(move_btn, 210)
        self.btn.clicked.connect(self.ins_team)

        # кнопка удалить запись
        self.btn = QPushButton('Удалить team', self)
        self.btn.resize(200, 40)
        self.btn.move(move_btn, 260)
        self.btn.clicked.connect(self.delete_team)

        # --------------------
        move_btn = 1200
        self.fb_tb = Tb(
            self, x=650, y=10, wight=520, height=400,
            labels=['fb_id', 'first_name', 'last_name', 'team_id'],
            db_table=FootballPlayers
        )

        self.fb_label = QLabel(self)
        self.fb_label.setText('Поля футболистов')
        self.fb_label.move(1180, 10)

        self.fb_id = QLineEdit(self)
        self.fb_id.resize(200, 40)
        self.fb_id.move(move_btn, 60)

        self.first_name = QLineEdit(self)
        self.first_name.resize(200, 40)
        self.first_name.move(move_btn, 110)

        self.last_name = QLineEdit(self)
        self.last_name.resize(200, 40)
        self.last_name.move(move_btn, 160)

        self.team_id = QLineEdit(self)
        self.team_id.resize(200, 40)
        self.team_id.move(move_btn, 210)

        # кнопка добавить запись
        self.btn = QPushButton('Добавить игрока', self)
        self.btn.resize(240, 40)
        self.btn.move(move_btn - 20, 260)
        self.btn.clicked.connect(self.ins_fb)

        # кнопка удалить запись
        self.btn = QPushButton('Удалить игрока', self)
        self.btn.resize(240, 40)
        self.btn.move(move_btn - 20, 310)
        self.btn.clicked.connect(self.delete_fb)

    def upd_team(self):
        self.tb_team.updt()
        self.id.setText('')
        self.name.setText('')
        self.raiting.setText('')

    def ins_team(self):
        id, name, raiting = int(self.id.text()), self.name.text(), self.raiting.text()
        query = insert(Teams).values(id=id, name=name, raiting=raiting)
        session.execute(query)
        session.commit()
        self.upd_team()

    def delete_team(self):
        id = int(self.id.text())
        query = delete(Teams).where(Teams.id == id)
        session.execute(query)
        session.commit()
        self.upd_team()

    # ---------------------

    def upd_fb(self):
        self.fb_tb.updt()
        self.fb_id.setText('')
        self.first_name.setText('')
        self.last_name.setText('')
        self.team_id.setText('')

    def ins_fb(self):
        fb_id, first_name, last_name, team_id = int(
            self.fb_id.text()
        ), self.first_name.text(), self.last_name.text(), self.team_id.text()

        query = insert(FootballPlayers).values(fb_id=fb_id, first_name=first_name, last_name=last_name, team_id=team_id)
        try:
            session.execute(query)
        except Exception as ex:
            print(ex)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Введите другой team_id")
            msg.setInformativeText('Данной команды не существует')
            msg.setWindowTitle("Ошибка")
            msg.exec_()
        session.commit()
        self.upd_fb()

    def delete_fb(self):
        id = int(self.fb_id.text())
        query = delete(FootballPlayers).where(FootballPlayers.fb_id == id)
        session.execute(query)
        session.commit()
        self.upd_fb()


class Tb(QTableWidget):
    def __init__(self, wg, x, y, wight, height, labels, db_table):
        self.another_window = None
        self.wg = wg  # запомнить окно, в котором эта таблица показывается
        super().__init__(wg)
        self.setGeometry(x, y, wight, height)
        self.setColumnCount(len(labels))
        self.labels = labels
        self.db_table = db_table
        self.updt()
        self.cellClicked.connect(self.cell_click)  # установить обработчик щелка мыши в таблице
        self.setEditTriggers(QTableWidget.NoEditTriggers)  # запретить изменять поля

    def updt(self):
        self.clear()
        self.setRowCount(0)
        self.setHorizontalHeaderLabels(self.labels)  # заголовки столбцов

        query = select(self.db_table)
        queryset = session.execute(query)

        row = 0
        for obj in queryset.scalars().all():
            self.setRowCount(self.rowCount() + 1)
            col = 0
            for attr in self.labels:
                self.setItem(row, col, QTableWidgetItem(str(getattr(obj, attr))))
                col += 1
            row += 1
        self.resizeColumnsToContents()

    def cell_click(self, row, col):
        count = 0
        for attr in self.labels:
            getattr(self.wg, attr).setText(self.item(row, count).text().strip())
            count += 1


app = QApplication(sys.argv)
ex = MyWidget()
ex.show()
app.exec()
