from PySide6.QtWidgets import QApplication, QMessageBox
from mainwindow import MainWindow
import sys

app = QApplication([])
window = MainWindow()

window.showMinimized()
#window.show()
sys.exit(app.exec())

print("app chiusa")


   

