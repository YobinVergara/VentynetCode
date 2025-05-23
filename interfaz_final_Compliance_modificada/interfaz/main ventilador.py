#para modificar caracteristicas de la ventana
from PyQt5 import QtCore, QtGui, QtWidgets
#libreria para crear la ventana principal de la aplicacion
from PyQt5.QtWidgets import QMainWindow, QApplication
#para importar interfaz .UI
from PyQt5.uic import loadUi
#para realizar la comunicacion serial
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
#para detectar posicion del mouse
from PyQt5.QtCore import QIODevice,QPoint
#para graficas
import pyqtgraph as pg
#para datos de graficas
import numpy as np
#para
import sys
import time
#variable para almacenar datos de entrada
memoria=""
indicador1=False
indicador2=False
##------------------------------------------------------------------------------
##----funcion para decodificar trama de sensores desde SP a PC------------------
##------------------------------------------------------------------------------
def trama_recepcion(x):        
    p=""
    f=""
    v=""
    flag1=0
    flag2=0
    flag3=0
    for i in x:
        if i=="P":
            flag1=1
        elif i=="F":
            flag1=0
            flag2=1
        elif i=="V":
            flag2=0
            flag3=1
        elif i=="?":
            flag3=0
        if flag1==1:
            p=p+i
        if flag2==1:
            f=f+i
        if flag3==1:
            v=v+i
    p=float(p[1:])
    f=float(f[1:])
    v=float(v[1:])
    #if(v<0):
     #   v=0
    return p,f,v

##------------------------------------------------------------------------------
##----Inicia codigo de interfaz-------------------------------------------------
##------------------------------------------------------------------------------

class MyApp(QMainWindow):
    
    
    def __init__(self):
        super(MyApp, self).__init__()
        loadUi('desing.ui',self)

        
        #control conect
        self.modo_op=""
        self.serial=QSerialPort()
        self.bt_connect.clicked.connect(self.serial_connect)
        self.bt_disconected.clicked.connect(self.serial_disconnect)
        self.bt_enviar.clicked.connect(self.config)
        self.bt_enviarP.clicked.connect(self.configurarP)
        self.bt_stop.clicked.connect(self.stop)
        self.bt_stopP.clicked.connect(self.stop)
        self.bt_Reset.clicked.connect(self.reset)
        self.sl_frec.valueChanged.connect(self.calcular)
        self.rel_IE.valueChanged.connect(self.calcular)
        self.sp_Vmax.valueChanged.connect(self.calcular)
        self.sl_Frec.valueChanged.connect(self.calcularP)
        self.Rel_IE.valueChanged.connect(self.calcularP)
        self.sp_Pmax.valueChanged.connect(self.calcularP)

        self.serial.readyRead.connect(self.read_data)
        self.read_ports()
        
        self.ancho=30
        self.x1=list(np.linspace(0,self.ancho,700))
        self.y1=list(np.linspace(0,0,700))
        self.x2=list(np.linspace(0,self.ancho,700))
        self.y2=list(np.linspace(0,0,700))
        self.x3=list(np.linspace(0,self.ancho,700))
        self.y3=list(np.linspace(0,0,700))
        self.x4=list(np.linspace(0,self.ancho,150))
        self.y4=list(np.linspace(0,0,150))
        self.x5=list(np.linspace(0,self.ancho,150))
        self.y5=list(np.linspace(0,0,150))
        self.filtradoP=0
        self.filtradoQ=0
        self.filtradoV=0
        self.V=0
        self.v2=0
        self.colorB1=(255,192,203,100)
        self.colorB2=(50,50,200,100)
        self.colorB3=(189,236,182,100)
        self.colorB4=(189,236,182,100)
        self.colorB5=(189,236,182,100)
        self.colorL1='#da0037'
        self.colorL2='#00c5da'
        self.colorL3='#6eda00'
        self.colorL4='#ffff00'
        self.colorL5='#00ff00'
        #contador para determinar los maximos y minimos
        self.cont=0
        self.cont2=0

        #Grafica Presion
        pg.setConfigOption('background','#040431')
        pg.setConfigOption('foreground','#ffffff')
        self.plt1=pg.PlotWidget(title='Presion')
        self.grafPre.addWidget(self.plt1)
        #Grafica Flujo
        self.plt2=pg.PlotWidget(title='Flujo')
        self.grafFlu.addWidget(self.plt2)
        #Grafica Volumen
        self.plt3=pg.PlotWidget(title='Volumen')
        self.grafVol.addWidget(self.plt3)
        #Grafica Volumen vs presion
        self.plt4=pg.PlotWidget(title='Volumen vs Presion')
        self.grafVolPres.addWidget(self.plt4)
        #Grafica Flujo vs presion
        self.plt5=pg.PlotWidget(title='Flujo vs Volumen')
        self.grafFluPres.addWidget(self.plt5)

        self.read_ports()
        self.n=0
        self.listp=[]
        self.listp2=[]
        self.listf=[]
        self.listv=[]

        #Para contar las primera iteraciones para calcular la Compliance
        self.autoC=0 
        self.arrayPmax=[]
        self.arrayPmin=[]
        self.arrayV=[]
        self.compliance=0.022350303827630615


     
