from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
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

        self.ui.tableWidget_2.setColumnCount(6)
        self.ui.tableWidget_2.setRowCount(1)
        self.ui.tableWidget_2.setHorizontalHeaderLabels(["Код туриста", "Серия паспорта", "Город", "Страна", "Телефон", "Индекс"])

        self.ui.tableWidget.setColumnWidth(0, 130)
        self.ui.tableWidget.setColumnWidth(1, 150)
        self.ui.tableWidget.setColumnWidth(2, 150)
        self.ui.tableWidget.setColumnWidth(3, 150)

        self.ui.tableWidget_2.setColumnWidth(0, 98)
        self.ui.tableWidget_2.setColumnWidth(1, 100)
        self.ui.tableWidget_2.setColumnWidth(2, 100)
        self.ui.tableWidget_2.setColumnWidth(3, 100)
        self.ui.tableWidget_2.setColumnWidth(4, 100)
        self.ui.tableWidget_2.setColumnWidth(5, 100)
        self.ui.tableWidget_2.setRowHeight(0, 50)

        vertical_header = self.ui.tableWidget_2.verticalHeader()
        vertical_header.setVisible(False)
        
        self.showDataFromDB()
        self.ui.tableWidget.cellClicked.connect(self.showRelatedInfoTouristData)

        self.ui.pushButton_4.clicked.connect(self.addRow)
        self.ui.pushButton_2.clicked.connect(self.editDataInTourist)

        self.ui.pushButton.clicked.connect(self.add_data_to_tourist)
        self.ui.pushButton_3.clicked.connect(self.removeDataFromDb)


    def showDataFromDB(self):
        connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM tourist ORDER BY id")
            rows = cursor.fetchall()
            
            for row_number, row_data in enumerate(rows):
                self.ui.tableWidget.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.ui.tableWidget.setItem(row_number, column_number, item)
                    
        connection.close()


    def showRelatedInfoTouristData(self):
        selected_row = self.ui.tableWidget.currentRow()
        if selected_row >= 0:
            item = self.ui.tableWidget.item(selected_row, 0)
            if item is not None:
                id_tourist = int(item.text())
                self.ui.tableWidget_2.clearContents()
                self.showInfoTouristDataForId(id_tourist)


    def showInfoTouristDataForId(self, id_tourist):
        connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM info_tourist WHERE id_tourist = %s", (id_tourist,))
            rows = cursor.fetchall()

            for row_number, row_data in enumerate(rows):
                for column_number, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.ui.tableWidget_2.setItem(row_number, column_number, item)

        connection.close()


    def addRow(self):
        row_position = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(row_position)
        self.ui.tableWidget_2.clearContents()


    def add_data_to_tourist(self):
        try:
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

            self.add_data_to_info_tourist()
        except Exception as ex:
            messageBox = QMessageBox()
            messageBox.setIcon(QMessageBox.Warnibg)
            messageBox.setWindowTitle("Предупреждение")
            messageBox.setText("Ошибка при добавлении данных!")
            messageBox.exec()
        finally:
            messageBox = QMessageBox()
            messageBox.setIcon(QMessageBox.Information)
            messageBox.setWindowTitle("Инфо")
            messageBox.setText("Данные успешно добавлены")
            messageBox.exec()


    def add_data_to_info_tourist(self):
        id_tourist = self.ui.tableWidget_2.item(0, 0).text()
        passport_number = self.ui.tableWidget_2.item(0, 1).text()
        city = self.ui.tableWidget_2.item(0, 2).text()
        country = self.ui.tableWidget_2.item(0, 3).text()
        phone_number = self.ui.tableWidget_2.item(0, 4).text()
        city_index = self.ui.tableWidget_2.item(0, 5).text()
        
        if not all([id_tourist, passport_number, city, country, phone_number, city_index]): return

        connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)

        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM tourist WHERE id = %s", (id_tourist,))
            existing_id = cursor.fetchone()
           
            if not existing_id:
                messageBox = QMessageBox()
                messageBox.setIcon(QMessageBox.Warning)
                messageBox.setWindowTitle("Предупреждение")
                messageBox.setText("Нельзя добавить запись, т.к пользователь не существует")
                messageBox.exec()
                return

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO info_tourist (id_tourist, passport_number, city, country, phone_number, city_index) VALUES (%s, %s, %s, %s, %s, %s)", (id_tourist, passport_number, city, country, phone_number, city_index))
            connection.commit()


    def editDataInTourist(self):
        try:
            connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)
            cursor = connection.cursor()

            for row in range(self.ui.tableWidget.rowCount()):
                id = int(self.ui.tableWidget.item(row, 0).text())  
                first_name = self.ui.tableWidget.item(row, 1).text()  
                second_name = self.ui.tableWidget.item(row, 2).text()  
                patronymic = self.ui.tableWidget.item(row, 3).text()
                
                cursor.execute("""
                    UPDATE tourist 
                    SET first_name = %s, second_name = %s, patronymic = %s 
                    WHERE id = %s
                """, (first_name, second_name, patronymic, id))

            connection.commit()
            cursor.close()
            connection.close()

            self.editDataInInfoTourist()
        except Exception:
            messageBox = QMessageBox()
            messageBox.setIcon(QMessageBox.Warning)
            messageBox.setWindowTitle("Предупреждение")
            messageBox.setText("Ошибка во время изменения данных!")
            messageBox.exec()
        finally:
            messageBox = QMessageBox()
            messageBox.setIcon(QMessageBox.Information)
            messageBox.setWindowTitle("Инфо")
            messageBox.setText("Данные успешно обновлены!")
            messageBox.exec()


    def editDataInInfoTourist(self):
        connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)
        cursor = connection.cursor()

        for row in range(self.ui.tableWidget_2.rowCount()):
            id_tourist = int(self.ui.tableWidget_2.item(row, 0).text())  
            passport_number = self.ui.tableWidget_2.item(row, 1).text()  
            city = self.ui.tableWidget_2.item(row, 2).text()  
            country = self.ui.tableWidget_2.item(row, 3).text()
            phone_number = self.ui.tableWidget_2.item(row, 4).text()
            city_index = self.ui.tableWidget_2.item(row, 5).text()

            cursor.execute("""
                UPDATE info_tourist 
                SET passport_number = %s, city = %s, country = %s, phone_number = %s, city_index = %s 
                WHERE id_tourist = %s
            """, (passport_number, city, country, phone_number, city_index, id_tourist))

        connection.commit()
        cursor.close()
        connection.close()


    def removeDataFromDb(self):
        current_row = self.ui.tableWidget.currentRow()
        connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)

        if current_row != -1:  
            id_item = self.ui.tableWidget.item(current_row, 0)
            id_value = id_item.text()

            self.ui.tableWidget.removeRow(current_row)
            self.ui.tableWidget_2.clearContents()

            cursor = connection.cursor()
            cursor.execute("DELETE FROM info_tourist WHERE id_tourist = %s", (id_value,))
            cursor.execute("DELETE FROM tourist WHERE id = %s", (id_value,))
            connection.commit()
            cursor.close()

            messageBox = QMessageBox()
            messageBox.setIcon(QMessageBox.Information)
            messageBox.setWindowTitle("Инфо")
            messageBox.setText("Данные успешно удалены!")
            messageBox.exec()


def main():
    app = QApplication(sys.argv)
    mainWindow = MyMainWindow()
    mainWindow.setWindowTitle("DB_Viewer")
    mainWindow.setWindowIcon(QIcon("icon.png"))
    mainWindow.setFixedSize(800, 600)
    mainWindow.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
