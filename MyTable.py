from builtins import len

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QMenu, QAction, QStyledItemDelegate, \
    QMessageBox, QAbstractItemView, QItemDelegate
from PyQt5.QtGui import QKeySequence, QDoubleValidator


def clear_clipboard():
    clipboard = QApplication.clipboard()
    clipboard.clear()


def check_digits_in_array(arr):
    for string in arr:
        if not string.isdigit():  # Если строка не состоит только из цифр
            return False
    return True


class FloatDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        if editor is not None:
            validator = QDoubleValidator(parent)
            validator.setRange(0, 1, 2)
            editor.setValidator(validator)
        return editor


class MyTable(QTableWidget):
    def __init__(self, rows, columns):
        super().__init__(rows, columns)
        self.setRowCount(rows)
        self.setColumnCount(columns)

        self.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.setSelectionBehavior(QTableWidget.SelectItems)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_menu)
        self.bind_action()
        delegate = FloatDelegate(self)
        self.setItemDelegate(delegate)

        self.set_table_data('')

        self.stepKey = {Qt.Key_Q: 0.01, Qt.Key_A: -0.01, Qt.Key_W: 0.1, Qt.Key_S: -0.1, Qt.Key_E: 1, Qt.Key_D: -1}

    def set_cell_value(self, Key, value):
        self.stepKey[Key] = value

    def bind_action(self):
        copy_action = QAction("Copy", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.copy)
        self.addAction(copy_action)

        paste_action = QAction("Paste", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.paste)
        self.addAction(paste_action)

    def open_menu(self, position):
        menu = QMenu()
        copy_action = menu.addAction("Copy")
        copy_action.triggered.connect(self.copy)
        paste_action = menu.addAction("Paste")
        paste_action.triggered.connect(self.paste)
        clear_action = menu.addAction("Clear clipboard")
        clear_action.triggered.connect(clear_clipboard)
        menu.exec_(self.mapToGlobal(position))

    def keyPressEvent(self, event):
        selected_range = self.selectedRanges()[0]
        keys_to_values = {
            Qt.Key_Q: 0.01,
            Qt.Key_A: -0.01,
            Qt.Key_W: 0.1,
            Qt.Key_S: -0.1,
            Qt.Key_E: 1.0,
            Qt.Key_D: -1.0
        }

        if event.key() in keys_to_values:
            for row in range(selected_range.topRow(), selected_range.bottomRow() + 1):
                for col in range(selected_range.leftColumn(), selected_range.rightColumn() + 1):
                    cell_value = self.get_cell_value(row, col).replace(',', '.')
                    step_value = keys_to_values[event.key()]

                    try:
                        cell_val = float(cell_value)
                        new_cell_val = cell_val + step_value

                        if new_cell_val > 1.0:
                            new_cell_val = 1.0
                        elif new_cell_val < 0.0:
                            new_cell_val = 0.0

                        self.change_cell_value(row, col, str(round(new_cell_val, 2)).replace('.', ','))
                    except ValueError:
                        print("Value is not a float")
        else:
            super().keyPressEvent(event)

    def get_cell_value(self, row, column):
        item = self.item(row, column)
        if item is not None:
            return item.text()
        else:
            return None

    def set_table_data(self, value):
        self.change_cell_value(0, 0, "0,0")  # Изменить значение ячейки в строке 0, столбце 0
        self.change_cell_value(0, 1, "0,0")  # Изменить значение ячейки в строке 0, столбце 0
        self.change_cell_value(0, 2, "0,0")  # Изменить значение ячейки в строке 0, столбце 0
        self.change_cell_value(0, 3, "0,5")  # Изменить значение ячейки в строке 0, столбце 0
        self.change_cell_value(0, 4, "1,0")  # Изменить значение ячейки в строке 0, столбце 0
        self.change_cell_value(0, 5, "0,5")  # Изменить значение ячейки в строке 0, столбце 0
        self.change_cell_value(0, 6, "1,0")  # Изменить значение ячейки в строке 0, столбце 0
        self.change_cell_value(0, 7, "1,0")  # Изменить значение ячейки в строке 0, столбце 0

    def get_table_data(self):
        data = []
        for row in range(self.rowCount()):
            row_data = []
            for column in range(self.columnCount()):
                item = self.item(row, column)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append('')
            data.append(row_data)
        return data

    def change_cell_value(self, row, column, new_value):
        item = self.item(row, column)
        if item is None:
            item = QTableWidgetItem(str(new_value))
            self.setItem(row, column, item)
        else:
            item.setText(str(new_value))

    def copy(self):
        if self.hasFocus():
            selected = self.selectedRanges()
            s = ""
            for r in range(selected[0].topRow(), selected[0].bottomRow() + 1):
                for c in range(selected[0].leftColumn(), selected[0].rightColumn() + 1):
                    try:
                        s += str(self.item(r, c).text()) + '\t'
                    except AttributeError:
                        s += '\t'
                s = s[:-1] + '\n'  # eliminate last '\t'
            clipboard = QApplication.clipboard()
            clipboard.setText(s)

    def paste(self):
        clipboard = QApplication.clipboard()
        data = clipboard.text()
        rows = data.split('\n')
        selected = self.selectedRanges()

        if rows[0]:
            for i, row in enumerate(rows):
                if row:
                    cells = row.split('\t')
                    for j, cell in enumerate(cells):
                        try:
                            float(cell.replace(',', '.'))
                        except ValueError:
                            QMessageBox.warning(self, 'Ошибка', 'В буфере содержатся не только цифры')
                            return

        len_rows = len(rows) - 1
        if len_rows == 1:
            if rows[0]:
                columns = rows[0].split('\t')
                if len(columns) == 1:
                    for r in range(selected[0].topRow(), selected[0].bottomRow() + 1):
                        for c in range(selected[0].leftColumn(), selected[0].rightColumn() + 1):
                            self.change_cell_value(r, c, rows[0])
                elif len(columns) == self.columnCount():
                    for r in range(selected[0].topRow(), selected[0].bottomRow() + 1):
                        for c in range(0, self.columnCount()):
                            self.change_cell_value(r, c, columns[c])
        elif len_rows == self.rowCount():
            for r in range(0, self.rowCount()):
                if rows[r]:
                    for c in range(selected[0].leftColumn(), selected[0].rightColumn() + 1):
                        self.change_cell_value(r, c, rows[r])
        else:
            for i, row in enumerate(rows):
                if row:
                    cells = row.split('\t')
                    print(check_digits_in_array(cells))
                    for j, cell in enumerate(cells):
                        if cell:
                            target_row = (i + selected[0].topRow()) % self.rowCount()
                            target_column = (j + selected[0].leftColumn()) % self.columnCount()
                            for selected_range in selected:
                                if (selected_range.topRow() <= target_row <= selected_range.bottomRow() and
                                        selected_range.leftColumn() <= target_column <= selected_range.rightColumn()):
                                    self.change_cell_value(target_row, target_column, cell)