#-----------------------------------------------------------------------------------#
#----funcion para establecer los puertos seiales disponibles------------------------#
#-----------------------------------------------------------------------------------#
    def read_ports(self):
        self.baudrates=['1200','2400','4800','9600','19200','38400','115200']
        portList=[]
        ports=QSerialPortInfo().availablePorts()
        for i in ports:
            portList.append(i.portName())
        self.cb_list_ports.clear()
        self.cb_baudrates.clear()
        self.cb_list_ports.addItems(portList)
        self.cb_baudrates.addItems(self.baudrates)
        self.cb_baudrates.setCurrentText("9600")
    def REC(self):
        self.memoria=""
        memoria=""
    def stop_REC (self):
        archivo=open("datos.txt","w")
        archivo.write(self.memoria)
        archivo.close()
        self.memoria=""
    def calcular(self):
        self.modo_op="Volumen control"
        SL=self.rel_IE.value()
        self.sp_Frec.setValue(self.sl_frec.value())
        mensaje=""
        tciclo=(60/self.sp_Frec.value())-self.sp_tesp1.value()-self.sp_tesp2.value()
        print(tciclo)
        ti=0
        te=0
        if(SL==0):
            mensaje="Relacion 1:1 [s]"
            ti=tciclo*0.5
        elif(SL>0):
            mensaje="Relacion 1:"+str(1+(SL/10))+" [s]"
            ti=tciclo*(1/(2+(SL/10)))
        else:
            mensaje="Relacion "+str(1+(SL/(-10)))+":1 [s]"
            ti=tciclo*((1+(SL/(-10)))/(2+(SL/(-10))))
        self.lb_relacion.setText(mensaje)
        te=tciclo-ti
        self.sp_tisnp.setValue(ti)
        self.sp_tespir.setValue(te)
        print("tinsp="+str(ti)+"  tesp="+str(te))
        print(mensaje)

