import sys
from PyQt5 import uic, QtCore, QtWidgets, QtSerialPort, QtGui
from PyQt5.QtGui import QIcon
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys
import os
import csv
import ctypes
import numpy as np

#Define
class Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        self.portname_comboBox = QtWidgets.QComboBox()
        self.baudrate_comboBox = QtWidgets.QComboBox()

        for info in QtSerialPort.QSerialPortInfo.availablePorts():
            self.portname_comboBox.addItem(info.portName())

        for baudrate in QtSerialPort.QSerialPortInfo.standardBaudRates():
            self.baudrate_comboBox.addItem(str(baudrate), baudrate)

        buttonBox = QtWidgets.QDialogButtonBox()
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        lay = QtWidgets.QFormLayout(self)
        lay.addRow("Port Name:", self.portname_comboBox)
        lay.addRow("BaudRate:", self.baudrate_comboBox)
        lay.addRow(buttonBox)
        self.setFixedSize(self.sizeHint())

    def get_results(self):
        return self.portname_comboBox.currentText(), self.baudrate_comboBox.currentData()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('gui.ui', self)
        self.setWindowIcon(QIcon('Icon.png')) # set the icon  
        self.setWindowTitle('ADConductivity Sensor') # set the title
        
        myappid = u'ApparateDesign.ConductivitySensor.version.0_1' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.cx = [0,0]
        self.cy = [0,0]
        self.Tx = [0,0]
        self.Ty = [0,0]
        pen = pg.mkPen(color=(255, 0, 0))

        self.conDataLine =  self.ConductivityPlotWindow.plot(self.cx, self.cy, pen=pen)        
        self.TempDataLine =  self.TemperaturePlotWindow.plot(self.Tx, self.Ty, pen=pen)

        pg.setConfigOptions(antialias=True)
        self.ConductivityPlotWindow.setBackground('w')
        pg.setConfigOption('foreground', 'k')
        styles = {'font':'Segoe UI', 'font-size':'10pt'}
        self.ConductivityPlotWindow.setTitle("Conductivity", size="12pt")
        self.ConductivityPlotWindow.setLabel('left', 'Conductivity [mS/cm]', **styles)
        self.ConductivityPlotWindow.setLabel('bottom', 'Time since reset [mSec]', **styles)
        self.ConductivityPlotWindow.showGrid(x=True, y=True)
 
 
        styles = {'font':'Segoe UI', 'font-size':'10pt'}
        self.TemperaturePlotWindow.setBackground('w')
        self.TemperaturePlotWindow.setTitle("Temperature", size="12pt")
        self.TemperaturePlotWindow.setLabel('left', 'Temperature [°C]', **styles)
        self.TemperaturePlotWindow.setLabel('bottom', 'Time since reset [mSec]', **styles)
        self.TemperaturePlotWindow.showGrid(x=True, y=True)



        self.show()
        self.u_high = 0
        self.u_mid = 0
        self.Temperature = 0
        self.cell_constant = 0
        self.TemperatureCoefficient = 0
        self.cond = 0
        self.ref_res=200
        self.conductivity=0
        self.conductivityTcomp = 0
        self.m = 0
        self.b = 0
        self.R0 = 100
        self.Tcoefficient = 100
        self.timeOfVoltageSend = 0
        self.AutoscrollSingleMeasurementEnabled = False
        self.AutoscrollContiMeasurementEnabled = False
        
        ### ----- Serial Communication ----- ###
        self.configureButtonConductivity.clicked.connect(self.openDialogPortVoltages)
        self.cnctButtonConductivity.clicked.connect(self.connectToConductivityPort)

        self.configureButtonTemperature.clicked.connect(self.openDialogPortTemperature)
        self.cnctButtonTemperature.clicked.connect(self.connectToTemperaturePort)

        self.measureButton_1.clicked.connect(self.calibrationPoint_1)
        self.measureButton_2.clicked.connect(self.calibrationPoint_2)
        self.measureButton_3.clicked.connect(self.calibrationPoint_3)
        self.resetCalibrationButton.clicked.connect(self.resetCalibration)
        self.calibrateButton.clicked.connect(self.calibrate)

        self.radioButton_22.clicked.connect(self.set_ref_22)
        self.radioButton_200.clicked.connect(self.set_ref_200)
        self.radioButton_2000.clicked.connect(self.set_ref_2000)
        self.nr_u_high.setReadOnly(True)
        self.nr_u_mid.setReadOnly(True)
        self.nr_rtd_res.setReadOnly(True)

        self.serialVoltages = QtSerialPort.QSerialPort(self, readyRead=self.receiveVoltages)
        self.serialTemperature = QtSerialPort.QSerialPort(self, readyRead=self.receiveTemperature)
 
        self.addSingleMeasurement.clicked.connect(self.addMeasurementData)
        self.addCalibration.clicked.connect(self.addCalibrationData)
        self.buttonLoadCalibrationFromTable.clicked.connect(self.loadCalibrationFromTable)
        self.updateFrequency = 10
        self.buttonSetUpdateFrequency.clicked.connect(self.setUpdateFrequency)
        self.buttonStartContinuousMeasurement.clicked.connect(self.startContinuousMeasurement)

        self.setCurrentRTD.clicked.connect(self.setR0)

        self.buttonNewSingleFile.clicked.connect(self.newSingleFile)
        self.buttonLoadSingleFile.clicked.connect(self.loadSingleFile)
        self.buttonSaveSingleFile.clicked.connect(self.saveSingleFile)
        
        self.buttonNewCalibrationFile.clicked.connect(self.newCalibrationFile)
        self.buttonLoadCalibrationFile.clicked.connect(self.loadCalibrationFile)
        self.buttonSaveCalibrationFile.clicked.connect(self.saveCalibrationFile)
        
        self.buttonNewContiFile.clicked.connect(self.newContiFile)
        self.buttonLoadContiFile.clicked.connect(self.loadContiFile)
        self.buttonSaveContiFile.clicked.connect(self.saveContiFile)                
        
        self.autoscrollSingleMeasurement.clicked.connect(self.enableAutoscrollSingleMeasurement)
        self.autoscrollContiMeasurement.clicked.connect(self.enableAutoscrollContiMeasurement)
        self.buttonDeleteCalibrationRow.clicked.connect(self.deleteCalibrationRow)
        self.buttonDeleteSingleMeasurementRow.clicked.connect(self.deleteSingleMeasurementRow)
        self.buttonDeleteContiMeasurementRow.clicked.connect(self.deleteContiMeasurementRow)                
        self.conStartPlot.clicked.connect(self.startConductivityPlot)
        self.conClearPlot.clicked.connect(self.clearConductivityPlot)
        self.TempStartPlot.clicked.connect(self.startTemperaturePlot)
        self.TempClearPlot.clicked.connect(self.clearTemperaturePlot)

    @QtCore.pyqtSlot()
    def openDialogPortVoltages(self):
        dialog = Dialog()
        if dialog.exec_():
            portname, baudrate = dialog.get_results()
            self.serialVoltages.setPortName(portname)
            self.serialVoltages.setBaudRate(baudrate)
            notification = '>C-sensor: port '+str(portname)+' and baudrate '+str(baudrate)+' set'
        self.notifications.appendPlainText(notification)

    @QtCore.pyqtSlot()
    def openDialogPortTemperature(self):
        dialog = Dialog()
        if dialog.exec_():
            portname, baudrate = dialog.get_results()
            self.serialTemperature.setPortName(portname)
            self.serialTemperature.setBaudRate(baudrate)        
            notification = '>T-sensor: port '+str(portname)+' and baudrate '+str(baudrate)+' set'
        self.notifications.appendPlainText(notification)
    @QtCore.pyqtSlot()
    def receiveVoltages(self):
        while self.serialVoltages.canReadLine():
            text = self.serialVoltages.readLine().data().decode(errors='ignore')
            text = text.rstrip('\r\n')
            u = text.split(";")
            
            try:
                self.u_high = float(u[1])
                self.u_mid  = float(u[2])
                self.timeOfVoltageSend   = float(u[0])               
            except:
                pass
        
            self.res = self.clc_res()
            self.cond = self.clc_cond()
            self.nr_resistance.setText(str(round(self.res,2)))
            self.nr_u_high.setText(str(round(self.u_high,0)))
            self.nr_u_mid.setText(str(round(self.u_mid,0)))
            self.nr_conductance.setText(str(round(self.cond,3)))
            self.clc_conductivity()
    @QtCore.pyqtSlot()
    def receiveTemperature(self):
        while self.serialTemperature.canReadLine():
            text = self.serialTemperature.readLine().data().decode(errors='ignore')
            text = text.rstrip('\r\n')
            R = text.split(";")
            try:
                self.RTDValue = float(R[0])
            except:
                pass
            self.nr_rtd_res.setText(str(round(self.RTDValue,3)))
            self.calibrateRTD()

    def get_results(self):
        return self.portname_comboBox.currentText(), self.baudrate_comboBox.currentData()
    
    @QtCore.pyqtSlot(bool)
    def connectToConductivityPort(self, checked):
        self.cnctButtonConductivity.setText("Disconnect" if checked else "Connect")
        if checked:
            if not self.serialVoltages.isOpen():
                self.notifications.appendPlainText('>conductivity sensor connected')
                if not self.serialVoltages.open(QtCore.QIODevice.ReadWrite):
                    self.cnctButtonConductivity.setChecked(False)
                    
        else:
            self.serialVoltages.close()
            self.nr_u_high.setText(str(0))
            self.nr_u_mid.setText(str(0))
            self.notifications.appendPlainText('>conductivity sensor disconnected')
 
    @QtCore.pyqtSlot(bool)
    def connectToTemperaturePort(self, checked):
        self.cnctButtonTemperature.setText("Disconnect" if checked else "Connect")
        if checked:    
            if not self.serialTemperature.isOpen():
                self.notifications.appendPlainText('>temperature sensor connected')
                if not self.serialTemperature.open(QtCore.QIODevice.ReadWrite):
                    self.cnctButtonTemperature.setChecked(False)
        else:
            self.serialTemperature.close()
            self.nr_rtd_res.setText(str(0))
            self.notifications.appendPlainText('>temperature sensor disconnected')

    @QtCore.pyqtSlot(bool)
    def startConductivityPlot(self, checked):
        self.conStartPlot.setText("Stop Plot" if checked else "Start Plot")
        if checked:
            self.conPlotTimer = QtCore.QTimer()
            self.conPlotTimer.setInterval(int(self.conUpdateTime.text()))
            self.conPlotTimer.timeout.connect(self.updateConductivityPlotData)
            self.conPlotTimer.start()
            pen = pg.mkPen(color=(255, 0, 0))

            self.notifications.appendPlainText('>conductivity plot started')
        else:   
            self.conPlotTimer.stop()
            self.conStartPlot.setChecked(False)
            self.notifications.appendPlainText('>conductivity plot stopped')

    @QtCore.pyqtSlot(bool)
    def startTemperaturePlot(self, checked):
        self.TempStartPlot.setText("Stop Plot" if checked else "Start Plot")
        if checked:
            self.TempPlotTimer = QtCore.QTimer()
            self.TempPlotTimer.setInterval(int(self.TempUpdateTime.text()))
            self.TempPlotTimer.timeout.connect(self.updateTemperaturePlotData)
            self.TempPlotTimer.start()
            self.notifications.appendPlainText('>Temperature plot started')
        else:   
            self.TempPlotTimer.stop()
            self.TempStartPlot.setChecked(False)
            self.notifications.appendPlainText('>Temperature plot stopped')

    def clearConductivityPlot(self):
        self.cx = [self.timeOfVoltageSend,self.timeOfVoltageSend]
        self.cy = [self.conductivity,self.conductivity]
        self.conDataLine.clear()

    def clearTemperaturePlot(self):
        self.Tx = [self.timeOfVoltageSend,self.timeOfVoltageSend]
        self.Ty = [self.Temperature,self.Temperature]
        self.TempDataLine.clear()        

    def updateConductivityPlotData(self):
        if len(self.cx)>=int(self.conPlotInterval.text()):
            self.cx = self.cx[1:]  # Remove the first y element.
        self.cx.append(self.timeOfVoltageSend)  # Add a new value 1 higher than the last.
        if len(self.cy)>=int(self.conPlotInterval.text()):
            self.cy = self.cy[1:]  # Remove the first
        self.cy.append(self.conductivity)  # Add a new random value.
        self.conDataLine.setData(self.cx, self.cy)  # Update the data.

    def updateTemperaturePlotData(self):
        if len(self.Tx)>=int(self.TempPlotInterval.text()):
            self.Tx = self.Tx[1:]  # Remove the first y element.
        self.Tx.append(self.timeOfVoltageSend)  # Add a new value 1 higher than the last.
        if len(self.Ty)>=int(self.TempPlotInterval.text()):
            self.Ty = self.Ty[1:]  # Remove the first
        self.Ty.append(self.Temperature)  # Add a new random value.
        self.TempDataLine.setData(self.Tx, self.Ty)  # Update the data        

    def newSingleFile(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Create new CSV', os.getenv('HOME'), 'All files (*)')
        self.singleMeasurements.setRowCount(0)
        self.singleFilePath.setText(path[0])
        if path[0] != '':
            with open(path[0],newline='') as csv_file:
                my_file = csv.reader(csv_file, delimiter=';')
                next(my_file)
                for row_data in my_file:
                    row = self.singleMeasurements.rowCount()
                    self.singleMeasurements.insertRow(row)
                    self.singleMeasurements.setColumnCount(len(row_data))
                    for column, stuff in enumerate(row_data):
                        item = QtWidgets.QTableWidgetItem(stuff)
                        self.singleMeasurements.setItem(row, column, item)                
        self.notifications.appendPlainText('>New Measurement CSV file opened')

    def loadSingleFile(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Measurement CSV', os.getenv('HOME'), 'CSV(*.csv)')
        self.singleMeasurements.setRowCount(0)
        self.singleFilePath.setText(path[0])
        if path[0] != '':
            with open(path[0],newline='') as csv_file:
                my_file = csv.reader(csv_file, delimiter=';')
                next(my_file)
                for row_data in my_file:
                    row = self.singleMeasurements.rowCount()
                    self.singleMeasurements.insertRow(row)
                    self.singleMeasurements.setColumnCount(len(row_data))
                    for column, stuff in enumerate(row_data):
                        item = QtWidgets.QTableWidgetItem(stuff)
                        self.singleMeasurements.setItem(row, column, item)                
        self.notifications.appendPlainText('>Measurement CSV file opened')

    def saveSingleFile(self):
        path = self.singleFilePath.text()
        print(path)
        self.singleFilePath.setText(path)
        if path != '':
            with open(path,'w', newline='') as csv_file:
                writer = csv.writer(csv_file, delimiter=';')
                headers = [self.singleMeasurements.horizontalHeaderItem(c).text() for c in range(self.singleMeasurements.columnCount())]
                writer.writerow(headers)
                for row in range(self.singleMeasurements.rowCount()):
                    rowdata = []
                    for column in range(self.singleMeasurements.columnCount()):
                        item = self.singleMeasurements.item(row, column)
                        if item is not None:
                            rowdata.append(item.text())
                        else:
                            rowdata.append('')
                    writer.writerow(rowdata)
        self.notifications.appendPlainText('>Measurement CSV file saved')                                 

    def newContiFile(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Create new CSV', os.getenv('HOME'), 'All files (*)')
        self.contiMeasurements.setRowCount(0)
        self.contiFilePath.setText(path[0])
        if path[0] != '':
            with open(path[0],newline='') as csv_file:
                my_file = csv.reader(csv_file, delimiter=';')
                next(my_file)
                for row_data in my_file:
                    row = self.contiMeasurements.rowCount()
                    self.contiMeasurements.insertRow(row)
                    self.contiMeasurements.setColumnCount(len(row_data))
                    for column, stuff in enumerate(row_data):
                        item = QtWidgets.QTableWidgetItem(stuff)
                        self.contiMeasurements.setItem(row, column, item)                
        self.notifications.appendPlainText('>New Continuous CSV file opened')

    def loadContiFile(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Measurement CSV', os.getenv('HOME'), 'CSV(*.csv)')
        self.contiMeasurements.setRowCount(0)
        self.contiFilePath.setText(path[0])
        if path[0] != '':
            with open(path[0],newline='') as csv_file:
                my_file = csv.reader(csv_file, delimiter=';')
                next(my_file)
                for row_data in my_file:
                    row = self.contiMeasurements.rowCount()
                    self.contiMeasurements.insertRow(row)
                    self.contiMeasurements.setColumnCount(len(row_data))
                    for column, stuff in enumerate(row_data):
                        item = QtWidgets.QTableWidgetItem(stuff)
                        self.contiMeasurements.setItem(row, column, item)                
        self.notifications.appendPlainText('>Continuous CSV file opened')

    def saveContiFile(self):
        path = self.contiFilePath.text()
        print(path)
        self.contiFilePath.setText(path)
        if path != '':
            with open(path,'w', newline='') as csv_file:
                writer = csv.writer(csv_file, delimiter=';')
                headers = [self.contiMeasurements.horizontalHeaderItem(c).text() for c in range(self.contiMeasurements.columnCount())]
                writer.writerow(headers)
                for row in range(self.contiMeasurements.rowCount()):
                    rowdata = []
                    for column in range(self.contiMeasurements.columnCount()):
                        item = self.contiMeasurements.item(row, column)
                        if item is not None:
                            rowdata.append(item.text())
                        else:
                            rowdata.append('')
                    writer.writerow(rowdata)
        self.notifications.appendPlainText('>Measurement CSV file saved')  

    def newCalibrationFile(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Create new CSV', os.getenv('HOME'), 'All files (*)')
        self.calibrationData.setRowCount(0)
        self.calibFilePath.setText(path[0])
        if path[0] != '':
            with open(path[0],newline='') as csv_file:
                my_file = csv.reader(csv_file, delimiter=';')
                next(my_file)
                for row_data in my_file:
                    row = self.calibrationData.rowCount()
                    self.calibrationData.insertRow(row)
                    self.calibrationData.setColumnCount(len(row_data))
                    for column, stuff in enumerate(row_data):
                        item = QtWidgets.QTableWidgetItem(stuff)
                        self.calibrationData.setItem(row, column, item)                
        self.notifications.appendPlainText('>New Calibration CSV file opened')

    def loadCalibrationFile(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Calibration CSV', os.getenv('HOME'), 'CSV(*.csv)')
        self.calibrationData.setRowCount(0)
        self.calibFilePath.setText(path[0])
        if path[0] != '':
            with open(path[0],newline='') as csv_file:
                my_file = csv.reader(csv_file, delimiter=';')
                next(my_file)
                for row_data in my_file:
                    row = self.calibrationData.rowCount()
                    self.calibrationData.insertRow(row)
                    self.calibrationData.setColumnCount(len(row_data))
                    for column, stuff in enumerate(row_data):
                        item = QtWidgets.QTableWidgetItem(stuff)
                        self.calibrationData.setItem(row, column, item)                
        self.notifications.appendPlainText('>Calibration CSV file opened')

    def saveCalibrationFile(self):
            path = self.calibFilePath.text()
            print(path)
            self.calibFilePath.setText(path)
            if path != '':
                with open(path,'w', newline='') as csv_file:
                    writer = csv.writer(csv_file, delimiter=';')
                    headers = [self.calibrationData.horizontalHeaderItem(c).text() for c in range(self.calibrationData.columnCount())]
                    writer.writerow(headers)
                    for row in range(self.calibrationData.rowCount()):
                        rowdata = []
                        for column in range(self.calibrationData.columnCount()):
                            item = self.calibrationData.item(row, column)
                            if item is not None:
                                rowdata.append(item.text())
                            else:
                                rowdata.append('')
                        writer.writerow(rowdata)
            self.notifications.appendPlainText('>Calibration CSV file saved') 
    
    def addMeasurementData(self):
        row_data = [self.u_high, self.u_mid, self.Temperature, self.ref_res, round(self.cell_constant,5), self.TemperatureCoefficient, round(self.cond,5), round(self.conductivity,5), round(self.conductivityTcomp,5)]
        row = self.singleMeasurements.rowCount()
        self.singleMeasurements.setRowCount(row+1)
        col = 0
        for item in row_data:
            cell = QtWidgets.QTableWidgetItem(str(item))
            self.singleMeasurements.setItem(row, col, cell)
            col += 1
        if self.AutoscrollSingleMeasurementEnabled == True:                
            self.singleMeasurements.scrollToBottom()

    def addCalibrationData(self):
        for i in [0,1,2]:
            row_data = [i+1, self.u_high_cal[i], self.u_mid_cal[i], self.Temperature, self.ref_res, self.ref_con[i]]       
            row = self.calibrationData.rowCount()
            self.calibrationData.setRowCount(row+1)
            col = 0
            for item in row_data:
                cell = QtWidgets.QTableWidgetItem(str(item))
                self.calibrationData.setItem(row, col, cell)
                col += 1
            
    def addContinuousMeasurement(self):
        row_data = [self.timeOfVoltageSend, self.u_high, self.u_mid, self.Temperature, self.ref_res, round(self.cell_constant,5), self.TemperatureCoefficient, round(self.cond,5), round(self.conductivity,5), round(self.conductivityTcomp,5)]
        row = self.contiMeasurements.rowCount()
        self.contiMeasurements.setRowCount(row+1)
        col = 0
        for item in row_data:
            cell = QtWidgets.QTableWidgetItem(str(item))
            self.contiMeasurements.setItem(row, col, cell)
            col += 1
        if self.AutoscrollContiMeasurementEnabled == True:                
            self.contiMeasurements.scrollToBottom()

    def enableAutoscrollSingleMeasurement(self, checked):
        self.autoscrollSingleMeasurement.setText("Disable Autoscroll" if checked else "Enable Autoscroll")
        if checked:
            self.AutoscrollSingleMeasurementEnabled = True
            self.notifications.appendPlainText('>Autoscroll enabled')
        else:   
            self.AutoscrollSingleMeasurementEnabled = False
            self.autoscrollSingleMeasurement.setChecked(False)
            self.notifications.appendPlainText('>Autoscroll disabled')

    def enableAutoscrollContiMeasurement(self, checked):
        self.autoscrollContiMeasurement.setText("Disable Autoscroll" if checked else "Enable Autoscroll")
        if checked:
            self.AutoscrollContiMeasurementEnabled = True
            self.notifications.appendPlainText('>Autoscroll enabled')
        else:   
            self.AutoscrollContiMeasurementEnabled = False
            self.autoscrollContiMeasurement.setChecked(False)
            self.notifications.appendPlainText('>Autoscroll disabled')

    def deleteCalibrationRow(self):
        indices = self.calibrationData.selectionModel().selectedRows()
        # Must delete in reverse order
        for each_row in reversed(sorted(indices)):
            self.calibrationData.removeRow(each_row.row())           

    def deleteSingleMeasurementRow(self):
        indices = self.singleMeasurements.selectionModel().selectedRows()

        # Must delete in reverse order
        for each_row in reversed(sorted(indices)):
            self.singleMeasurements.removeRow(each_row.row())

    def deleteContiMeasurementRow(self):
        indices = self.contiMeasurements.selectionModel().selectedRows()

        # Must delete in reverse order
        for each_row in reversed(sorted(indices)):
            self.contiMeasurements.removeRow(each_row.row())

    @QtCore.pyqtSlot(bool)
    def startContinuousMeasurement(self, checked):
        self.buttonStartContinuousMeasurement.setText("Stop Continuous Measurement" if checked else "Start Continuous Measurement")
        if checked:
            print(self.updateFrequency)
            self.contiMeasurementTimer = QtCore.QTimer()
            self.contiMeasurementTimer.setInterval(self.updateFrequency)
            self.contiMeasurementTimer.timeout.connect(self.addContinuousMeasurement)
            self.contiMeasurementTimer.start()
            self.notifications.appendPlainText('>Continuous Measurement started')
        else:   
            self.contiMeasurementTimer.stop()
            self.buttonStartContinuousMeasurement.setChecked(False)
            self.notifications.appendPlainText('>Continuous Measurement stopped')

    def setUpdateFrequency(self):
        self.updateFrequency = int(self.customUpdateFrequency.text())
        print(self.updateFrequency)
     
    def calibrationPoint_1(self):
        self.calPoint_1_HighValue.setText(self.nr_u_high.text())
        self.calPoint_1_MidValue.setText(self.nr_u_mid.text())
        self.measurement_u_high_1 = self.u_high
        self.measurement_u_mid_1 = self.u_mid
        self.notifications.appendPlainText('>calibration point 1 set')

    def calibrationPoint_2(self):
        self.calPoint_2_HighValue.setText(self.nr_u_high.text())
        self.calPoint_2_MidValue.setText(self.nr_u_mid.text())
        self.measurement_u_high_2 = self.u_high
        self.measurement_u_mid_2 = self.u_mid
        self.notifications.appendPlainText('>calibration point 2 set')

    def calibrationPoint_3(self):
        self.calPoint_3_HighValue.setText(self.nr_u_high.text())
        self.calPoint_3_MidValue.setText(self.nr_u_mid.text())
        self.measurement_u_high_3 = self.u_high
        self.measurement_u_mid_3 = self.u_mid
        self.notifications.appendPlainText('>calibration point 3 set')

    def calibrate(self):
        self.refCon_1 = float(self.refPoint_1.text())
        self.refCon_2 = float(self.refPoint_2.text())
        self.refCon_3 = float(self.refPoint_3.text())
        self.u_high_cal = [self.measurement_u_high_1, self.measurement_u_high_2, self.measurement_u_high_3]
        print(self.u_high_cal)
        self.u_mid_cal = [self.measurement_u_mid_1, self.measurement_u_mid_2, self.measurement_u_mid_3]
        print(self.u_mid_cal)
        self.ref_con = [self.refCon_1, self.refCon_2, self.refCon_3]
        print(self.ref_con)
        self.conductance_cal= np.zeros(3)
        self.cell_constant_cal = np.zeros(3)

        for i in range(len(self.conductance_cal)):
            self.conductance_cal[i]= 1/(self.u_mid_cal[i]*self.ref_res/(self.u_high_cal[i]-self.u_mid_cal[i]))*1000
            self.cell_constant_cal[i] = self.ref_con[i]/self.conductance_cal[i]
        print(self.conductance_cal)
        print(self.cell_constant_cal)
        self.cal_data_func = np.polyfit(self.conductance_cal, self.cell_constant_cal, 1)
        print(self.cal_data_func)
        self.m = self.cal_data_func[0]
        self.b = self.cal_data_func[1]
        self.calFunction_m.setText(str(self.cal_data_func[0]))
        self.calFunction_b.setText(str(self.cal_data_func[1]))
        self.R2 = round(np.corrcoef(self.conductance_cal, self.cell_constant_cal)[0,1]**2,2)
        self.R_squared.setText(str(self.R2))
        self.notifications.appendPlainText('>conductivity sensor calibrated')
    def resetCalibration(self):
        self.calPoint_1_HighValue.setText(str(0))
        self.calPoint_1_MidValue.setText(str(0))
        self.calPoint_2_HighValue.setText(str(0))
        self.calPoint_2_MidValue.setText(str(0))
        self.calPoint_3_HighValue.setText(str(0))
        self.calPoint_3_MidValue.setText(str(0))
        self.calFunction_m.setText(str(0))
        self.calFunction_b.setText(str(0))
        self.refPoint_1.setText(str(0))
        self.refPoint_2.setText(str(0))
        self.refPoint_3.setText(str(0))
        self.R_squared.setText(str(0))
        self.notifications.appendPlainText('>calibration data resetted')
    
    def calibrateRTD(self):
        A  = 3.9083e-3
        B  = -5.775e-7
        R  = self.RTDValue
        R0 = self.R0
        C  = (R0-R)/(R0*B)
        F1 = A/2/B
        F2 = F1**2-C
        self.Temperature = -F1 - np.sqrt(F2)
        self.nr_temperature.setText(str(round(self.Temperature,2)))

    def clc_res(self):
        self.res = self.u_mid*self.ref_res/(self.u_high-self.u_mid)
        return self.res 
    
    def clc_cond(self):
        self.cond = 1/self.res*1000
        return self.cond

    def clc_conductivity(self):
        self.cell_constant = self.cond*self.m + self.b
        self.conductivity = self.cond*self.cell_constant
        self.nr_conductivity.setText(str(round(self.conductivity,3)))  
        self.compensateTemperature()
    
    def set_ref_22(self):
        self.ref_res = 22
        self.notifications.appendPlainText('>reference resistance set to 22 Ohm')

    def set_ref_200(self):
        self.ref_res = 200
        self.notifications.appendPlainText('>reference resistance set to 200 Ohm')
    
    def set_ref_2000(self):
        self.ref_res = 2000        
        self.notifications.appendPlainText('>reference resistance set to 2k Ohm')

    def setR0(self):
        self.R0=float(self.R_0_Value.text())

    def compensateTemperature(self):

        kappa=self.conductivity
        alpha=float(self.compensationCoefficient.text())
        T=self.Temperature
        kappa25 = 1/(1+alpha/100*(T-25))*kappa
        self.conductivityCompensated = kappa25
        self.nr_conductivityCompensated.setText(str(round(kappa25,2)))

    def loadCalibrationFromTable(self):
        self.calPoint_1_HighValue.setText(self.calibrationData.item(0,1).text())
        self.calPoint_1_MidValue.setText(self.calibrationData.item(0,2).text())
        self.refPoint_1.setText(self.calibrationData.item(0,5).text())
        self.measurement_u_high_1 = float(self.calibrationData.item(0,1).text())
        self.measurement_u_mid_1 = float(self.calibrationData.item(0,2).text())
        
        self.calPoint_2_HighValue.setText(self.calibrationData.item(1,1).text())
        self.calPoint_2_MidValue.setText(self.calibrationData.item(1,2).text())
        self.refPoint_2.setText(self.calibrationData.item(1,5).text())
        self.measurement_u_high_2 = float(self.calibrationData.item(1,1).text())
        self.measurement_u_mid_2 = float(self.calibrationData.item(1,2).text())       
        
        self.calPoint_3_HighValue.setText(self.calibrationData.item(2,1).text())
        self.calPoint_3_MidValue.setText(self.calibrationData.item(2,2).text())
        self.refPoint_3.setText(self.calibrationData.item(2,5).text())
        self.measurement_u_high_3 = float(self.calibrationData.item(2,1).text())
        self.measurement_u_mid_3 = float(self.calibrationData.item(2,2).text())
        self.notifications.appendPlainText('>calibration data imported...\n ...please set the reference resistance\n ...according to the table before calibration!')
if __name__=='__main__':

    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("windowsvista")
    window = MainWindow()
    window.show()
    app.exec_()
