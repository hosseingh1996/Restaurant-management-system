import sys
import pymysql
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QPushButton, QMainWindow, QMessageBox


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("restaurant.ui", self)


        try:
            self.db = pymysql.connect(
                host="localhost",
                user="root",
                password="",
                database="restaurant"
            )
            self.cursor = self.db.cursor()
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "Database Error", str(e))
            sys.exit(1)

        self.total_price = 0.00

        self.setup_menu_table()
        self.setup_table_table()

        self.order_button.clicked.connect(self.place_order)
        self.checkout_button.clicked.connect(self.checkout)

    def setup_menu_table(self):

            self.cursor.execute("SELECT * FROM menu")
            dishes = self.cursor.fetchall()

            self.menu_table.setRowCount(len(dishes))
            for row, (dish_id, dish_name, price, category) in enumerate(dishes):
                self.menu_table.setItem(row, 0, QTableWidgetItem(dish_name))
                self.menu_table.setItem(row, 1, QTableWidgetItem(f" تومان {price:.2f}"))
                self.menu_table.setItem(row, 2, QTableWidgetItem(category))


                self.dish_combo.addItem(dish_name)

    def setup_table_table(self):

            self.cursor.execute("SELECT * FROM tables")
            tables = self.cursor.fetchall()

            self.table_table.setRowCount(len(tables))
            for row, (table_id, table_number, status) in enumerate(tables):
                self.table_table.setItem(row, 0, QTableWidgetItem(str(table_number)))
                self.table_table.setItem(row, 1, QTableWidgetItem(status))

                action_button = QPushButton("رزرو" if status == "خالی" else "منتظر", self)
                action_button.clicked.connect(lambda _, tn=table_id, s=status: self.toggle_table_status(tn, s))
                self.table_table.setCellWidget(row, 2, action_button)

    def toggle_table_status(self, table_id, current_status):
        new_status = "پر" if current_status == "خالی" else "خالی"


        self.cursor.execute(
            "UPDATE tables SET status = %s WHERE id = %s",
            (new_status, table_id)
            )
        self.db.commit()
        self.setup_table_table()


    def place_order(self):
        dish = self.dish_combo.currentText().strip()
        quantity = self.quantity_input.text()

        if quantity.isdigit() and int(quantity) > 0:
            price = self.get_dish_price(dish)
            if price is not None:
                total_price = float(price.strip('تومان ')) * int(quantity)
                self.total_price += total_price

                self.update_total_label()


    def get_dish_price(self, dish_name):

            self.cursor.execute("SELECT price FROM menu WHERE name = %s", (dish_name,))
            result = self.cursor.fetchone()
            if result:
                return f"{result[0]:.2f}"
            else:
                print(f"No price found for dish: {dish_name}")



    def update_total_label(self):
        self.total_label.setText(f"Total: تومان {self.total_price:.2f}")

    def checkout(self):
        print(f"Total: {self.total_price:.2f}")
        self.total_price = 0.00
        self.update_total_label()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