##Se mutiplica por 60 para pasar segundo a minutos y se divide en 1000 para pasar ml a L##Por qúe el 98 Preguntar?       
        self.sp_Qmax.setValue((60*self.sp_Vmax.value())/(1000*self.sp_tisnp.value())*0.98)

        self.sp_PresT.setValue((0.0025*(self.sp_Qmax.value()**2))+(0.2203*self.sp_Qmax.value())-0.5912)


    def calcularP(self):
        self.modo_op="Presion control"
        SL=self.Rel_IE.value()
        self.sp_FrecP.setValue(self.sl_Frec.value())
        mensaje=""
        tciclo=(60/self.sp_FrecP.value())-self.sp_TespI.value()-self.sp_TespE.value()
        print(tciclo)
        ti=0
        te=0
        if(SL==0):
            mensaje="Rel 1:1 [s]"
            ti=tciclo*0.5
        elif(SL>0):
            mensaje="Rel 1:"+str(1+(SL/10))+" [s]"
            ti=tciclo*(1/(2+(SL/10)))
        else:
            mensaje="Rel "+str(1+(SL/(-10)))+":1 [s]"
            ti=tciclo*((1+(SL/(-10)))/(2+(SL/(-10))))
        self.lb_relacionP.setText(mensaje)
        te=tciclo-ti
        self.sp_Tinsp.setText(str(round(ti,2)))
        self.sp_Tespir.setText(str(round(te,2)))
        self.sp_tisnp.setValue(ti)
        self.sp_tespir.setValue(te)
        print("tinsp="+str(ti)+"  tesp="+str(te))
        print(mensaje)

        C=self.compliance  ##Compliancia pulmonar L/cmH2o
        
        PEEP = self.sp_Peep.value()
        PIP = self.sp_Pmax.value()
        Vtil=1000*(C*(PIP-PEEP))
        Qmax = (C*(PIP-PEEP))/(ti/60) ##L/min
        self.sp_Vmax.setValue(Vtil)
        self.sp_Qmax.setValue(Qmax)
        self.sp_PresT.setValue((0.0025*(self.sp_Qmax.value()**2))+(0.2203*self.sp_Qmax.value())-0.5912)
        #self.compliance.setText(str(round(C,5)))
        print("PIP = "+str(PIP)+ " PEEP = "+str(PEEP)+ " C = "+str(C)+ " Ti = "+str(ti)+" Vt= "+str(Vtil))
        print("Flujo = "+str(Qmax)+ " Presión tanque = "+str(self.sp_PresT.value()))

        

#-----------------------------------------------------------------------------------#
#----funcion para generar la coneccion serial---------------------------------------#
#-----------------------------------------------------------------------------------#
    def serial_connect(self):
        self.serial.waitForReadyRead(100)
        self.port=self.cb_list_ports.currentText()
        self.baud=self.cb_baudrates.currentText()
        self.serial.setBaudRate(int(self.baud))
        self.serial.setPortName(self.port)
        self.serial.open(QIODevice.ReadWrite)
        if self.serial.isOpen():
            dat="a?E?0?0?0?0?0?0?0?0?0?0"
            self.serial.write(dat.encode())
        else:
            self.label_34.setText("Error")
            print("no se pudo abrir puerto")
    def serial_disconnect(self):
        dat="b?E?0?0?0?0?0?0?0?0?0?0"
        self.serial.write(dat.encode())
        lambda:self.serial.close()
        self.label_34.setText("----")
#-----------------------------------------------------------------------------------#
#----funcion para leer datos--------------------------------------------------------#
#-----------------------------------------------------------------------------------#
    def read_data(self):
        if not self.serial.canReadLine(): return
        rx=self.serial.readLine()
        x=str(rx,'utf8').strip()
        #print(x)
        if(x[0]=="L"):
            x=x[1:]
            #print("el sistema ha sido "+x)
            self.label_34.setText(x)
#-----------------------------------------------------------------------------------#
#-------------- cuando se recibe una trama de sensores inicia por S ----------------#
#-----------------------------------------------------------------------------------#
        elif(x[0]=="S"):
#-----------------------------------------------------------------------------------#            
#-------------- decodificacion de la trama de sensores------------------------------#
#-----------------------------------------------------------------------------------#
            p,f,v=trama_recepcion(x)
            print(f"P: {p} F: {f} V: {v}")
