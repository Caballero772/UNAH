#^ldrh\s+r\d+\s*,\s*(\[\s*r\d+\s*(,\s*(r\d|\d+))?\s*\]|=\s*(0b[10]+|0x[A-Fa-f\d]+|\d+))$

import re

class Codigo:
    
    def __init__(self,archivo):
        # Registros, tambien se encuentran los valores lineaText, lineaData, error, descrError que se usan para el control del programa
        self.registro = {"lineaText": None, "lineaData": None,"lineaError": None, "error" : None, "descrError" : None,"r0":"0x00000000","r1":"0x00000000","r2":"0x00000000","r3":"0x00000000","r4": "0x00000000","r5":"0x00000000","r6":"0x00000000","r7":"0x00000000","r8":"0x00000000","r9":"0x00000000","r10":"0x00000000","r11":"0x00000000","r12":"0x00000000","r13":"0x00000000","r14":"0x00000000","r15":"0x00000000",} 
        # Diccionario de instrucciones en las que se encuentran los nombres de las instrucciones y estan asociados a las funciones
        self.instrucciones = {"mov":self.mov,"add":self.add,"sub":self.sub,"str":self.strp,"ldr ":self.ldr,".word":self.word,".hword":self.hword,"wfi":self.wfi,".byte":self.byte, "neg":self.neg, "mul":self.mul, "eor":self.eor,"orr":self.orr,"and": self.andd,"ldrb":self.ldrb,"sxtb":self.sxtb,"ldrh":self.ldrh}
        # Diccionario de direccionas RAM asociadas asociadas en un inicio a un valor 0x00000000 en su valor por defecto, que sera definido
        # con la funcion crear_memoria()
        self.etiqueta = {} 
        self.ram = {}
        self.ram = self.crear_memoria(self.ram)
        self.ram["ultima"] = "0x20070000"
        # Lectura de linea por linea del texto en cuestion
        self.codigo = {}
        self.archivo = archivo
        # Funcion que lee el codigo a "ensamblar"   
        self.leer_codigo(self.archivo, self.codigo)

    def getRegistro(self):
        return self.registro
    
    def getInstrucciones(self):
        return self.instrucciones
    
    def getMemoria(self):
        return self.ram
    
    def getCodigo(self):
        return self.codigo

    def getArchivo(self):
        return self.archivo
    
    def getError(self):
        return self.error
    
    def getCodigo(self):
        return self.codigo
    
    def getDescrError(self):
        return self.descrError
    
    def getLineaText(self):
        return self.registro["lineaText"]
    
    def getLineaData(self):
        return self.registro["lineaData"]

    def ca2(self,numero,k):
        vMin=-2**(k-1)
        vMax=2**(k-1)-1
        if numero < 0 and k in [8,16,32] and numero>=vMin and numero<=vMax:
            not_=int("1"*k,2)
            numero='{0:0{1}b}'.format(abs(numero),k)
            ca1=not_-int("%s"%numero,2)
            ca2 = ca1+1
            return '0b{0:0{1}b}'.format(ca2,k)
        elif numero >=0 and numero<=vMax:
            return "0b{0:0{1}b}".format(numero,k)
        elif not(numero>=vMin and numero<=vMax):
            self.registro["error"] = 5
            self.registro["descrError"] = "El valor no puede almacenarse en k = " + str(k)
        elif not(k in [8,16,32]):
            self.registro["error"] = 6
            self.registro["descrError"] = "K no valido"

    def ca2_decimal(self, numero):
        ca2=numero.split("0x")
        binario = bin(int(ca2[1], 16))[2:]
        if ((len(binario)==32) and (binario[0] == "1")):
            normal = ""
            for i in (binario):
                if i == "1": normal += '0'
                else: normal += '1'
            return ((int(str(normal), 2))+1)*-1
        else:
            return int(ca2[1],16)

    def neg(self, line):
        if re.search(r"^neg\s*r\d{1,2}\s*,\s*r\d{1,2}$",line):
            f = lambda x: x if int(x) < 8 else None
            lista = list(filter(None,list(map(f,re.findall(r"\d{1,2}",line)))))
            print(lista)
            if len(lista) == 2:
                lista[1] = -self.ca2_decimal(self.registro["r" + str(lista[1])])
                lista[1] = hex(int(self.ca2(lista[1],32),2))
                lista[1] = "0x" + (10 - len(lista[1])) * "0" + lista[1][2:].upper()
                self.registro["r" +  lista[0]] = lista[1]
                del(lista)
            else:
                self.registro["error"] = 12
                self.registro["descrError"] = "El valor del registro no es valido"
                self.registro["lineaError"] = self.obtener_llave(line,self.codigo)
        else:
            self.registro["error"] = 4 
            self.registro["descrError"] = "Error de sintaxis"
            self.registro["lineaError"] = self.obtener_llave(line,self.codigo)

    def andd(self, line):
        if re.search(r"^and\s*r[0-7],\s*r[0-7]\s*$", line) != None:
            rd=re.search(r"r[0-7]", line).group()
            rs=re.search(r",\s*r[0-7]", line).group().split()
            valrd=int(str(self.registro[rd]), 16)
            valrs=int(str(self.registro[rs[1]]), 16)
            self.registro[rd]='0x{0:0{1}X}'.format(int(valrd & valrs),8)
        elif re.search(r"(^and\s*r([8-9]|1[0-5]),\s*r[0-7]\s*$)|(^and\s*r[0-7],\s*r([8-9]|1[0-5])\s*$)", line) != None:
            self.registro["error"] = 10 
            self.registro["descrError"] = "No se puede acceder a esos registro"
            self.registro["lineaError"] = self.obtener_llave(line,self.codigo)
        else:
            self.registro["error"] = 4 
            self.registro["descrError"] = "Error de sintaxis"
            self.registro["lineaError"] = self.obtener_llave(line,self.codigo)

    def orr(self, line):
        if re.search(r"^orr\s*r[0-7],\s*r[0-7]\s*$", line) != None:
            rd=re.search(r"r[0-7]", line).group()
            rs=re.search(r",\s*r[0-7]", line).group().split()
            valrd=int(str(self.registro[rd]), 16)
            valrs=int(str(self.registro[rs[1]]), 16)
            self.registro[rd]='0x{0:0{1}X}'.format(int(valrd | valrs),8)
        elif re.search(r"(^orr\s*r([8-9]|1[0-5]),\s*r[0-7]\s*$)|(^orr\s*r[0-7],\s*r([8-9]|1[0-5])\s*$)", line) != None:
            self.registro["error"] = 10 
            self.registro["descrError"] = "No se puede acceder a esos registro"
            self.registro["lineaError"] = self.obtener_llave(line,self.codigo)
        else:
            self.registro["error"] = 4 
            self.registro["descrError"] = "Error de sintaxis"
            self.registro["lineaError"] = self.obtener_llave(line,self.codigo)

    def mov(self,line):
        #evalúa la sintaxis de la función mov con un registro y una constante
        lineaConstDec=re.search(r"^mov\s*r([0-9]|1[0-5]),\s*#(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-5]{2}))\s*$", line)
        lineaConstBin=re.search(r"^mov\s*r([0-9]|1[0-5]),\s*#0b([0-1]{1,8})\s*$", line)
        lineaConstHex=re.search(r"^mov\s*r([0-9]|1[0-5]),\s*#(0X|0x)([A-F0-9]{1,2}|[a-f0-9]{1,2})\s*$", line)
        #evalúa la sintaxis de la función mov con dos registros
        lineaRegis=re.search(r"^mov\s*r([0-9]|1[0-5]),\s*r([0-9]|1[0-5])\s*", line)
        if re.search(r"r([0-7])", line) != None: 
            registro=re.search(r"r[0-7]", line).group() #para extraer el registro usado en la función
            if lineaConstDec != None: 
                constante=re.search(r"#([0-9]{1,3})", line).group().split("#") #para extraer la constante
                self.registro[registro]='0x{0:0{1}X}'.format(int(constante[1]),8)
            elif lineaConstBin != None:
                constante=re.search(r"#0b([0-1]{1,8})", line).group().split("0b")
                self.registro[registro]='0x{0:0{1}X}'.format(int(str(constante[1]),2),8) 
            elif lineaConstHex != None:
                constante=re.search(r"#(0X|0x)([A-F0-9]{1,2}|[a-f0-9]{1,2})", line).group().split("0x") or re.search(r"#(0X|0x)([A-F0-9]{1,2}|[a-f0-9]{1,2})",line).group().split("0X")
                self.registro[registro]='0x{0:0{1}X}'.format(int(str(constante[1]),16),8)
            elif lineaRegis != None: 
                if re.search(r",\s*r[0-7]$", line) != None:
                    registro2=re.search(r",\s*r[0-7]", line).group().split() #para extraer el segundo registro usado en la función
                    self.registro[registro2[1]]=self.registro[registro]
                else: 
                    self.registro["error"] = 10 
                    self.registro["descrError"] = "No se puede acceder a esos registro"
                    self.registro["lineaError"] = self.obtener_llave(line,self.codigo)
            else:
                self.registro["error"] = 4
                self.registro["descrError"] = "Error de sintaxis"
                self.registro["lineaError"] = self.obtener_llave(line,self.codigo)
        else:
            self.registro["error"] = 10 
            self.registro["descrError"] = "No se puede acceder a esos registro"
            self.registro["lineaError"] = self.obtener_llave(line,self.codigo)

    def ldrb(self,line):
        if re.search(r"^ldrb\s*r(\d|1[0-5])\s*,\s*=((0x|0X)[A-Fa-f\d]{2}|0b[01]{1,8}|([0-9]{1,2}|1[0-9]{2}|2[0-5]{5})|\-\d{1,3}|\w+)\s*$", line) != None:
            if re.search(r"r[0-7]", line) != None:
                registro=re.search(r"r[0-7]", line).group()
                if re.search(r"=(0x|0X)[A-Fa-f\d]{1,2}", line) != None:
                    constante=re.search(r"=(0x|0X)[A-Fa-f\d]{1,2}",line).group().lower().split("0x")
                    self.registro[registro]='0x{0:0{1}X}'.format(int(str(constante[1]),16),8)
                elif re.search(r"=0b[01]{1,8}", line) != None:
                    constante=re.search(r"=0b[01]{1,8}", line).group().split("0b")
                    self.registro[registro]='0x{0:0{1}X}'.format(int(str(constante[1]),2),8)
                elif re.search(r"=\d{1,3}", line) != None:
                    constante=re.search(r"=\d{1,3}", line).group().split("=")
                    self.registro[registro]='0x{0:0{1}X}'.format(int(constante[1]),8)
                elif re.search(r"=\-\d{1,3}", line) !=None:
                    constante=re.search(r"=\-\d{1,3}", line).group().split("=")
                    if -129 < int(constante[1]) < 0:
                        value=self.ca2(int(constante[1]),8)
                        value=value.split("0b")
                        self.registro[registro]='0x{0:0{1}X}'.format(int(str(value[1]),2),8)
                    else:
                        self.registro["error"] = 5
                        self.registro["descrError"] = "Codigo Error = 5: El valor no puede almacenarse en k = 8"
                        self.registro["lineaError"] = self.obtener_llave(line,self.codigo)
                else:
                    etiqueta=re.search(r"=\w+", line).group().split("=")
                    direccion = self.etiqueta[etiqueta[1]].split("10x")
                    self.registro[registro]='0x{}'.format(direccion[1])
            elif re.search(r"r([8-9]|1[0-5])",line) !=None:
                self.registro["error"] = 10
                self.registro["descrError"] = "No se puede acceder a esos registro"
                self.registro["lineaError"] = self.obtener_llave(line,self.codigo)
        elif re.search(r"^ldrb\s*r([0-9]|1[0-5])\s*,\s*\[\s*(r(\d|1[0-5])|r(\d|1[0-5])\s*,\s*((r(\d|1[0-5]))|#((\d{1,2})|0x[A-Fa-f\d]{1,2}|0b[01]{1,8})))\s*\]\s*$", line) != None:
            if re.search(r"ldrb\s*r[0-7]\s*,",line) !=None:
                registro=re.search(r"r[0-7]", line).group()
                if re.search(r"(,\s*\[\s*r([0-7])\s*\])|(,\s*\[\s*(r([0-7])\s*,\s*#(0|0x[0]{1,2}|0b[0]{1,8}))\s*\])", line) != None:
                    registro2=re.search(r",\s*\[\s*r([0-7])\s*", line).group().split("[")
                    registro2=registro2[1].split()
                    value=self.ram[self.registro[registro2[0][-2:]]].split("x")
                    self.registro[registro]='0x000000{}'.format(value[1])
                elif re.search(r",\s*\[\s*r([0-7])\s*,\s*#((\d{1,2})|0x[A-Fa-f\d]{1,2}|0b[01]{1,8})\s*\]", line) != None:
                    registro2=re.search(r",\s*\[\s*r([0-7])", line).group().split("[")
                    registro2=registro2[1].split()
                    if re.search(r"#(\d{1,2})\s*\]$", line) != None:
                        constante=re.search(r"#(\d{1,2})\s*\]$", line).group().split("#")
                        constante=constante[1].split("]")
                        if 0<int(constante[0])<32:
                            if int(self.registro[registro2[0]][-2:])+int(constante[0]) > 41:
                                self.registro[registro]='0x00000000'
                            else:
                                memoria=hex(int(self.registro[registro2[0]][-2:])+int(constante[0])).split("0x")
                                value=self.ram['0x2007{0:0{1}X}'.format(int(memoria[1]),4)].split("0x")
                                self.registro[registro]='0x000000{}'.format(value[1])
                        else:
                            self.registro["error"] = 13
                            self.registro["descrError"] = "El valor del offset no es valido"
                            self.registro["lineaError"] = self.obtener_llave(line,self.codigo)

                    elif re.search(r"#0b[01]{1,8}\s*\]$", line) != None:
                        constante=re.search(r"#0b[01]{1,8}\s*\]$", line).group().split("0b")
                        constante=constante[1].split("]")
                        if 0<int(str(constante[0]),2)<32:
                            if int(self.registro[registro2[0]][-2:])+int(str(constante[0]),2) > 41:
                                self.registro[registro]='0x00000000'
                            else:
                                memoria=hex(int(self.registro[registro2[0]][-2:])+int(str(constante[0]),2)).split("0x")
                                value=self.ram['0x2007{0:0{1}X}'.format(int(str(memoria[1]),16),4)].split("0x")
                                self.registro[registro]='0x000000{}'.format(value[1])
                        else:
                            self.registro["error"] = 13
                            self.registro["descrError"] = "El valor del offset no es valido"
                            self.registro["lineaError"] = self.obtener_llave(line,self.codigo)

                    elif re.search(r"#(0x|0X)[A-Fa-f\d]{1,2}", line) != None:
                        constante=re.search(r"#0x[A-Fa-f\d]{1,2}", line).group().lower().split("0x")
                        if 0<int(str(constante[1]),16)<32:
                            if int(self.registro[registro2[0]][-2:])+int(str(constante[1]),16) > 41:
                                self.registro[registro]='0x00000000'
                            else:
                                memoria=hex(int(self.registro[registro2[0]][-2:])+int(str(constante[1]),16)).split("0x")
                                value=self.ram['0x2007{0:0{1}X}'.format(int(str(memoria[1]),16),4)].split("0x")
                                self.registro[registro]='0x000000{}'.format(value[1])
                        else:
                            self.registro["error"] = 13
                            self.registro["descrError"] = "El valor del offset no es valido"
                            self.registro["lineaError"] = self.obtener_llave(line,self.codigo)

                elif re.search(r",\s*\[\s*r([0-7])\s*,\s*r([0-7])\s*\]$", line) != None:
                    registro2=re.search(r",\s*\[\s*r([0-7])", line).group().split("[")
                    registro2=registro2[1].split()
                    if re.search(r",\s*r([0-7])\s*\]", line) != None:
                        registro3=re.search(r",\s*r([0-7])\s*\]", line).group().split("]")
                        registro3=registro3[0].split()
                        if 0<=int(self.registro[registro3[1]],16)<42:
                            memoria=hex(int(self.registro[registro2[0]][-2:])+int(self.registro[registro3[1]],16)).split("0x")
                            value=self.ram['0x2007{0:0{1}X}'.format(int(memoria[1]),4)].split("0x")
                            self.registro[registro]='0x000000{}'.format(value[1])
                        elif hex(int(self.registro[registro2[0]][-2:])+int(self.registro[registro3[1]],16)) > "0x29":
                            self.registro[registro]='0x00000000'
                        else:
                            self.registro["error"] = 13
                            self.registro["descrError"] = "El valor del offset no es valido"
                            self.registro["lineaError"] = self.obtener_llave(line,self.codigo)             
                else: 
                    self.registro["error"] = 10
                    self.registro["descrError"] = "No se puede acceder a esos registro"
                    self.registro["lineaError"] = self.obtener_llave(line,self.codigo)
            else:
                self.registro["error"] = 10
                self.registro["descrError"] = "No se puede acceder a esos registro"
                self.registro["lineaError"] = self.obtener_llave(line,self.codigo)
        else:
            self.registro["error"] = 4
            self.registro["descrError"] = "Error de sintaxis"
            self.registro["lineaError"] = self.obtener_llave(line,self.codigo)
        
    def sxtb(self, line):
        if re.search(r"^sxtb\s*r(\d|1[0-5])\s*,\s*r(\d|1[0-5])\s*$", line) != None:
            if re.search(r"r([0-7]),", line) != None:
                registro=re.search(r"r([0-7])", line).group()
                if re.search(r",\s*r([0-7])", line) != None:
                    registro2=re.search(r",\s*r([0-7])", line).group().split()
                    binario = bin(int(self.registro[registro2[1]], 16))[2:]
                    if ((len(binario)==8) and (binario[0] == "1")):
                        self.registro[registro]='0xFFFFFF{}'.format(self.registro[registro2[1]][-2:])
                    else:
                        self.registro[registro]=self.registro[registro2[1]]
                else:
                    self.registro["error"] = 10
                    self.registro["descrError"] = "No se puede acceder a esos registro"
                    self.registro["lineaError"] = self.obtener_llave(line,self.codigo)
            else: 
                self.registro["error"] = 10
                self.registro["descrError"] = "No se puede acceder a esos registro"
                self.registro["lineaError"] = self.obtener_llave(line,self.codigo)
        else:
            self.registro["error"] = 4
            self.registro["descrError"] = "Error de sintaxis"
            self.registro["lineaError"] = self.obtener_llave(line,self.codigo)

    def eor(self,line):

        
        if re.search(r"^eor\s+r\d+\s*,\s*r\d+$",line) != None:
            lista = re.findall("\d+",line)
            f = lambda x: x if int(x) < 8 else None
            lista = list(filter(None,list(map(f,lista))))
            if len(lista) == 2:
                rd = int(self.registro["r" + str(lista[0])],16)
                rs = int(self.registro["r" + str(lista[1])],16)
                rd = hex(int(bin(rd ^ rs),2))
                self.registro["r" + str(lista[0])] = "0x" + (10 - len(rd))*"0" + rd[2:].upper()
                del(rd)
                del(rs)
                del(lista)
            else:
                self.registro["error"] = 10
                self.registro[""] = "No se puede acceder a esos registro"                 
                self.registro["lineaError"] = self.obtener_llave(line,self.codigo) 
        else:
            self.registro["error"] = 4
            self.registro["descrError"] = "Error de sintaxis"
            self.registro["lineaError"] = self.obtener_llave(line,self.codigo)

    def add(self,line):
        reg = re.findall(r"r[0-9]\s*|r[0-9]|#[0-9]*",line)
        rd = reg[0]     #registro destino
        rs = reg[1]     #rs 
        
        try:
            rn = reg[2]         #rn (puede ser que sea un registro o un valor inmediato)
        except IndexError:
            rn = None

        if rn is not None:                          #verifica si el tercer dato esta presente
            reg = re.search(r"r[0-9]",rn)           #almacena un registro
            d_inm = re.search(r"[0-9]",rn)          #almacena un dato inmediato
            
        if reg is not None:            #entra si es un registro

                val_rd = int(self.registro[rd],16)      #valor del registro destino(int)
                val_rs = int(self.registro[rs],16)      #valor del rs(int)
                val_rn = int(self.registro[rn],16)      #valor del rn(int)

                val_rd = val_rs + val_rn           #valor de la sumatoria (int)

                val_rd_hex = hex(val_rd)            #valor de la sumatoria en hexadeximal
                val_rd_clean = re.search(r"(?!0x|x)([\w]+)",val_rd_hex).group() #eliminando el "0x" generado por python
                sum_fin = "0x" + (10 - len(val_rd_hex)) * "0" + val_rd_clean    #añadiendo el 0x000000
                self.registro[rd] = sum_fin     #asignando el valor al registro

                print(self.registro[rd])

        elif d_inm is not None:     #si es un dato inmediato

            if int(d_inm.group()) <=7:   #verifica si el valor esta dentro del rango(0-7)   
                
                val_rd = int(self.registro[rd],16)      #valor del registro destino (int)
                val_rs = int(self.registro[rs],16)      #valor del registro rs  (int)
                d_inm_int = int(d_inm.group())          #valor del dato inmediato   (int)
                
                val_rd = val_rs +d_inm_int              #valor de la suma (int)

                val_rd_hex = hex(val_rd)                #valor de la suma en hex
                val_rd_clean = re.search(r"(?!0x|x)([\w]+)",val_rd_hex).group() #eliminando el "0x" generado por python
                sum_fin = "0x" + (10 - len(val_rd_hex)) * "0" + val_rd_clean    #añadiendo el 0x000000
                self.registro[rd] = sum_fin #asignando el valor al registro

                print(self.registro[rd])
            else:
                self.registro["error"] = 5
                self.registro["descrError"] = "El valor excede el limite de bits(3)"                 
                self.registro["lineaError"] = self.obtener_llave(line,self.codigo)

        elif rs is not None:                            #solo tiene rd y #inm8
            d_inm = re.search(r"[0-9]",rs)
            if int(d_inm.group()) <=255:
                val_rd = int(self.registro[rd],16)   #valor del registro rd(int)
                d_inm_int = int(d_inm.group())             #valor del dato inmediato(int)

                val_rd = val_rd + d_inm_int

                val_rd_hex = hex(val_rd)
                val_rd_clean = re.search(r"(?!0x|x)([\w]+)",val_rd_hex).group()
                sum_fin = "0x" + (10 - len(val_rd_hex)) * "0" + val_rd_clean
                self.registro[rd] = sum_fin
            else:
                self.registro["error"] = 5
                self.registro["descrError"] = "El valor exede el limite de bits(8)"                 
                self.registro["lineaError"] = self.obtener_llave(line,self.codigo)

        #print("add")

    def sub(self,line):
        return "Aqui va su codigo :')"

    def ldrh(self, line):
        if re.search(r"^ldrh\s+r\d+\s*,\s*(\[\s*r\d+\s*(,\s*(r\d|\d+))?\s*\]|=\s*-?(0b[10]+|0x[A-Fa-f\d]+|\d+))$",line):
            diccionario = {re.search(r"=\s*-?(0x[A-Fa-f\d]+|0b[01]+|\d+)",line):self.ldrhValores,re.search(r"\[\s*r\d+\s*(,(\s*r\d+|\s*\d+))?\s*\]",line):self.ldrhRegistros}
            del diccionario[None]
            diccionario[list(diccionario.keys())[0]](line)
            del(diccionario)
        else:
            self.registro["error"] = 4
            self.registro["descrError"] = "Error de sintaxis"
            self.registro["lineaError"] = self.obtener_llave(line,self.codigo)

    def ldrhRegistros(self,line):
        print(line)

    def ldrhValores(self,line):
        valor = {re.search(r"-?0x[A-Fa-f\d]+",line):16,re.search(r"-?0b[01]+",line):2}
        del valor[None]
        valor = int(list(valor.keys())[0].group(),valor[list(valor.keys())[0]]) if len(valor) == 1 else int(re.search(r"=-?\d+",line).group()[1:])
        if valor > -2**15 and valor < 2**15-1:
            rd = re.search(r"r[0-7]",line)
            if rd != None:
                pass
                #Revisar el almacenamiento de los valores
                #rd = rd.group()
                #valor = hex(int(self.ca2(valor, 16),2))
                #self.registro[rd] = "0x" + (10 - len(valor))*"0" + valor[2:].upper()
            else:
                self.registro["error"] = 10
                self.registro["descrError"]  = "No se puede acceder a esos registro"
                self.registro["lineaError"] = self.obtener_llave(line,self.codigo)
                del(rd)
                del(valor)
        else:
            self.registro["error"] = 5
            self.registro["descrError"] = "El valor no se puede almacenear en k = 16"
            self.registro["lineaError"] = self.obtener_llave(line,self.codigo)
            del(valor)
            
    def ldr(self,line):
        if re.search(r"^ldr\s+r\d{1,2}\s*,\s*(\[r\d{1,2}\]|=\s*(-?0x[A-Fa-f\d]+|-?0b[10]+|-?\d+|\w+))$",line) != None:
            rd = re.search(r"\[r[0-9]{1,2}\]$",line)                          #registro
            val = re.search(r"=\s*-?(0x[A-Fa-f\d]+|0b[01]+|\d+)$",line)                 #numero(hex,dec,bin)
            tag = re.search(r"=\s*\w+$",line)                    

            if rd is not None:
                rds = re.search(r"r[0-9]{1,2}",line).group()                  #Registro destino(string)
                rbs = re.search(r"\[r[0-9]{1,2}\]",line).group()              #Registro base(string)
                rbn = re.search(r"r[0-9]{1,2}",rbs).group()                     #Registro base(string, sin corchetes)
                val1 = int(re.search(r"[0-9]{1,2}",rds).group())                #valor del registro destino(int)
                val2 = int(re.search(r"[0-9]{1,2}",rbs).group())                #valor del registro base(int)
                if val1 > 7 and val2 > 7:
                    self.registro["error"] = 10
                    self.registro["descrError"] = "No se puede acceder a esos registro"
                    self.registro["lineaError"] = self.obtener_llave(line,self.codigo)         
                else: 
                    itemrb = self.registro[rbn]                                      #valor dentro del registro rb(deberia ser una dir de mem)
                    valhex = re.search(r"0x2007",itemrb).group()                # int de la dir de mem
                    if valhex != '0x2007':                                      #verifica si es una dir de memoria(error)
                        pass  
                    else:                                                       #guarde el contenido de la dir de mem contenida en rb al rd
                        
                        dic_reg = self.etiqueta.values()                              #extrae los values de el dic etiqueta
                        str_dic = str(dic_reg)                                   #convierte el dic etiqueta en string
                        val_item = re.search(r"\d"+itemrb,str_dic).group()       #extrae el valor deseado de el dic etiqueta
                        num_vals = re.search(r"^[0-9]",val_item).group()         #extrae el # de pos a evaluar 
                        num_val = int(num_vals)                                  #el num de string a int
                        dic_ram_keys = list(self.ram.keys())                                #lista de los keys de el dic ram
                        dic_ram_values = list(self.ram.values())                            #lista de los valores de el dic ram
                        dist_ram = len(dic_ram_keys)                                   # tamaño de el dic ram
                        ram_key_val = " "                                              # posicion de la mem ram donde se aloca el val inicial
                        store_val_rev = " "                                            # valor a almacenar en el registro destino(siendo lista y al reves)
                        for i in range (0,dist_ram):                                   #ciclo para buscar la posicion donde se encuentra alocado el key
                            if itemrb == dic_ram_keys[i]:
                                ram_key_val = i
                        for f in range(0,num_val):                                       #itera y une los valores de las dir de mem
                            store_val_rev = store_val_rev + dic_ram_values[ram_key_val+f]
                        lista_store_val = re.findall(r"(?!0x|x)([\w]{2})",store_val_rev)            #filtra los numeros (excluye el 0x)
                        lista_store_val.reverse()                                          # reversa la lista del valor a almacenar (al ser little endian)
                        store_val = "0x"+"".join(lista_store_val)                          #valor reversado y convertido en string                             
                        self.registro[rds] = store_val
            elif val is not None:
                if re.search(r"-?0x[A-Fa-f\d]+$",line) is not None:
                
                    if int(re.search(r"-?0x[A-Fa-f\d]+$",line).group(),16) <= 2**31-1 and int(re.search(r"-?0x[A-Fa-f\d]+$",line).group(),16) >= -2**31:
                        
                        rds = re.search(r"r[0-9]{1,2}",line).group()
                        vals = re.search(r"-?0x[A-Fa-f\d]+",line).group()
                        vals = hex(int(self.ca2(int(vals,16),32),2))
                        self.registro[rds] = "0x" + (10 - len(vals)) * "0" + vals[2:].upper()

                    else:
                        self.registro["error"] = 5
                        self.registro["descrError"] = "El valor no puede almacenarse en k = 32"                 
                        self.registro["lineaError"] = self.obtener_llave(line,self.codigo)

                elif re.search(r"-?0b[01]+$",line) is not None:
                    
                    if int(re.search(r"-?0b[01]+$",line).group(),2) <= 2**31-1 and int(re.search(r"-?0b[01]+$",line).group(),2) >= -2**31:
                        
                        rds = re.search(r"r[0-9]{1,2}",line).group()
                        valbs = re.search(r"-?0b[01]+$",line).group()
                        valb_hex = hex(int(self.ca2(int(valbs,2),32),2))
                        self.registro[rds] = "0x" + (10 - len(valb_hex)) * "0" + valb_hex[2:].upper()
                    
                    else:
                        self.registro["error"] = 5
                        self.registro["descrError"] = "El valor no puede almacenarse en k = 32"
                        self.registro["lineaError"] = self.obtener_llave(line,self.codigo)
                
                elif re.search(r"[0-9]+$",line) is not None:
                    if int(re.search(r"-?\d+$",line).group()) <= 2**31-1 and int(re.search(r"-?\d+$",line).group()) >= -2**31:
                        rds = re.search(r"r[0-9]{1,2}",line).group()                  
                        valds = re.search(r"-?[0-9]+$",line).group()
                        vald_hex = hex(int(self.ca2(int(valds),32),2))
                        self.registro[rds] = "0x" + (10 - len(vald_hex)) * "0" + vald_hex[2:].upper()
                    else:
                        self.registro["error"] = 5
                        self.registro["descrError"] = "El valor no puede almacenarse en k = 32"
                        self.registro["lineaError"] = self.obtener_llave(line,self.codigo)
            elif tag is not None:

                rds = re.search(r"r[0-9]{1,2}",line).group()                  
                tag = re.search(r"\w+$",line).group()                         
                
                if tag in list(self.etiqueta.keys()):
                    val_tag = self.etiqueta[tag]                                         
                    dir_tag = re.search(r"0x2007[0-9]+",val_tag).group()              
                    self.registro[rds] = dir_tag
                else:
                    self.registro["error"] = 11
                    self.registro["descrError"] = "La etiqueta no existe"
                    self.registro["lineaError"] = self.obtener_llave(line,self.codigo)                    
        else:
            self.registro["error"] = 4
            self.registro["descrError"] = "Error de sintaxis"
            self.registro["lineaError"] = self.obtener_llave(line,self.codigo)
        
    def strp(self,line):
        if re.search("^str\s+r[0-9]{1,2}\s*,\s*\[\s*r\d{1,2}(\s*,\s*r\d{1,2}|\s*,\s*#\d{1,2})?\s*\]$",line) != None:

            registros = re.findall("r\d{1,2}|#\d{1,2}",line)

            if len(registros) == 2:

                if int(registros[0][1:]) >-1 and int(registros[0][1:]) < 8 and int(registros[1][1:]) >-1 and int(registros[1][1:]) < 8:
       	 		
                    valorregistro = self.registro[registros[0]]
                    direccionRam = self.registro[registros[1]]

                    self.ram[direccionRam]= "0x" + valorregistro[8:].upper()
                    self.ram["0x" + hex(int(direccionRam,16) + 1)[2:].upper()] = "0x" + valorregistro[6:8].upper()
                    self.ram["0x" + hex(int(direccionRam,16) + 2)[2:].upper()] = "0x" + valorregistro[4:6].upper()
                    self.ram["0x" + hex(int(direccionRam,16) + 3)[2:].upper()] = "0x" + valorregistro[2:4].upper()

                else:
                    
                    self.registro["error"] = 12
                    self.registro["descrError"] = "El valor del registro no es valido"
                    self.registro["lineaError"] = self.obtener_llave(line,self.codigo)
          	 
            elif len(registros)==3 and registros[2][:1] == "#":

                if int(registros[0][1:]) >-1 and int(registros[0][1:]) < 8 and int(registros[1][1:])>-1 and int(registros[1][1:]) <8:
          		
                    if int(registros[2][1:])%4==0 and int(registros[2][1:]) < 37:
            		
                        valorregistro=self.registro[registros[0]]
                        direccionRam= self.registro[registros[1]]
                        valorOffset= int(registros[2][1:])
            		
                        self.ram["0x" + hex(int(direccionRam,16) + valorOffset)[2:].upper()] = "0x" + valorregistro[8:].upper()
                        self.ram["0x" + hex(int(direccionRam,16) + (1 + valorOffset))[2:].upper()] = "0x" + valorregistro[6:8].upper()
                        self.ram["0x" + hex(int(direccionRam,16) + (2 + valorOffset))[2:].upper()] = "0x" + valorregistro[4:6].upper()
                        self.ram["0x" + hex(int(direccionRam,16) + (3 + valorOffset))[2:].upper()] = "0x" + valorregistro[2:4].upper()

                    else:
                    
                        self.registro["error"] = 13
                        self.registro["descrError"] = "El valor del offset no es valido"
                        self.registro["lineaError"] = self.obtener_llave(line,self.codigo)


                else: 
          		
                    self.registro["error"] = 12
                    self.registro["descrError"] = "El valor del registro no es valido"
                    self.registro["lineaError"] = self.obtener_llave(line,self.codigo)
        
            elif len(registros)==3 and registros[2][:1] == "r":
            
                if int(registros[0][1:]) >-1 and int(registros[0][1:]) < 8 and int(registros[1][1:])>-1 and int(registros[1][1:]) <8 and int(registros[2][1:])>-1 and int(registros[2][1:])<8:
                
                    valorregistro1= int(self.registro[registros[2]],16)

                    if valorregistro1%4==0 and valorregistro1<37:
                        # Alexander was here
                        valorregistro=self.registro[registros[0]]
                        direccionRam= self.registro[registros[1]]
            
                        self.ram["0x" + hex(int(direccionRam,16) + valorregistro1)[2:].upper()] = "0x" + valorregistro[8:].upper()
                        self.ram["0x" + hex(int(direccionRam,16) + (1 + valorregistro1))[2:].upper()] = "0x" + valorregistro[6:8].upper()
                        self.ram["0x" + hex(int(direccionRam,16) + (2 + valorregistro1))[2:].upper()] = "0x" + valorregistro[4:6].upper()
                        self.ram["0x" + hex(int(direccionRam,16) + (3 + valorregistro1))[2:].upper()] = "0x" + valorregistro[2:4].upper()

                    else:

                        self.registro["error"] = 14
                        self.registro["descrError"] = "El valor contenido en el tercer registro no es valido"
                        self.registro["lineaError"] = self.obtener_llave(line,self.codigo)
            
                else:

                    self.registro["error"] = 12
                    self.registro["descrError"] = "El valor del registro no es valido"
                    self.registro["lineaError"] = self.obtener_llave(line,self.codigo)

        else:

            self.registro["error"] = 4
            self.registro["descrError"] = "Error de sintaxis"
            self.registro["lineaError"] = self.obtener_llave(line,self.codigo)

    def mul(self,line):
        if re.search("^mul\s+r\d{1,2}\s*,\s*(r\d{1,2}\s*|r\d{1,2}\s*,\s*r\d{1,2}\s*)?$", line) != None:
       
            registros = re.findall("r\d{1,2}",line)
            if len(registros)==2:

                if int(registros[0][1:]) >-1 and int(registros[0][1:]) < 8 and int(registros[1][1:]) >-1 and int(registros[1][1:]) < 8:

                    valorRegisDestino= codigo.ca2_decimal(self.registro[registros[0]])  
                    valorRegisFuente= codigo.ca2_decimal(self.registro[registros[1]])
                    valorMultiplicacion= valorRegisFuente*valorRegisDestino
                    valorMultiplicacion= int(codigo.ca2(valorMultiplicacion,32),2)

                    self.registro[registros[0]]= '0x{0:0{1}X}'.format(valorMultiplicacion,8)

                else:
                    self.registro["error"] = 12
                    self.registro["descrError"] = "El valor del registro no es valido"
                    self.registro["lineaError"] = self.obtener_llave(line,self.codigo)

            if len(registros)==3:

                if int(registros[0][1:]) >-1 and int(registros[0][1:]) < 8 and int(registros[1][1:]) >-1 and int(registros[1][1:]) < 8 and int(registros[2][1:])> -1 and int(registros[2][1:])< 8:

                    if registros[0] == registros[1]:
                    
                        valorRegisDestino= codigo.ca2_decimal(self.registro[registros[1]])  
                        valorRegisFuente= codigo.ca2_decimal(self.registro[registros[2]])
                        valorMultiplicacion= valorRegisFuente*valorRegisDestino
                        valorMultiplicacion= int(codigo.ca2(valorMultiplicacion,32),2)

                        self.registro[registros[0]]= '0x{0:0{1}X}'.format(valorMultiplicacion,8)

                    elif registros[0] == registros[2]:

                        valorRegisDestino= codigo.ca2_decimal(self.registro[registros[1]])  
                        valorRegisFuente= codigo.ca2_decimal(self.registro[registros[2]])
                        valorMultiplicacion= valorRegisFuente*valorRegisDestino
                        valorMultiplicacion= int(codigo.ca2(valorMultiplicacion,32),2)

                        self.registro[registros[0]]= '0x{0:0{1}X}'.format(valorMultiplicacion,8)

                    else: 
                        self.registro["error"] = 15
                        self.registro["descrError"] = "Debe introducir dos registros iguales"
                        self.registro["lineaError"] = self.obtener_llave(line,self.codigo)

                else:
                    self.registro["error"] = 12
                    self.registro["descrError"] = "El valor del registro no es valido"
                    self.registro["lineaError"] = self.obtener_llave(line,self.codigo)

        else:
            self.registro["error"] = 4
            self.registro["descrError"] = "Error de sintaxis"
            self.registro["lineaError"] = self.obtener_llave(line,self.codigo)

    def obtener_direccion(self,valor = None):
        return hex(537329664 + list(self.ram.values()).index("0x00")) if valor == None else hex(537329664 + list(self.ram.values()).index(valor))

    def word(self,line):
        if re.search(r"^([A-z]{1}[\w_]*:)?\s*\.word\s+-?(0x[0-9A-Fa-z]+|0b[0-1]+|\d+)$",line) != None:
            
            if int(self.ram["ultima"],16) <= 537329700:
                
                valor = {re.search(r"-?0x[0-9A-F]+$",line):16, re.search(r"-?0b[01]+$",line):2}
                valor.pop(None)
                valor = int(list(valor.keys())[0].group(),valor[list(valor.keys())[0]]) if len(valor) == 1 else int(re.search(r"-?\d+$",line).group())

                if valor >= -2**31 and valor <= 2**31:

                    valor = hex(int(self.ca2(valor,32),2))
                    valor = "0x" + (10 - len(valor)) * "0" + valor[2:]
                    direccion = self.ram["ultima"]
                    self.ram["ultima"] = hex(int(direccion,16) + 3)
                    self.ram[direccion] = "0x" + str(valor[8:]).upper()
                    self.ram["0x" + hex(int(direccion,16) + 1)[2:].upper()] = "0x" + str(valor[6:8]).upper()
                    self.ram["0x" + hex(int(direccion,16) + 2)[2:].upper()] = "0x" + str(valor[4:6]).upper()
                    self.ram["0x" + hex(int(direccion,16) + 3)[2:].upper()] = "0x" + str(valor[2:4]).upper()
                    self.ram["ultima"] = "0x" + hex(int(direccion,16) + 4)[2:].upper()

                    if re.search(r"^([A-z]{1}[\w_]*:)",line) != None:
                        self.guardar_etiqueta(re.search(r"^([A-z]{1}[\w_]*)",line).group(),direccion,4,line)

                    del(direccion)
                    del(valor)

                else:
                    self.registro["error"] = 5 
                    self.registro["descrError"] = "El valor no puede almacenarse en k"
                    self.registro["lineaError"] = self.obtener_llave(line,self.codigo)                
            else:
                self.registro["error"] = 7
                self.registro["descrError"] = "No hay suficiente memoria para reservar una palabra"
                self.registro["lineaError"] = self.obtener_llave(line,self.codigo)                 
        else:
            self.registro["error"] = 4
            self.registro["descrError"] = "Error de sintaxis"
            self.registro["lineaError"] = self.obtener_llave(line,self.codigo)

    def byte(self,line):
        
        if re.search(r"^([A-z]{1}\w*:)?\s*\.byte\s+-?(0x[A-Fa-f0-9]+|0b[01]+|\d+)$",line) != None:
            if int(self.ram["ultima"],16) < 537329704:
                
                valor = {re.search(r"0x[A-Fa-f0-9]+$",line):16,re.search(r"0b[01]+$",line):2}
                valor.pop(None)
                valor = int(list(valor.keys())[0].group(),valor[list(valor.keys())[0]]) if len(valor) == 1 else int(re.search(r"-?\d+$",line).group())
                
                if valor >= -128 and valor <= 127:
                    
                    valor = hex(int(self.ca2(valor,8),2))
                    valor = "0x" + (2 - len(valor)) * "0" + valor[2:]
                    self.ram[self.ram["ultima"]] = "0x" + str(valor[2:]).upper()
                    
                    if re.search(r"^([A-z]{1}\w*:)",line) != None:
                        self.guardar_etiqueta(re.search(r"^([A-z]{1}\w*)",line).group(),self.ram["ultima"],1,line)
                    
                    del(valor)
                    self.ram["ultima"] = "0x" + hex(int(self.ram["ultima"],16) + 1)[2:].upper()

                else:
                    self.registro["error"] = 5
                    self.registro["descrError"] = "El valor no puede almacenarse en k = 8"
                    self.registro["lineaError"] = self.obtener_llave(line,self.codigo)
            else:
                self.registro["error"] = 8
                self.registro["descrError"] = "No hay suficiente memoria para reservar un byte"
                self.registro["lineaError"] = self.obtener_llave(line,self.codigo)                
        else:
            self.registro["error"] = 4
            self.registro["descrError"] = "Error de sintaxis"
            self.registro["lineaError"] = self.obtener_llave(line,self.codigo)

    def hword(self,line):
        
        if(re.search(r"^([A-z]{1}\w*:)?\s*\.hword\s+-?(0x[A-Fa-f0-9]+|0b[01]+|\d+)$",line)) != None:
            if int(self.ram["ultima"],16) <= 537329702:
                
                valor = {re.search(r"0x[A-Fa-f0-9]+$",line):16,re.search(r"0b[01]+$",line):2}
                valor.pop(None)
                valor = int(list(valor.keys())[0].group(),valor[list(valor.keys())[0]]) if len(valor) == 1 else int(re.search(r"-?\d+$",line).group())
                
                if valor >= -32768 and valor <= 32767:
                    valor = hex(int(self.ca2(valor,16),2))
                    valor = "0x" + (6 - len(valor)) * "0" + valor[2:]
                    direccion = self.ram["ultima"]
                    self.ram[direccion] = "0x" + str(valor[4:]).upper()
                    self.ram["0x" + hex(int(direccion,16) + 1)[2:].upper()] = "0x" + str(valor[2:4]).upper()

                    if(re.search(r"^([A-z]{1}\w*:)",line)) != None:
                        self.guardar_etiqueta(re.search(r"^([A-z]{1}\w*)",line).group(),direccion,2,line)                
                    self.ram["ultima"] = "0x" + hex(int(direccion,16) + 2)[2:].upper()
                     
                else:
                    self.registro["error"] = 9
                    self.registro["descrError"] = "No hay suficiente memoria para reservar una media palabra"
                    self.registro["lineaError"] = self.obtener_llave(line,self.codigo)
            else:
                self.registro["error"] = 4
                self.registro["descrError"] = "Error de sintaxis"
                self.registro["lineaError"] = self.obtener_llave(line,self.codigo)                
        else:
            self.registro["error"] = 4
            self.registro["descrError"] = "Error de sintaxis"
            self.registro["lineaError"] = self.obtener_llave(line,self.codigo)

    def wfi(self,line):
        pass
    
    def leer_codigo(self,archivo,codigo):
        # Se realiza la lectura del archivo
        archivoR = open(archivo,"r")
        # Variable centinela que lleva el control de las lineas de codigo.
        i = 1

        # Bucle encargado de realizar la asocicion linea a linea del codigo.
        while True:
            # Lectura de la n-esima linea
            line = archivoR.readline()
            # Si no existe una linea mas se detiene el ciclo.
            if not line:
                break
            # Si la linea es una cadena de texto que carece de caracteres entonces no la almacenara en 
            # el diccionario.
            elif line.isspace() == False:
                # Se realiza un arreglo sobre la linea de codigo capturada, de modo que si posee espacios a su 
                # izquierda o derecha los elimina, ademas elimina el caracter asociado al salto de linea
                line = re.sub("[\\n]","",line.strip())
                # Se realiza un condicional dado que si encuentra la etiqueta .data la almacena para poder realizar 
                # un control sobre los bloques
                if line == ".data":
                    if self.registro["lineaData"] == None:
                        self.registro["lineaData"] = i
                    else:
                        self.codigoError = 1
                        self.descrError = ".data ya fue definido"
                # El mismo proceso del condicional anterior 
                elif line == ".text":
                    if self.registro["lineaText"] == None:
                        self.registro["lineaText"] = i
                    else:
                        self.codigoError = 2
                        self.descrError = ".text ya fue definido"
                codigo[i] = line
            i += 1
        # Eliminacion de las variables y cerrado del archivo ya usado
        del(i)
        archivoR.close()
        del(line)

    def crear_memoria(self,memoria): 
        # Creacion de un diccionario que asocia la direccion de memoria con su valor por defecto, 0x00000000

        return {"0x" + str(hex(i)[2:]).upper() : "0x00" for i in range(537329664,537329704)}

    def exec_text(self,lineaText):
        # Esta liea evalua si existe una etiqueta llemada .text
        if lineaText != None:
            lineaText+= 1
            # Bucle que se usa para evaluar cada una de las lineas de codigo utilizadas
            while True:
                if lineaText in self.codigo and lineaText != self.registro["lineaData"] and self.registro["error"] == None:
                    self.comprobar_instruccion(lineaText)
                elif lineaText == self.registro["lineaData"] or lineaText > max(self.codigo) + 1 or self.registro["error"] != None:
                    break
                lineaText+= 1
    
    def comprobar_instruccion(self,line):
        # Se crea una funcion lambda que servira para saber si el elemento x, se encuentra en en la linea 
        # de codigo que se quiere ejecutar         
        f = lambda x: x if x in self.codigo[line] else None
        
        #Funcion map que se usa en conjunto con la funcion "f" y luego filtra todos los elementos None
        # solo para quedarse con las direcciones
        lista = list(filter(None,list(map(f,self.instrucciones))))
        
        # Si la lista retorna mas de dos valores eso quiere decir que el usuario ingreso mas de dos valores 
        # en su codigo. Ejemplo mov add r1, #255
        if len(lista) == 1:
            self.instrucciones[lista[0]](self.codigo[line])
        else:
                self.registro["error"] = 4
                self.registro["descrError"] = "Error de sintaxis"
                self.registro["lineaError"] = line

    def exec_data(self,lineaData):
        # La logica de esta funcion se maneja de la misma manera que exec_text
        if lineaData != None:
            lineaData +=1
            while True:
                if lineaData in self.codigo and lineaData != self.registro["lineaText"] and self.registro["error"] == None:
                    self.comprobar_instruccion(lineaData)
                elif lineaData == self.registro["lineaText"] or lineaData > max(self.codigo) + 1 or self.registro["error"] != None:
                    break
                lineaData+=1

    def obtener_llave(self,linea,diccionario):
        
        #Obtiene los valores y las llaves de un diccionario
        valores = list(diccionario.values())
        llaves = list(diccionario.keys())

        # if de una sola linea que devuelve la llave de un diccionario
        return llaves[valores.index(linea)] if linea in valores else None

    def guardar_etiqueta(self,etiqueta,direccion,valor,linea):
        if etiqueta not in self.etiqueta:
            self.etiqueta[str(etiqueta)] = str(valor) + direccion
        else:
            self.registro["error"] = 6 
            self.registro["descrError"] = "La etiqueta ya se incializo"
            self.registro["lineaError"] = self.obtener_llave(linea,self.codigo)

#codigo = Codigo("Codigo.txt")
#codigo.exec_data(codigo.registro["lineaData"])
#codigo.exec_text(codigo.registro["lineaText"])
