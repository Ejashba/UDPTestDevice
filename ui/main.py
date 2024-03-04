import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QThread, pyqtSignal
from TestWindow import TestWindow
from PyQt5.QtNetwork import QUdpSocket, QHostAddress

test_host = '0.0.0.0'
test_port = '100'

if __name__ == '__main__':
    app = QApplication([])
    testing_window = TestWindow(test_host, test_port)
    testing_window.show()
    sys.exit(app.exec())

#app = QApplication([])

#window = QWidget()
#window.setWindowTitle("Satellite Test App")
#window.setGeometry(150, 150, 500, 500)
#helloMsg = QLabel("<h1>Hello, World!</h1>", parent=window)
#helloMsg.move(60, 15)

#window.show()
#sys.exit(app.exec())