#-----------------------------------------------------------------------------------#            
#-------------- filtro de media movil exponencial ----------------------------------#
#-----------------------------------------------------------------------------------#
            alphaP=0.1
            alphaQ=0.5
            alphaV=0.3
            self.filtradoP=(alphaP*p)+(1-alphaP)*self.filtradoP 
            p=self.filtradoP
            self.filtradoQ=(alphaQ*f)+(1-alphaQ)*self.filtradoQ
            f=self.filtradoQ
            self.filtradoV=(alphaV*v)+(1-alphaV)*self.filtradoV
            v=self.filtradoV
            print(f"PF: {p} FF: {f} VF: {v}")
            
#-----------------------------------------------------------------------------------#            
#-------------- calculo del volumen ------------------------------------------------#
#-----------------------------------------------------------------------------------#
            self.v2=self.v2+f
            if(self.v2<0 or v==0):
                self.v2=0
            #v=self.v2
#-----------------------------------------------------------------------------------#         
#--------- almacenamiento de las señales -------------------------------------------#
#-----------------------------------------------------------------------------------#
            tiempo=str(time.time())
            linea=str(p)+"="+str(f)+"="+str(v)+"="+tiempo+"\n"
            archivo=open("datos.txt","a")
            archivo.write(linea)
            archivo.close()
#-----------------------------------------------------------------------------------#            
#--------- calculo de maximos y minimos de la presion ------------------------------#
#-----------------------------------------------------------------------------------#
            self.listp.append(p)
            self.listp2.append(p)
            if(self.cont==100):
                maximoP=np.amax(self.listp)
                self.label_19.setText("{:.1f}".format(maximoP))
                minimoP=np.amin(self.listp)
                self.label_21.setText("{:.1f}".format(minimoP))
                self.listp=[]

                
            #if(self.n>=4):
                #self.label_20.setText("{:.1f}".format(p))
            self.graficador1(p)
            self.graficador4(p)
#-----------------------------------------------------------------------------------#            
#--------- calculo de maximos y minimos del flujo ----------------------------------#
#-----------------------------------------------------------------------------------#
            self.listf.append(f)
            if(self.cont==100):
                maximof=np.amax(self.listf)
                self.label_24.setText("{:.0f}".format(maximof))
                minimof=np.amin(self.listf)
                self.label_26.setText("{:.0f}".format(minimof))
                self.listf=[]
            if(self.n>=4):
                self.label_22.setText("{:.0f}".format(f))
            self.graficador2(f)
#-----------------------------------------------------------------------------------#            
#--------- calculo de maximos y minimos del volumen --------------------------------#
#-----------------------------------------------------------------------------------#
            self.listv.append(v)
            if(self.cont==100):
                maximov=np.amax(self.listv)
                self.label_30.setText("{:.0f}".format(maximov))
                self.cont=0
                self.listv=[]
            if(self.n>=4):
                self.label_28.setText("{:.0f}".format(v))
            self.graficador3(v)
            self.graficador5(f)
            self.cont=self.cont+1
            self.cont2=self.cont2+1

        self.n=self.n+1

        
        #Para aumentar cada ciclo y guardar en una lista la PIP, PEEP y el volumen
        if (self.cont==100):
                self.autoC +=1
                self.arrayPmax.append(np.amax(self.listp))
                self.arrayPmin.append(np.amin(self.listp))
                self.arrayV.append(np.amax(self.listv))
                #print("Ciclo: " + str(self.autoC))

                #Cuando pasen 6 ciclos se empieza a recalcular la compliance
                if (self.autoC==5):
                    
                    PIP = self.sp_Pmax.value()
                    #print("Lista PIP" + str(self.arrayPmax))
                    #print("Lista PEEP" + str(self.arrayPmin))
                    #print("Lista Volumen" + str(self.arrayV))
                    
                    error = ((abs(PIP - self.arrayPmax[self.autoC-1]))/PIP)*100
                    print("Error: "+str(error))
                    
                    if error > 5:
                        
                        #Se eliminan los primeros dos términos ya que siempre son elevados
                        self.arrayPmax = self.arrayPmax[2:]
                        self.arrayPmin = self.arrayPmin[2:]
                        self.arrayV = self.arrayV[2:]
                        
                        #Se encuentra el promedio
                        promPmax = sum(self.arrayPmax) / len (self.arrayPmax)
                        promPmin = sum(self.arrayPmin) / len (self.arrayPmin)
                        promV = (sum(self.arrayV) / len (self.arrayV))/1000

                        #print ("Promedio PIP: " + str(promPmax))
                        #print ("Promedio PEEP: " + str(promPmin))
                        #print ("Promedio Volumen: " + str(promV))
                        #Nueva compliance
                        C=promV/(promPmax-promPmin)
                        
                        #Volver a enviar los parámetros corregidos
                        self.compliance = C
                        print("Nuevo valor de C: "+str(C))
                        self.calcularP()
                        self.configurarP()
                    
               
