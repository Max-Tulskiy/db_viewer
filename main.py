from PySide6.QtWidgets import QApplication, QMainWindow
from window import Ui_MainWindow
import sys
import psycopg2
from config import host, user, password, db_name


class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


def main():
    #app = QApplication(sys.argv)
    #mainWindow = MyMainWindow()
    #mainWindow.show()
    #sys.exit(app.exec())
    try:
        connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)

        with connection.cursor() as cursor:
            cursor.execute("запрос тут")


    except Exception as ex:
        print("Не удалось подключиться к бд", ex)
    finally:
        if connection:
            connection.close()
            print("Коннект закрыт")


if __name__ == "__main__":
    main()
