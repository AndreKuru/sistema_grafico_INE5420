import sys
from PyQt6 import QtWidgets, QtGui

from MainWindow import Ui_Widget


class MainWindow(QtWidgets.QMainWindow, Ui_Widget):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.draw_line()

    def draw_line(self):
        canvas = self.label.pixmap()
        painter = QtGui.QPainter(canvas)
        painter.drawLine(500, 500, 200, 200)
        painter.end()
        self.label.setPixmap(canvas)


app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()