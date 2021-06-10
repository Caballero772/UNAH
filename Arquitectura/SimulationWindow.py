import sys
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QIcon, QPixmap, QMovie
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QFrame, QWidget, QPlainTextEdit, QGroupBox, QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView
from Codigo import Codigo

class SimulationWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        QMainWindow.setWindowFlags(self,Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Simulador")
        self.setWindowIcon(QIcon("Imagenes/venadocolaBlanca.png"))
        self.resize(800,580)
        
        self.fondoMainWindow()
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.codigo = Codigo("Codigo.txt")
        self.grupoDeComponentes()
        self.separadores()
        self.ptEjecutar.clicked.connect(self.prueba)
        self.ptNuevo.clicked.connect(self.limpiarVentana)

    def limpiarVentana(self):
        self.cuadroDeTexto.setPlainText("")

    def prueba(self):
        fileW = open("Codigo.txt","w")
        fileW.write(self.cuadroDeTexto.toPlainText())
        fileW.close()
        
        self.codigo = Codigo("Codigo.txt ")
        self.codigo.exec_data(self.codigo.registro["lineaData"])
        self.codigo.exec_text(self.codigo.registro["lineaText"])
        self.actualizarTablas()
        self.resultadoEjecucuion()
        # print(self.codigo.registro)
        # print(self.codigo.ram)
    
    def resultadoEjecucuion(self):
        if self.codigo.registro["lineaError"] is None:
            self.resultado.appendPlainText("Programa finalizado de forma exitosa...")
        else:
            self.resultado.appendPlainText("""%s %s %s"""%(self.codigo.registro["lineaError"],self.codigo.registro["error"],self.codigo.registro["descrError"]))

    def fondoMainWindow(self):
        fondo = QLabel(self)
        fondo.setGeometry(QRect(-30,0,860,580))
        imagen = QPixmap("Imagenes/fondoMain1.png") 
        fondo.setPixmap(imagen)
        fondo.setScaledContents(True)

    def grupoDeComponentes(self):
        self.grupoDeComponentes = QGroupBox(self.centralwidget)
        self.grupoDeComponentes.setGeometry(QRect(0,0,800,580))
        self.plainText(self.grupoDeComponentes)
        self.tablas(self.grupoDeComponentes)
        self.botones(self.grupoDeComponentes)

    
    def plainText(self, espacio):
        self.cuadroDeTexto = QPlainTextEdit(espacio)
        self.cuadroDeTexto.setGeometry(QRect(200,10,400,380))
        self.cuadroDeTexto.setPlainText(""".data
word1:  .word 0x10203040
hword2:  .hword 0x5060
byte3:  .byte 22

.text
mov r0, #220
mov r1, #4
mov r2, #22
mov r3,#6
mov r4,#254
ldr r5, =byte3

        """)
        self.resultado = QPlainTextEdit(espacio)
        self.resultado.setGeometry(QRect(10,440,780,125))
        self.resultado.setReadOnly(True)
        self.resultado.setPlainText("""QtARMSim version 0.4.16
(c) 2014-19 Sergio Barrachina Mir
Developed at the Jaume I University, Castellón, Spain.

Connected to ARMSim (ARMSim version info follows).
V 1.4
(c) 2014 Germán Fabregat
ATC - UJI                                    """)
    def tablas(self, espacio):
        self.tablaRegistros = QTableWidget(espacio)
        self.tablaRegistros.setGeometry(QRect(10,10,145,380))
        self.tablaRegistros.setColumnCount(1)
        self.tablaRegistros.setRowCount(16)   
        nombreFilas=[]
        for x in range(0,16):
            nombreFilas.append("r%s"%x)
            self.tablaRegistros.setItem(x,0,QTableWidgetItem("0x00000000"))
        self.tablaRegistros.setVerticalHeaderLabels(nombreFilas)
        nombreColumna = ["Registros"]
        self.tablaRegistros.setHorizontalHeaderLabels(nombreColumna)
        self.tablaRegistros.setAlternatingRowColors(True)
        self.tablaRegistros.setSelectionMode(QAbstractItemView.SingleSelection)#Seleccionar una celda a la vez

        self.tablaMemoria = QTableWidget(espacio)
        self.tablaMemoria.setGeometry(QRect(635,10,145,380))
        #self.tablaMemoria.verticalHeader().setVisible(False)
        self.tablaMemoria.setColumnCount(1)
        self.tablaMemoria.setRowCount(40)
        fila=0
        nombreFilas=[]
        for key in self.codigo.ram:
            self.tablaMemoria.setItem(fila,0,QTableWidgetItem(self.codigo.ram[key]))
            nombreFilas.append(key)
            fila+=1
        self.tablaMemoria.setVerticalHeaderLabels(nombreFilas)
        self.tablaMemoria.setAlternatingRowColors(True)
        nombreColumna = ["RAM"]
        self.tablaMemoria.setHorizontalHeaderLabels(nombreColumna)
        self.tablaMemoria.setColumnWidth(0,50)
        self.tablaMemoria.setSelectionMode(QAbstractItemView.SingleSelection)#Seleccionar una celda a la vez

    def actualizarTablas(self):
        for x in range(0,16):
            self.tablaRegistros.setItem(x,0,QTableWidgetItem(self.codigo.registro["r%s"%x]))
        fila=0
        for key in self.codigo.ram:
            self.tablaMemoria.setItem(fila,0,QTableWidgetItem(self.codigo.ram[key]))
            fila+=1

    def botones(self, espacio):
        self.ptNuevo = QPushButton(espacio)
        self.ptNuevo.setText("Nuevo")
        self.ptNuevo.setGeometry(QRect(200,400,200,35))
        self.ptNuevo.setIcon(QIcon("Imagenes/signs.png"))

        self.ptEjecutar = QPushButton(espacio)
        self.ptEjecutar.setText("Ejecutar")
        self.ptEjecutar.setGeometry(QRect(405,400,195,35))
        self.ptEjecutar.setIcon(QIcon("Imagenes/computer.png"))

    def separadores(self):
        line=QFrame(self)                          
        line.setGeometry(QRect(165,20,20,350))     
        line.setFrameShape(QFrame.VLine)           
        line.setFrameShadow(QFrame.Raised)         
        #line.setLineWidth(2)                     

        line2=QFrame(self)                          
        line2.setGeometry(QRect(610,20,20,350))     
        line2.setFrameShape(QFrame.VLine)          
        line2.setFrameShadow(QFrame.Raised)         


