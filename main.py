from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from window import Ui_MainWindow
import sys
import psycopg2
from config import host, user, password, db_name


class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.ui.tableWidget.setColumnCount(4)

        self.ui.tableWidget.setHorizontalHeaderLabels(["Код туриста", "Фамилия", "Имя", "Отчество"])

        self.showDataFromDB()
        
        self.ui.pushButton_4.clicked.connect(self.addRow)
        self.ui.pushButton_2.clicked.connect(self.editDataInDB)
        self.ui.tableWidget.itemChanged.connect(self.editDataInDB)
        self.ui.pushButton.clicked.connect(self.add_data_to_database)
        self.ui.pushButton_3.clicked.connect(self.removeDataFromDb)

    def showDataFromDB(self):
        connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM tourist ORDER BY id")
            rows = cursor.fetchall()

            for row_number, row_data in enumerate(rows):
                self.ui.tableWidget.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.ui.tableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def addRow(self):
        row_position = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(row_position)

    #Добавить
    def add_data_to_database(self):
        
        num_rows = self.ui.tableWidget.rowCount()
        connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)
        
        for row in range(num_rows):
            id_item = self.ui.tableWidget.item(row, 0)
            name_item = self.ui.tableWidget.item(row, 1)
            surname_item = self.ui.tableWidget.item(row, 2)
            patronymic_item = self.ui.tableWidget.item(row, 3)

            if not all([id_item, name_item, surname_item, patronymic_item]):
                continue

            id_value = id_item.text()
            first_name_value = name_item.text()
            second_name_value = surname_item.text()
            patronymic_value = patronymic_item.text()

            cursor = connection.cursor()
            cursor.execute("SELECT id FROM tourist WHERE id = %s", (id_value,))
            existing_id = cursor.fetchone()

            if existing_id:
                continue

            cursor.execute("INSERT INTO tourist (id, first_name, second_name, patronymic) VALUES (%s, %s, %s, %s)", (id_value, first_name_value, second_name_value, patronymic_value))
            connection.commit()

            cursor.close()
            connection.close()

    #Изменить
    def editDataInDB(self, item):
        mappa = {'Код туриста': 'id', 'Фамилия': 'second_name', 'Имя': 'first_name', 'Отчество': 'patronymic'}
        row = item.row()
        column = item.column()
        new_value = item.text()

        id_item = self.ui.tableWidget.item(row, 0)
        id_value = id_item.text()

        connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)
        cursor = connection.cursor()
        cursor.execute("UPDATE tourist SET {} = %s WHERE id = %s".format(mappa[self.ui.tableWidget.horizontalHeaderItem(column).text()]), (new_value, id_value))
        connection.commit()
        cursor.close()
        connection.close()

    #Удалить
    def removeDataFromDb(self):
        current_row = self.ui.tableWidget.currentRow()
        connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)

        if current_row != -1:  
            id_item = self.ui.tableWidget.item(current_row, 0)
            id_value = id_item.text()

            self.ui.tableWidget.removeRow(current_row)

            cursor = connection.cursor()
            cursor.execute("DELETE FROM tourist WHERE id = %s", (id_value,))
            connection.commit()
            cursor.close()


def main():
    app = QApplication(sys.argv)
    mainWindow = MyMainWindow()
    mainWindow.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
