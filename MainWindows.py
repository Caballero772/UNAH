import sys
from PyQt5.QtGui import QFont,QIcon,QMovie
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QBoxLayout, QVBoxLayout, QWidget,
                             QGroupBox, QLabel, QTextEdit)

from SimulationWindow import SimulationWindow

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.resize(500, 480)
        QMainWindow.setWindowFlags(self,Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Simulador")
        self.setWindowIcon(QIcon("Imagenes/venadocolaBlanca.png"))

        self.simulador = SimulationWindow()

        self.groupMain = QGroupBox(self)
        self.groupMain.setGeometry(QRect(5,5,490,470))
        self.diseñoGroupMain()
        self.ptInicio.clicked.connect(self.inicarSimulacion)

    def inicarSimulacion(self):
        self.hide()
        self.simulador.show()
        

    def diseñoGroupMain(self):
        self.movie = QMovie("Imagenes/binary6(re).gif")
        self.gif = QLabel(self.groupMain)
        self.gif.setGeometry(QRect(-50,0,600,290))
        self.gif.setScaledContents(True)
        self.gif.setMovie(self.movie)
        self.movie.start()

        self.editores = QTextEdit(self.groupMain)
        self.editores.setReadOnly(True)
        self.editores.setGeometry(QRect(0,290,490,120))
        self.editores.setPlainText("""                              Simulador ensamblador
María Fernanda Pineda         20161000446
Alexander Ismael Tejeda      20161005903
Virgilio Josué Caballero          20161000697
Cristian Jeanluc Boquín         20151020669
José Carlos Velásquez          20141031775""")

        font = QFont()
        font.setPointSize(11)                                                               #Tamaño de letra
        self.editores.setFont(font)
        self.ptInicio  = QPushButton(self.groupMain)
        self.ptInicio.setGeometry(QRect(0,410,490,60))
        self.ptInicio.setText("Iniciar Simulacion")
        self.ptInicio.setFont(font)
        self.ptInicio.setIcon(QIcon("Imagenes/computer.png"))


app = QApplication(sys.argv)
mainWindow= MainWindow()
mainWindow.show()
app.exec_()