#-----------------------------------------------------------------------------------#
#----Grafica de la Presion----------------------------------------------------------#
#-----------------------------------------------------------------------------------#
    def graficador1(self,h):
        self.y1=self.y1[1:]
        self.y1.append(h)
        self.plt1.clear()
        self.plt1.plot(self.x1,self.y1, pen=pg.mkPen(self.colorL1,width=2),fillLevel=0, brush=(self.colorB1))
            # Calcula la media de los datos
        media = np.mean(self.y1)
        self.label_20.setText("{:.1f}".format(media))

        # Agrega la línea horizontal de la media
        self.media_line = pg.InfiniteLine(pos=media, angle=0, pen=pg.mkPen('b'))
        self.plt1.addItem(self.media_line)
        self.plt1.showGrid(x=True, y=True)


#-----------------------------------------------------------------------------------#
#----Grafica del Flujo--------------------------------------------------------------#
#-----------------------------------------------------------------------------------#
    def graficador2(self,h):
        self.y2=self.y2[1:]
        self.y2.append(h)
        self.plt2.clear()
        self.plt2.plot(self.x2,self.y2, pen=pg.mkPen(self.colorL2,width=2),fillLevel=-0.3, brush=(self.colorB2))
        self.plt2.showGrid(x=True, y=True)
        
#-----------------------------------------------------------------------------------#
#----Grafica del Volumen------------------------------------------------------------#
#-----------------------------------------------------------------------------------#
    def graficador3(self,h):
        self.y3=self.y3[1:]
        self.y3.append(h)
        self.plt3.clear()
        self.plt3.plot(self.x3,self.y3, pen=pg.mkPen(self.colorL3,width=2),fillLevel=-0.3, brush=(self.colorB3))
        self.plt3.showGrid(x=True, y=True)
        
#-----------------------------------------------------------------------------------#
#----Grafica cerrada Vol Pres------------------------------------------------------------#
#-----------------------------------------------------------------------------------#
    def graficador4(self,h):
        self.y4=self.y4[1:]
        self.x4=self.y3[550:]
        self.y4.append(h)
        self.plt4.clear()
        self.plt4.plot(self.y4,self.x4, pen=pg.mkPen(self.colorL4,width=2))
        self.plt4.showGrid(x=True, y=True)
        

#-----------------------------------------------------------------------------------#
#----Grafica cerrada Flujo Vol------------------------------------------------------------#
#-----------------------------------------------------------------------------------#
    def graficador5(self,h):
        self.y5=self.y5[1:]
        self.x5=self.y3[550:]
        self.y5.append(h)
        self.plt5.clear()
        self.plt5.plot(self.x5,self.y5, pen=pg.mkPen(self.colorL5,width=2))
        self.plt5.showGrid(x=True, y=True)

#-----------------------------------------------------------------------------------#
#----funcion para enviar datos por el puerto seial----------------------------------#
#-----------------------------------------------------------------------------------#
    def send_data(self, data):
        data=data+"\n"
        print(data)
        if self.serial.isOpen():
            self.serial.write(data.encode())
            print("enviado")
        else:
            print("no se pudo abrir puerto")


