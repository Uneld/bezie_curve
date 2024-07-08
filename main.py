import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtGui import QIntValidator, QFont
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QLineEdit, QPushButton, QMessageBox, \
    QLabel, QHBoxLayout, QTextEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from MyTable import MyTable
from CalcBezie import Point
from CalcBezie import de_casteljau


class MatplotlibWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Алгоритм де Кастельжо для кривой Бизье")

        # self.setFixedHeight()

        self.mtwidget = QWidget(self)
        self.setCentralWidget(self.mtwidget)
        self.layout = QVBoxLayout(self.mtwidget)
        self.layout_h = QHBoxLayout(self.mtwidget)
        self.layout_v1 = QVBoxLayout(self.mtwidget)
        self.layout_v2 = QVBoxLayout(self.mtwidget)
        self.layout_v3 = QVBoxLayout(self.mtwidget)

        self.label = QLabel('Задание точек для кривой Бизье')
        self.label.setFixedHeight(20)
        self.layout.addWidget(self.label)

        self.table = MyTable(1, 8)  # Пример: таблица 10x5
        self.table.setHorizontalHeaderLabels(
            ["P0 x", "P0 y", "P1 x", "P1 y", "P2 x", "P2 y", "P3 x", "P3 y"])  # Заголовки столбцов
        self.table.setFixedHeight(80)
        self.layout.addWidget(self.table)

        self.label1 = QLabel('Количество точек')
        self.label1.setFixedHeight(20)
        self.layout_v1.addWidget(self.label1)
        self.le_num_cells = QLineEdit('10')
        self.le_num_cells.setValidator(QIntValidator())
        self.le_num_cells.textChanged.connect(self.btn_calc_clicked)
        self.layout_v1.addWidget(self.le_num_cells)

        self.label2 = QLabel('Входная величина')
        self.label2.setFixedHeight(20)
        self.layout_v2.addWidget(self.label2)
        self.le_input = QLineEdit('1024')
        self.le_input.setValidator(QIntValidator())
        self.le_input.textChanged.connect(self.btn_calc_clicked)
        self.layout_v2.addWidget(self.le_input)

        self.label3 = QLabel('Выходная величина')
        self.label3.setFixedHeight(20)
        self.layout_v3.addWidget(self.label3)
        self.le_output = QLineEdit('1024')
        self.le_output.setValidator(QIntValidator())
        self.le_output.textChanged.connect(self.btn_calc_clicked)
        self.layout_v3.addWidget(self.le_output)

        self.layout_h.addLayout(self.layout_v1)
        self.layout_h.addLayout(self.layout_v2)
        self.layout_h.addLayout(self.layout_v3)
        self.layout.addLayout(self.layout_h)

        # self.button = QPushButton("Расчет")
        # self.button.clicked.connect(self.btn_calc_clicked)
        # self.button.setFixedWidth(820)
        # self.layout.addWidget(self.button)

        self.fig = plt.figure()
        self.canvas = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas)

        self.ax = self.fig.add_subplot(111)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout.addWidget(self.toolbar)

        self.font = QFont()
        self.font.setPointSize(10)
        self.te_to_c = QTextEdit()
        self.te_to_c.setFixedHeight(100)
        self.te_to_c.setFont(self.font)
        self.layout.addWidget(self.te_to_c)
        self.table.cellChanged.connect(self.btn_calc_clicked)
        self.btn_calc_clicked()

    def btn_calc_clicked(self):

        list_table = self.table.get_table_data()
        if not list_table:
            return
        # print(list_table)
        mapped = list(map(self.chunks_mapper, list_table[0]))
        # print(mapped)
        if len(mapped) == 8:
            p0 = Point(mapped[0], mapped[1])
            p1 = Point(mapped[2], mapped[3])
            p2 = Point(mapped[4], mapped[5])
            p3 = Point(mapped[6], mapped[7])
        else:
            return

        try:
            duration = 1.0
            num_chuck = int(self.le_num_cells.text())
            if num_chuck > 0:
                time_step = (duration / num_chuck + duration) / num_chuck
            else:
                time_step = 1
        except ValueError:
            return

        t = 0.0
        x_list = []
        y_list = []
        while t <= 1.0:
            result = de_casteljau(p0, p1, p2, p3, t)
            x_list.append(result.x)
            y_list.append(result.y)
            # print(f"Точка на кривой Безье с параметром t={t} : ({result.x}, {result.y})")

            t += time_step / duration

        # print(len(x_list))
        self.ax.clear()
        self.ax.plot(x_list, y_list)
        self.ax.set_xlim(0, 1.0)  # Максимальное значение по оси X
        self.ax.set_ylim(0, 1.0)  # Максимальное значение по оси Y
        self.draw_point(p0, 'P0')
        self.draw_point(p1, 'P1')
        self.draw_point(p2, 'P2')
        self.draw_point(p3, 'P3')
        self.canvas.draw()

        out_x = list(map(self.calc_in_val, x_list))
        # print(out_x)
        out_y = list(map(self.calc_out_val, y_list))
        # print(out_y)

        text = '\n'.join([
            f'uint8_t SIZE_DATA_BEZIER = {len(x_list)};',
            f'uint32_t data_bezier_input[SIZE_DATA_BEZIER] = ' + '{' + ', '.join(str(item) for item in out_x) + '};',
            f'uint32_t data_bezier_output[SIZE_DATA_BEZIER] = ' + '{' + ', '.join(str(item) for item in out_y) + '};',
        ])

        self.te_to_c.clear()
        self.te_to_c.setPlainText(text)

    def draw_point(self, point, text):
        self.ax.scatter(point.x, point.y)
        self.ax.annotate(text, (point.x, point.y), textcoords="offset points", xytext=(10, -10), ha='center')

    def chunks_mapper(self, chunk):
        try:
            return float(chunk.replace(',', '.'))
        except ValueError:
            QMessageBox.warning(self, 'Ошибка', 'Косяк с преобразованием')

    def calc_in_val(self, chunk):
        try:
            return round(chunk * float(self.le_input.text()))
        except ValueError:
            return

    def calc_out_val(self, chunk):
        try:
            return round(chunk * float(self.le_output.text()))
        except ValueError:
            return


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MatplotlibWidget()
    mainWindow.show()
    sys.exit(app.exec_())
