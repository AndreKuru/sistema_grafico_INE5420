import sys
from PyQt6 import QtWidgets

from MainWindow import Ui_Widget
from Creating_New_Object import Ui_Dialog

class Creating_New_Object_Window(QtWidgets.QWidget, Ui_Dialog):
    def __init__(self) -> None:
        super(Creating_New_Object_Window, self).__init__()
        self.setupUi(self)


class MainWindow(QtWidgets.QMainWindow, Ui_Widget):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.pushButton_Create.clicked.connect(self.show_creating_new_object)
        self.dialog = Creating_New_Object_Window()

    def show_creating_new_object(self, checked):
        window = Creating_New_Object_Window()
        window.show()


app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()