#-----------------------------------------------------------------------------------#
#----funcion para enviar la configuracion a la tarjeta electronica------------------#
#-----------------------------------------------------------------------------------#
            
    def config(self):
        trama=""
        if(self.modo_op=="Volumen control"):
            trama="V?"
        elif(self.cb_modo_op.currentText()=="Presion Control"):
            trama="P?"
        elif(self.cb_modo_op.currentText()=="Flujo control"):
            trama="F?"
        if(self.cb_tp_onda.currentText()=="Escalon"):
            trama=trama+"E?"
        elif(self.cb_tp_onda.currentText()=="Rampa Descendente"):
            trama=trama+"R?"
        trama=trama+str(self.sp_FIO2.value())+"?"
        trama=trama+str(self.sp_Vmax.value())+"?"
        trama=trama+str(self.sp_Pmax.value())+"?"
        trama=trama+str(self.sp_Qmax.value())+"?"
        trama=trama+str(self.sp_PEEP.value())+"?"
        trama=trama+str(self.sp_Frec.value())+"?"
        trama=trama+str(self.sp_tisnp.value())+"?"
        trama=trama+str(self.sp_tesp1.value())+"?"
        trama=trama+str(self.sp_tespir.value())+"?"
        trama=trama+str(self.sp_tesp2.value())+"?"
        trama=trama+str(self.sp_air.value())+"?"
        trama=trama+str(self.sp_o2.value())+"?"
        trama=trama+str(self.sp_PresT.value())
        print(trama)
        self.send_data(trama)


#-----------------------------------------------------------------------------------#
#----funcion para enviar la configuracion a la tarjeta electronica------------------#
#-----------------------------------------------------------------------------------#
    def configurarP(self):
        self.autoC=0
        self.arrayPmax=[]
        self.arrayPmin=[]
        self.arrayV=[]
        self.configP()
            
    def configP(self):
        trama="P?"
        if(self.cb_tp_onda.currentText()=="Escalon"):
            trama=trama+"E?"
        elif(self.cb_tp_onda.currentText()=="Rampa Descendente"):
            trama=trama+"R?"
        trama=trama+str(self.sp_FIO2.value())+"?"
        trama=trama+str(self.sp_Vmax.value())+"?"
        trama=trama+str(self.sp_Pmax.value())+"?"
        trama=trama+str(self.sp_Qmax.value())+"?"
        trama=trama+str(self.sp_Peep.value())+"?"
        trama=trama+str(self.sp_FrecP.value())+"?"
        trama=trama+str(self.sp_Tinsp.text())+"?"
        trama=trama+str(self.sp_TespI.value())+"?"
        trama=trama+str(self.sp_Tespir.text())+"?"
        trama=trama+str(self.sp_TespE.value())+"?"
        trama=trama+str(self.sp_air.value())+"?"
        trama=trama+str(self.sp_o2.value())+"?"
        trama=trama+str(self.sp_PresT.value())
        print(trama)
        self.send_data(trama)

#-----------------------------------------------------------------------------------#
#----funcion para detener el sistema------------------------------------------------#
#-----------------------------------------------------------------------------------#
    def stop(self):
        self.send_data("f?E?0?0?0?0?0?0?0?0?0?0")
    def reset(self):
        self.send_data("r?E?0?0?0?0?0?0?0?0?0?0")
        
        
#-----------------------------------------------------------------------------------#
#----Las siguientes lineas permiten crear una ventana a partir----------------------#
#----de la interfaz creada----------------------------------------------------------#
#-----------------------------------------------------------------------------------#
if __name__ == "__main__":
    app=QApplication(sys.argv)
    my_app=MyApp()
    my_app.show()
    sys.exit(app.exec_())
    
