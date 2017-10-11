#!/usr/bin python 
import tkinter as tk
import serial
import csv
import numpy as np
import matplotlib.pyplot as plt
import tkinter.filedialog # Otherwise it won't compile to .exe
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import time
import serial.tools.list_ports


#1/4/2017
#Only UpSweeps
#4x4 support (Should be ablke to easily change to any array size by tweeking how 256 is split)
#variable array sizes
#add auto find ser
#Find prettier TkInter Module!!!!

class Application(tk.Frame):
	def __init__(self, master=None):
		"""Application initialization
		"""
		tk.Frame.__init__(self, master)
		try: 
			self.ser=serial.Serial('/dev/ttyUSB0', 115200, timeout=20, parity = serial.PARITY_NONE) #Keithley serial port - COM4: Deskotp, COM5: Laptop
		except:
			print("No serial port for keithley")
		try: 
			self.ser1=serial.Serial('/dev/ttyACM0', 9600, timeout=10, parity = serial.PARITY_NONE) #Arduino serial port
		except:
			print("No serial port for arduino")
##		ArduinoPorts = [
##			p.device
##			for p in serial.tools.list_ports.comports()
##				
##			if 'Arduino' in p.description
##		]
##		KeithleyPorts = [
##			p.device
##			for p in serial.tools.list_ports.comports()
##				
##			if 'USB-Serial' in p.description
##		]
##		print(KeithleyPorts)
##		
##		if len(KeithleyPorts) > 0:
##			self.ser=serial.Serial(KeithleyPorts[0], 115200, timeout=10, parity = serial.PARITY_NONE) #Keithley serial port - COM4: Desktop, COM5: Laptop
##			print("Keithley is on " + str(KeithleyPorts[0]))
##		else:
##			print("No serial port for Keithley")
##		if len(ArduinoPorts) > 0: 
##			self.ser1=serial.Serial(ArduinoPorts[0], 9600, timeout=10, parity = serial.PARITY_NONE) #Arduino serial port
##			print("Arduino is on " + str(ArduinoPorts[0]))
##		else:
##			print("No serial port for Arduino")
##
##		ports = list(serial.tools.list_ports.comports())  #Print all ports in use
##		for p in ports:
##			print(p)
##			print(p.serial_number)
			
		self.fig = plt.Figure(figsize=(7, 6), dpi=100)
		self.fig.suptitle("I-V Sweep")
		self.a = self.fig.add_subplot(111)
		self.a.grid(b=True, which='major', color='r', linestyle='--')

		
		self.start = tk.DoubleVar()
		self.start.set(0.0)
		self.stop = tk.DoubleVar()
		self.stop.set(0.5)
		self.steps = tk.IntVar()
		self.steps.set(100)
		self.compliance = tk.DoubleVar()
		self.compliance.set(0.005)
		self.delay = tk.DoubleVar()
		self.delay.set(0.1)
		self.NPLC = tk.DoubleVar()
		self.NPLC.set(0.05)
		self.loops = tk.IntVar()
		self.loops.set(1)
		self.loopStep = tk.DoubleVar()
		self.loopStep.set(0)
		self.loopComplete = tk.DoubleVar()
		self.loopComplete.set(0)
		self.loopCompleteInt = tk.IntVar()
		self.loopCompleteInt.set(0)
		self.loopCount = tk.IntVar()
		self.loopCount.set(1)
		self.delayLoop = tk.DoubleVar()
		self.delayLoop.set(0.01)
		self.QuadCount = tk.IntVar()
		self.QuadCount.set(0)
		self.filenamenumber = tk.IntVar()
		self.filenamenumber.set(0)
		self.filename = tk.StringVar()
		self.filename.set("Sweep_")
		self.filenametext = tk.StringVar()
		self.setfilename()
		self.modes = tk.IntVar()
		self.modes.set(0)
		self.QUADmode = tk.IntVar()
		self.QUADmode.set(0)
		self.holdMode = tk.IntVar()
		self.holdMode.set(0)

		#Graph Variables
		self.XStart = tk.DoubleVar()
		self.XStart.set(0.0)
		self.XStop = tk.DoubleVar()
		self.XStop.set(0.5)
		self.YStop = tk.DoubleVar()
		self.YStop.set(0.005)
		self.YStart = tk.DoubleVar()
		self.YStart.set(0)
		
		self.mux = tk.IntVar()
		self.mux.set(0)

		
		self.arrayRow = tk.IntVar()
		self.arrayRow.set(2)
		self.arrayColumn = tk.IntVar()
		self.arrayColumn.set(2)
		self.switchKey = tk.IntVar()
		self.switchKey.set(0)
		self.perStep = tk.DoubleVar()
		self.perStep.set(0)
		self.perComplete = tk.DoubleVar()
		self.perComplete.set(0)
		self.perCompleteInt = tk.IntVar()
		self.perCompleteInt.set(0)
		self.deviceNumber = tk.IntVar()
		self.deviceNumber.set(0)

		self.quadValue = tk.StringVar()
		self.quadValue.set("")
		self.quadState=tk.IntVar()
		
		self.quad1 = tk.BooleanVar()
		self.quad1.set(False)
		self.quad2 = tk.BooleanVar()
		self.quad2.set(False)
		self.quad3 = tk.BooleanVar()
		self.quad3.set(False)
		self.quad4 = tk.BooleanVar()
		self.quad4.set(False)
		
		self.quad5 = tk.BooleanVar()
		self.quad5.set(False)
		self.quad6 = tk.BooleanVar()
		self.quad6.set(False)
		self.quad7 = tk.BooleanVar()
		self.quad7.set(False)
		self.quad8 = tk.BooleanVar()
		self.quad8.set(False)
		
		self.quad9 = tk.BooleanVar()
		self.quad9.set(False)
		self.quad10 = tk.BooleanVar()
		self.quad10.set(False)
		self.quad11 = tk.BooleanVar()
		self.quad11.set(False)
		self.quad12 = tk.BooleanVar()
		self.quad12.set(False)
		
		self.quad13 = tk.BooleanVar()
		self.quad13.set(False)
		self.quad14 = tk.BooleanVar()
		self.quad14.set(False)
		self.quad15 = tk.BooleanVar()
		self.quad15.set(False)
		self.quad16 = tk.BooleanVar()
		self.quad16.set(False)
		self.columnconfigure(0, pad = 2)
		self.createWidgets()
		self.grid()

	def createWidgets(self):
		self.fileFrame = tk.Frame()
		self.filenameLabel = tk.Label(text = "File Name: ")
		self.filenameLabel.grid(row = 0, column = 0, sticky = tk.W, padx = 5, pady = 5, in_ = self.fileFrame)
		self.filenameEntry = tk.Entry(textvariable = self.filename)
		self.filenameEntry.grid(row = 0, column = 1, sticky = tk.W, padx = 5, pady = 5, in_ = self.fileFrame)
		self.filenamenumberEntry = tk.Entry(textvariable = self.filenamenumber, width = 3, justify = tk.RIGHT)
		self.filenamenumberEntry.grid(row = 0, column = 2, sticky = tk.W, padx = 5, pady = 5, in_ = self.fileFrame)
		self.setButton = tk.Button(self.fileFrame, text='Set', command=self.setfilename)
		self.setButton.grid(row = 0, column = 3, sticky = tk.W)
		self.saveToLabel = tk.Label(text = "Next: ")
		self.saveToLabel.grid(row = 1, column = 0, sticky = tk.W, padx = 5, pady = 5, in_ = self.fileFrame)
		self.saveToLabelName = tk.Label(textvariable = self.filenametext)
		self.saveToLabelName.grid(row = 1, column = 1, sticky = tk.W, padx = 5, pady = 5, in_ = self.fileFrame)
		self.fileFrame.grid(row = 0, column = 0, sticky = tk.W + tk.N, padx = 5, pady = 5, in_ = self)
		
		self.infoFrame = tk.Frame()
		self.loopCountLabel = tk.Label(text = "Loop:")
		self.loopCountLabel.grid(row = 0, column = 0, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.infoFrame)
		
		self.loopCountVar = tk.Label(textvariable = self.loopCount)
		self.loopCountVar.grid(row = 0, column = 1, in_ = self.infoFrame)

		self.perCompleteLabel = tk.Label(text = "Permutation Complete:")
		self.perCompleteLabel.grid(row = 0, column = 2, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.infoFrame)
		
		self.perCompleteVar = tk.Label(textvariable = self.perCompleteInt)
		self.perCompleteVar.grid(row = 0, column = 3, in_ = self.infoFrame)

		self.per1Label = tk.Label(text = "%")
		self.per1Label.grid(row = 0, column = 4, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.infoFrame)

		self.loopCompleteLabel = tk.Label(text = "Loop Complete:")
		self.loopCompleteLabel.grid(row = 0, column = 5, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.infoFrame)
		
		self.loopCompleteVar = tk.Label(textvariable = self.loopCompleteInt)
		self.loopCompleteVar.grid(row = 0, column = 6, in_ = self.infoFrame)

		self.per2Label = tk.Label(text = "%")
		self.per2Label.grid(row = 0, column = 7, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.infoFrame)
		
		self.infoFrame.grid(row = 0, column = 1, in_ = self)
		
		self.settingsFrame = tk.Frame()
		self.startLabel = tk.Label(text = "START(V)")
		self.startLabel.grid(row = 0, column = 0, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.settingsFrame)
		self.stopLabel = tk.Label(text = "STOP(V)")
		self.stopLabel.grid(row = 0, column = 1, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.settingsFrame)
		self.stepsLabel = tk.Label(text = "STEPS(#)")
		self.stepsLabel.grid(row = 0, column = 2, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.settingsFrame)
		self.complianceLabel = tk.Label(text = "COMP.(A)")
		self.complianceLabel.grid(row = 0, column = 3, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.settingsFrame)
		self.delayLabel = tk.Label(text = "DELAY(s)")
		self.delayLabel.grid(row = 0, column = 4, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.settingsFrame)
		self.loopsLabel = tk.Label(text = "LOOPS(#)")
		self.loopsLabel.grid(row = 0, column = 5, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.settingsFrame)
		self.startEntry = tk.Entry(textvariable = self.start, width = 6, justify = tk.RIGHT)
		self.startEntry.grid(row = 1, column = 0, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.settingsFrame)
		self.stopEntry = tk.Entry(textvariable = self.stop, width = 6, justify = tk.RIGHT)
		self.stopEntry.grid(row = 1, column = 1, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.settingsFrame)
		self.stepsEntry = tk.Entry(textvariable = self.steps, width = 6, justify = tk.RIGHT)
		self.stepsEntry.grid(row = 1, column = 2, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.settingsFrame)
		self.complianceEntry = tk.Entry(textvariable = self.compliance, width = 6, justify = tk.RIGHT)
		self.complianceEntry.grid(row = 1, column = 3, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.settingsFrame)
		self.delayEntry = tk.Entry(textvariable = self.delay, width = 6, justify = tk.RIGHT)
		self.delayEntry.grid(row = 1, column = 4, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.settingsFrame)
		self.loopsEntry = tk.Entry(textvariable = self.loops, width = 6, justify = tk.RIGHT)
		self.loopsEntry.grid(row = 1, column = 5, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.settingsFrame)
		self.settingsFrame.grid(row = 1, column = 0, sticky = tk.W + tk.N, padx = 5, pady = 5, in_ = self)

		self.SweepsettingsFrame = tk.Frame()
		self.delayLoopLabel = tk.Label(text = "S.Delay(s)")
		self.delayLoopLabel.grid(row = 2, column = 0, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.settingsFrame)
		self.delayLoopEntry = tk.Entry(textvariable = self.delayLoop, width = 6, justify = tk.RIGHT)
		self.delayLoopEntry.grid(row = 3, column = 0, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.settingsFrame)
		self.NPLCLabel = tk.Label(text = "NPLC")
		self.NPLCLabel.grid(row = 2, column = 1, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.settingsFrame)
		self.NPLCEntry = tk.Entry(textvariable = self.NPLC, width = 6, justify = tk.RIGHT)
		self.NPLCEntry.grid(row = 3, column = 1, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.settingsFrame)
		self.SweepsettingsFrame.grid(row = 1, column = 0, sticky = tk.W + tk.N, padx = 5, pady = 5, in_ = self)
		
		self.GraphsettingsFrame = tk.Frame()
		self.YStartLabel = tk.Label(text = "Y Start")
		self.YStartLabel.grid(row = 0, column = 0, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.GraphsettingsFrame)
		self.YStartEntry = tk.Entry(textvariable = self.YStart, width = 6, justify = tk.RIGHT)
		self.YStartEntry.grid(row = 1, column = 0, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.GraphsettingsFrame)
		self.YStopLabel = tk.Label(text = "Y Stop")
		self.YStopLabel.grid(row = 0, column = 1, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.GraphsettingsFrame)
		self.YStopEntry = tk.Entry(textvariable = self.YStop, width = 6, justify = tk.RIGHT)
		self.YStopEntry.grid(row = 1, column = 1, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.GraphsettingsFrame)
		self.XStartLabel = tk.Label(text = "X Start")
		self.XStartLabel.grid(row = 0, column = 2, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.GraphsettingsFrame)
		self.XStartEntry = tk.Entry(textvariable = self.XStart, width = 6, justify = tk.RIGHT)
		self.XStartEntry.grid(row = 1, column = 2, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.GraphsettingsFrame)
		self.XStopLabel = tk.Label(text = "X Stop")
		self.XStopLabel.grid(row = 0, column = 3, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.GraphsettingsFrame)
		self.XStopEntry = tk.Entry(textvariable = self.XStop, width = 6, justify = tk.RIGHT)
		self.XStopEntry.grid(row = 1, column = 3, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.GraphsettingsFrame)
		self.GraphsettingsFrame.grid(row = 2, column = 0, sticky = tk.W + tk.N, padx = 5, pady = 5, in_ = self)

		
		self.sweepModeFrame = tk.Frame()
		self.stairRadio = tk.Radiobutton(self.sweepModeFrame, text ="Staircase sweep", variable = self.modes, value = 0)
		self.stairRadio.grid(row = 0, column = 0, sticky = tk.W)
		self.pulsedRadio = tk.Radiobutton(self.sweepModeFrame, text ="Pulsed staircase sweep", variable = self.modes, value = 1)
		self.pulsedRadio.grid(row = 0, column = 1, sticky = tk.W)
		self.sweepModeFrame.grid(row = 3, column = 0, sticky = tk.W + tk.N, padx = 5, pady = 5, in_ = self)
		
		self.figureCanvas = FigureCanvasTkAgg(self.fig, master=self)
		self.figureCanvas.get_tk_widget().grid(row = 1, column = 1, columnspan = 15, rowspan = 15, sticky = tk.N, in_ = self)
		
		self.ARRAYFrame = tk.Frame()
		self.ARRAYLabel = tk.Label(text = "Array Size")
		self.ARRAYLabel.grid(row = 0, column = 0, sticky = tk.W+tk.E, in_ = self.ARRAYFrame)
		self.ArrayLabel1 = tk.Label(text = " Rows ")
		self.ArrayLabel1.grid(row = 1 , column = 0, sticky = tk.W, in_ = self.ARRAYFrame)
		self.ARRAYCheck0 = tk.Checkbutton(self.ARRAYFrame, text ="1", variable = self.arrayRow, offvalue = 0, onvalue = 1, command=self.ARRAYsize)
		self.ARRAYCheck0.grid(row = 1, column = 1, sticky = tk.W)
		self.ARRAYCheck1 = tk.Checkbutton(self.ARRAYFrame, text ="2", variable = self.arrayRow, offvalue = 0, onvalue = 2, command=self.ARRAYsize)
		self.ARRAYCheck1.grid(row = 1, column = 2, sticky = tk.W)
		self.ARRAYCheck2 = tk.Checkbutton(self.ARRAYFrame, text ="3", variable = self.arrayRow, offvalue = 0, onvalue = 3, command=self.ARRAYsize)
		self.ARRAYCheck2.grid(row = 1, column = 3, sticky = tk.W)       
		self.ARRAYCheck3 = tk.Checkbutton(self.ARRAYFrame, text ="4", variable = self.arrayRow, offvalue = 0, onvalue = 4, command=self.ARRAYsize)
		self.ARRAYCheck3.grid(row = 1, column = 4, sticky = tk.W)
		self.ArrayLabel2 = tk.Label(text = "Columns ")
		self.ArrayLabel2.grid(row = 2 , column = 0, sticky = tk.W, in_ = self.ARRAYFrame)
		self.ARRAYCheck5 = tk.Checkbutton(self.ARRAYFrame, text ="1", variable = self.arrayColumn, offvalue = 0, onvalue = 1, command=self.ARRAYsize)
		self.ARRAYCheck5.grid(row = 2, column = 1, sticky = tk.W)
		self.ARRAYCheck6 = tk.Checkbutton(self.ARRAYFrame, text ="2", variable = self.arrayColumn, offvalue = 0, onvalue = 2, command=self.ARRAYsize)
		self.ARRAYCheck6.grid(row = 2, column = 2, sticky = tk.W)
		self.ARRAYCheck7 = tk.Checkbutton(self.ARRAYFrame, text ="3", variable = self.arrayColumn, offvalue = 0, onvalue = 3, command=self.ARRAYsize)
		self.ARRAYCheck7.grid(row = 2, column = 3, sticky = tk.W)
		self.ARRAYCheck8 = tk.Checkbutton(self.ARRAYFrame, text ="4", variable = self.arrayColumn, offvalue = 0, onvalue = 4, command=self.ARRAYsize)
		self.ARRAYCheck8.grid(row = 2, column = 4, sticky = tk.W)
		self.ARRAYFrame.grid(row = 4, column = 0, in_ = self) 

		self.QUADAutoFrame = tk.Frame()
		self.QuadAutoOff = tk.Radiobutton(self.QUADAutoFrame, text ="AutoRunOff", variable = self.QUADmode, value = 0)
		self.QuadAutoOff.grid(row = 0, column = 0, sticky = tk.W)
		self.QuadAutoOn = tk.Radiobutton(self.QUADAutoFrame, text ="AutoRunOn", variable = self.QUADmode, value = 1)
		self.QuadAutoOn.grid(row = 0, column = 1, sticky = tk.W)
		self.QUADAutoFrame.grid(row = 5, column = 0, sticky = tk.W + tk.N, padx = 5, pady = 5, in_ = self)
		
		self.QUADFrame = tk.Frame()
		self.QUADLabel = tk.Label(text = "Arduino: ")
		self.QUADLabel.grid(row = 0, column = 0, sticky = tk.W+tk.E, in_ = self.QUADFrame)
		self.QUADCheck1 = tk.Checkbutton(self.QUADFrame, text ="A0", variable = self.quad1, offvalue = False, onvalue = True, command=self.QUADserial)
		self.QUADCheck1.grid(row = 1, column = 1, sticky = tk.W)
		self.QUADCheck2 = tk.Checkbutton(self.QUADFrame, text ="A1", variable = self.quad2, offvalue = False, onvalue = True, command=self.QUADserial)
		self.QUADCheck2.grid(row = 2, column = 1, sticky = tk.W)
		self.QUADCheck3 = tk.Checkbutton(self.QUADFrame, text ="A2", variable = self.quad3, offvalue = False, onvalue = True, command=self.QUADserial)
		self.QUADCheck3.grid(row = 3, column = 1, sticky = tk.W)
		self.QUADCheck4 = tk.Checkbutton(self.QUADFrame, text ="A3", variable = self.quad4, offvalue = False, onvalue = True, command=self.QUADserial)
		self.QUADCheck4.grid(row = 4, column = 1, sticky = tk.W)

		self.QUADCheck5 = tk.Checkbutton(self.QUADFrame, text ="B0", variable = self.quad5, offvalue = False, onvalue = True, state=tk.DISABLED, command=self.QUADserial)
		self.QUADCheck5.grid(row = 1, column = 2, sticky = tk.W)
		self.QUADCheck6 = tk.Checkbutton(self.QUADFrame, text ="B1", variable = self.quad6, offvalue = False, onvalue = True, state=tk.DISABLED, command=self.QUADserial)
		self.QUADCheck6.grid(row = 2, column = 2, sticky = tk.W)
		self.QUADCheck7 = tk.Checkbutton(self.QUADFrame, text ="B2", variable = self.quad7, offvalue = False, onvalue = True, state=tk.DISABLED, command=self.QUADserial)
		self.QUADCheck7.grid(row = 3, column = 2, sticky = tk.W)
		self.QUADCheck8 = tk.Checkbutton(self.QUADFrame, text ="B3", variable = self.quad8, offvalue = False, onvalue = True, state=tk.DISABLED, command=self.QUADserial)
		self.QUADCheck8.grid(row = 4, column = 2, sticky = tk.W)

		self.QUADCheck9 = tk.Checkbutton(self.QUADFrame, text ="C0", variable = self.quad9, offvalue = False, onvalue = True, state=tk.DISABLED, command=self.QUADserial)
		self.QUADCheck9.grid(row = 1, column = 3, sticky = tk.W)
		self.QUADCheck10 = tk.Checkbutton(self.QUADFrame, text ="C1", variable = self.quad10, offvalue = False, onvalue = True, state=tk.DISABLED, command=self.QUADserial)
		self.QUADCheck10.grid(row = 2, column = 3, sticky = tk.W)
		self.QUADCheck11 = tk.Checkbutton(self.QUADFrame, text ="C2", variable = self.quad11, offvalue = False, onvalue = True, state=tk.DISABLED, command=self.QUADserial)
		self.QUADCheck11.grid(row = 3, column = 3, sticky = tk.W)
		self.QUADCheck12 = tk.Checkbutton(self.QUADFrame, text ="C3", variable = self.quad12, offvalue = False, onvalue = True, state=tk.DISABLED, command=self.QUADserial)
		self.QUADCheck12.grid(row = 4, column = 3, sticky = tk.W)

		self.QUADCheck13 = tk.Checkbutton(self.QUADFrame, text ="D0", variable = self.quad13, offvalue = False, onvalue = True, state=tk.DISABLED, command=self.QUADserial)
		self.QUADCheck13.grid(row = 1, column = 4, sticky = tk.W)
		self.QUADCheck14 = tk.Checkbutton(self.QUADFrame, text ="D1", variable = self.quad14, offvalue = False, onvalue = True, state=tk.DISABLED, command=self.QUADserial)
		self.QUADCheck14.grid(row = 2, column = 4, sticky = tk.W)
		self.QUADCheck15 = tk.Checkbutton(self.QUADFrame, text ="D2", variable = self.quad15, offvalue = False, onvalue = True, state=tk.DISABLED, command=self.QUADserial)
		self.QUADCheck15.grid(row = 3, column = 4, sticky = tk.W)
		self.QUADCheck16 = tk.Checkbutton(self.QUADFrame, text ="D3", variable = self.quad16, offvalue = False, onvalue = True, state=tk.DISABLED, command=self.QUADserial)
		self.QUADCheck16.grid(row = 4, column = 4, sticky = tk.W)
		
		self.QUADFrame.grid(row = 6, column = 0, in_ = self)
		
		self.holdModeFrame = tk.Frame()
		self.holdOffRadio = tk.Radiobutton(self.holdModeFrame, text ="Hold Off", variable = self.holdMode, value = 0)
		self.holdOffRadio.grid(row = 0, column = 0, sticky = tk.W)
		self.HoldOnRadio = tk.Radiobutton(self.holdModeFrame, text ="Hold On", variable = self.holdMode, value = 1)
		self.HoldOnRadio.grid(row = 0, column = 1, sticky = tk.W)
		self.holdModeFrame.grid(row = 7, column = 0, sticky = tk.W + tk.N, padx = 5, pady = 5, in_ = self)

		self.buttonsFrame = tk.Frame()
		self.goButton = tk.Button(self.buttonsFrame, text='GO!', command=self.go)
		self.goButton.grid(row = 0, column = 2)
		self.quitButton = tk.Button(self.buttonsFrame, text='Quit', command=self.quit)
		self.quitButton.grid(row = 0, column = 4)
		self.buttonsFrame.grid(row = 8, column = 0, in_ = self)
	
	def setfilename(self):
		self.filenametext.set(self.filename.get()+str(self.filenamenumber.get()))
		print(self.filenametext.get())
	
	def configSweep(self):
		"""Configure Keithley 2400 SMU to perform voltage sweeps
		Takes the following arguments: 
		-ser: Serial port
		-start: Starting point of the voltage sweep (in volts)
		-stop: Ending point of the voltage sweep (in volts)
		-steps: Number of steps in the sweep
		-compliance: Current compliance (in amperes)
		-delay: Delay between points (in seconds)
		"""
		self.ser.write("smua.reset()\n".encode())       #Reset SMU
		self.ser.write("smua.nvbuffer2.clear()\n".encode())
		self.ser.write("smua.nvbuffer2.collectsourcevalues = 1\n".encode())
		self.ser.write("errorqueue.clear()\n".encode())
		self.ser.write("display.screen = display.SMUA\n".encode())              
		self.ser.write("display.smua.measure.func = display.MEASURE_DCAMPS\n".encode())         
		self.ser.write("format.data = format.ASCII\n".encode())
		self.ser.write("beeper.enable = beeper.OFF \n".encode())        #Turn off beeper               
		self.ser.write("smua.sense = smua.SENSE_LOCAL \n".encode())     #Sense current (DC)
		self.ser.write("smua.trigger.measure.i(smua.nvbuffer2)\n".encode())
		self.ser.write(("smua.source.limiti = "+str(self.compliance.get())+"\n").encode())      #Set compliance (A)
		self.ser.write(("smua.measure.nplc = "+str(self.NPLC.get())+"\n").encode())
		self.ser.write(("smua.trigger.source.linearv("+str(self.start.get())+","+str(self.stop.get())+","+str(self.steps.get()+1)+")\n" ).encode()) #Set sweep start point (V), stop point (V) and steps 
		self.ser.write("smua.trigger.endsweep.action = smua.SOURCE_IDLE\n".encode())
		self.ser.write("smua.trigger.source.action = smua.ENABLE\n".encode())   #Change to sweep mode
		self.ser.write("smua.source.autorangev = smua.AUTORANGE_ON \n".encode())        #Set source range AUTO/BEST/FIXED
		self.ser.write(("smua.nvbuffer2.fillcount = "+str(self.steps.get()+1)+"\n").encode())   #Set amount of points to store in memory (steps + 1)
		self.ser.write(("smua.measure.delay = "+str(self.delay.get())+"\n").encode())   #Set delay
		self.ser.write(("smua.trigger.count = "+str(self.steps.get()+1)+"\n").encode())
		

	def configCustomSweep(self):
		"""Configure Keithley 2400 SMU to perform voltage sweeps
		Takes the following arguments: 
		-ser: Serial port
		-start: Starting point of the voltage sweep (in volts)
		-stop: Ending point of the voltage sweep (in volts)
		-steps: Number of steps in the sweep
		-compliance: Current compliance (in amperes)
		-delay: Delay between points (in seconds)
		"""
		stepsize = (self.stop.get()-self.start.get())/self.steps.get()
		customSweepList = str(self.start.get())
		for ii in range(1, self.steps.get() + 1, 1):
			if ii % 2 == 0:
				customSweepList = customSweepList + "," + str(self.start.get() + ii * stepsize)
			else:
				customSweepList = customSweepList + ",0"
		self.ser.write("smua.reset()\n".encode())	#Reset SMU
		self.ser.write("beeper.enable = beeper.OFF \n".encode())	#Turn off beeper
		self.ser.write(":smua.source.func = smua.OUTPUT_DCVOLTS\n".encode())	#Source Voltage
		self.ser.write("smua.sense = smua.SENSE_LOCAL \n".encode())	#Sense current (DC)
		self.ser.write(("smua.source.limiti = "+str(self.compliance.get())+"\n").encode())	#Set compliance (A)
		self.ser.write("smua.measure.nplc = 0.05\n".encode())
		self.ser.write(":SOUR:VOLT:MODE LIST\n".encode())	#Sweep mode: list
		self.ser.write((":SOUR:LIST:VOLT "+customSweepList+"\n").encode())	#List of values
		self.ser.write(("defbuffer1.fillcount = "+str(self.steps.get())+"\n").encode())	#Set amount of points to store in memory (steps + 1)
		self.ser.write(("smua.measure.delay =  "+str(self.delay.get())+"\n").encode())	#Set delay		

	def runSweep(self):
		"""Orders the SMU to perform the previously configured sweep. Only takes the serial port as argument.
		"""
		
		self.ser.write("smua.source.output = smua.OUTPUT_ON\n".encode())
		self.ser.write("smua.trigger.measure.action = smua.ENABLE\n".encode())
		self.ser.write("smua.trigger.initiate()\n".encode())
		
	def recoverData(self, data):
		"""Converts the binary data stream acquired from the SMU into a 2-column human-readable list containing voltage and current (as string lists)
		for ease of manipulation and its later conversion into csv files.
		"""
		datacsv=csv.reader(data.decode().split(','))            #Convert binary data into a csv structure containing strings, and split using the commas (,) as separators
		list=[]                                                 #Empty list that will temporarily keep the extracted data (it comes as series of 5 values V,I,?,?,?)
		results=[[],[]]                                         #Empty list that will store the data as [[V1, V2..., Vn],[I1,I2,...,In]]
		for row in datacsv:
			list.append(row)                                #Extract data from the csv structure into list
		for ii in range(0, self.steps.get()+1):
			for jj in range(0,2):
				results[jj].append(list.pop(0).pop())   #Extract the first two values of each serias (V,I) into results
		return results
	
	def joinData(self, data1, data2):
		"""Function that merges #Graph Variables
		self.XStart = tk.DoubleVar()
		self.XStart.set(0.0)
		self.XStop = tk.DoubleVar()
		self.XStop.set(0.5)
		self.YStop = tk.DoubleVar()
		self.YStop.set(0.005)
		self.YStart = tk.DoubleVar()
		self.YStart.set(-self.YStop.get())two differents sets of data so they can be exported into a single file
		"""
		for ii in range(0, len(data2)): 
			data1.append(data2[ii])	#Append the second set of data to the former one
		return data1
	
	def exportFile(self, dataToExport):
		with open(self.filenametext.get()+".txt", 'wt') as csvfile:
			writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_NONE)
			array = np.asarray(dataToExport).T.tolist()
			#print(array)
			for ii in range(0, self.steps.get()):
				writer.writerow(array[ii])
	
	def loopSweeps(self):
		dataArray = []
		for l in range(0,self.loops.get()):
			self.loopCount.set(l + 1)
			self.runSweep()
			self.ser.write(("x = printbuffer(1,"+str(self.steps.get()+1)+",smua.nvbuffer2.sourcevalues, smua.nvbuffer2.readings)\n").encode())
			self.ser.write("waitcomplete(0)\n".encode())
			output = self.recoverData(self.ser.readline())
			self.plotCurve(output)
			self.loopComplete.set(self.loopComplete.get() + self.loopStep.get())
			self.loopCompleteInt.set(int(self.loopComplete.get()))
			dataArray = self.joinData(dataArray, output)
			self.ser.write("smua.source.output = smua.OUTPUT_OFF\n".encode())
			time.sleep(self.delayLoop.get())
			if self.holdMode.get() == 0:
				self.a.hold(False)
			elif self.holdMode.get() == 1:
				self.a.hold(True)
		self.ser.write("smua.source.output = smua.OUTPUT_OFF\n".encode())
		self.loopComplete.set(0)
		return dataArray

	def loopSweeps1(self):
		dataArray = []
		for l in range(0,self.loops.get()):
			self.loopCount.set(l + 1)
			self.runSweep()
			self.ser.write(("x = printbuffer(1,"+str(self.steps.get()+1)+",smua.nvbuffer2.sourcevalues, smua.nvbuffer2.readings)\n").encode())
			self.ser.write("waitcomplete(0)\n".encode())
			output = self.recoverData(self.ser.readline())
			self.loopComplete.set(self.loopComplete.get() + self.loopStep.get())
			self.loopCompleteInt.set(int(self.loopComplete.get()))
			dataArray = self.joinData(dataArray, output)
			time.sleep(self.delayLoop.get())
			if self.holdMode.get() == 0:
				self.a.hold(False)
			elif self.holdMode.get() == 1:
				self.a.hold(True)
		self.ser.write("smua.source.output = smua.OUTPUT_OFF\n".encode())
		self.loopComplete.set(0)
		return dataArray
	
	def plotCurve(self, data):
		if self.modes.get() == 0:
			self.a.plot(data[0],data[1])
		elif self.modes.get() == 1:
			self.a.scatter(data[0],data[1])
		self.a.hold(True)
		self.a.grid(b=True, which='major', color='r', linestyle='--')
		self.a.axis([self.XStart.get(), self.XStop.get() , self.YStart.get() , self.YStop.get()])
		self.figureCanvas.show()
		plt.pause(0.001)
		self.update()
	
	def MUXserial(self):
		#self.ser1.write("OFF".encode())
		MUXAddress = self.mux.get()
		if MUXAddress == 0:
			self.ser1.write("C0B0A0".encode())
		elif MUXAddress == 1:
			self.ser1.write("C0B0A1".encode())
		elif MUXAddress == 2:
			self.ser1.write("C0B1A0".encode())
		elif MUXAddress == 3:
			self.ser1.write("C0B1A1".encode())
		elif MUXAddress == 4:
			self.ser1.write("C1B0A0".encode())
		elif MUXAddress == 5:
			self.ser1.write("C1B0A1".encode())
		elif MUXAddress == 6:
			self.ser1.write("C1B1A0".encode())
		elif MUXAddress == 7:
			self.ser1.write("C1B1A1".encode())
		#self.ser1.write("ON".encode())

	def ARRAYsize(self):

		"""Initialisation"""
		self.QUADCheck1.config(state=tk.NORMAL)
		self.QUADCheck2.config(state=tk.NORMAL)
		self.QUADCheck3.config(state=tk.NORMAL)
		self.QUADCheck4.config(state=tk.NORMAL)
		self.QUADCheck5.config(state=tk.NORMAL)
		self.QUADCheck6.config(state=tk.NORMAL)
		self.QUADCheck7.config(state=tk.NORMAL)
		self.QUADCheck8.config(state=tk.NORMAL)
		self.QUADCheck9.config(state=tk.NORMAL)
		self.QUADCheck10.config(state=tk.NORMAL)
		self.QUADCheck11.config(state=tk.NORMAL)
		self.QUADCheck12.config(state=tk.NORMAL)
		self.QUADCheck13.config(state=tk.NORMAL)
		self.QUADCheck14.config(state=tk.NORMAL)
		self.QUADCheck15.config(state=tk.NORMAL)
		self.QUADCheck16.config(state=tk.NORMAL)

		
		"""Rows"""
		if self.arrayRow.get() < 4:
			self.quad4.set(False)
			self.QUADCheck4.config(state=tk.DISABLED)
			self.quad8.set(False)
			self.QUADCheck8.config(state=tk.DISABLED)
			self.quad12.set(False)
			self.QUADCheck12.config(state=tk.DISABLED)
			self.quad16.set(False)
			self.QUADCheck16.config(state=tk.DISABLED)
			if self.arrayRow.get() < 3:
				self.quad3.set(False)
				self.QUADCheck3.config(state=tk.DISABLED)
				self.quad7.set(False)
				self.QUADCheck7.config(state=tk.DISABLED)
				self.quad11.set(False)
				self.QUADCheck11.config(state=tk.DISABLED)
				self.quad15.set(False)
				self.QUADCheck15.config(state=tk.DISABLED)
				if self.arrayRow.get() < 2:
					self.quad2.set(False)
					self.QUADCheck2.config(state=tk.DISABLED)
					self.quad6.set(False)
					self.QUADCheck6.config(state=tk.DISABLED)
					self.quad10.set(False)
					self.QUADCheck10.config(state=tk.DISABLED)
					self.quad14.set(False)
					self.QUADCheck14.config(state=tk.DISABLED)
					if self.arrayRow.get() < 1:
						self.quad1.set(False)
						self.QUADCheck1.config(state=tk.DISABLED)
						self.quad5.set(False)
						self.QUADCheck5.config(state=tk.DISABLED)
						self.quad9.set(False)
						self.QUADCheck9.config(state=tk.DISABLED)
						self.quad13.set(False)
						self.QUADCheck13.config(state=tk.DISABLED)
		"""Columns"""
		if self.arrayColumn.get() < 4:
			self.quad13.set(False)
			self.QUADCheck13.config(state=tk.DISABLED)
			self.quad14.set(False)
			self.QUADCheck14.config(state=tk.DISABLED)
			self.quad15.set(False)
			self.QUADCheck15.config(state=tk.DISABLED)
			self.quad16.set(False)
			self.QUADCheck16.config(state=tk.DISABLED)
			if self.arrayColumn.get() < 3:
				self.quad9.set(False)
				self.QUADCheck9.config(state=tk.DISABLED)
				self.quad10.set(False)
				self.QUADCheck10.config(state=tk.DISABLED)
				self.quad11.set(False)
				self.QUADCheck11.config(state=tk.DISABLED)
				self.quad12.set(False)
				self.QUADCheck12.config(state=tk.DISABLED)
				if self.arrayColumn.get() < 2:
					self.quad5.set(False)
					self.QUADCheck5.config(state=tk.DISABLED)
					self.quad6.set(False)
					self.QUADCheck6.config(state=tk.DISABLED)
					self.quad7.set(False)
					self.QUADCheck7.config(state=tk.DISABLED)
					self.quad8.set(False)
					self.QUADCheck8.config(state=tk.DISABLED)
					if self.arrayColumn.get() < 1:
						self.quad1.set(False)
						self.QUADCheck1.config(state=tk.DISABLED)
						self.quad2.set(False)
						self.QUADCheck2.config(state=tk.DISABLED)
						self.quad3.set(False)
						self.QUADCheck3.config(state=tk.DISABLED)
						self.quad4.set(False)
						self.QUADCheck4.config(state=tk.DISABLED)

		"""Maximum Permutations"""
		self.deviceNumber.set(self.arrayRow.get() * self.arrayColumn.get())
		self.switchKey.set(pow(self.arrayRow.get(),self.arrayColumn.get()))
		self.perStep.set(100/self.switchKey.get())
		print(self.switchKey.get())

	def QUADserialAuto(self,permutation):
		quadValue = ""
		colA = 0
		colB = 0
		colC = 0
		colD = 0
		columnA = ""
		columnB = ""
		columnC = ""
		columnD = ""
		
		if self.arrayColumn.get() > 3:
			colD = int(permutation / pow(self.arrayRow.get(),3))
			permutation = permutation - (colD * pow(self.arrayRow.get(),3))
			columnD = "D" + str(colD)
		if self.arrayColumn.get() > 2:
			colC = int(permutation / pow(self.arrayRow.get(),2))
			permutation = permutation - (colC * pow(self.arrayRow.get(),2))
			columnC = "C" + str(colC)
		if self.arrayColumn.get() > 1:                        
			colB = int(permutation / pow(self.arrayRow.get(),1))
			permutation = permutation - (colB * pow(self.arrayRow.get(),1))
			columnB = "B" + str(colB)
		if self.arrayColumn.get() > 0:                       
			colA = int(permutation / 1)
			columnA = "A" + str(colA)
					
		quadValue = columnA + columnB + columnC + columnD
		quadCode = 'Z' + quadValue
		
		print(quadValue)
		self.ser1.write(quadCode.encode())

		
	def QUADserial(self):
		quadValue = ""
		self.quadState.set(0)
		if self.quad1.get():
			quadValue = quadValue +"A0"
		if self.quad2.get():
			quadValue =  quadValue + "A1"
		if self.quad3.get():
			quadValue =  quadValue + "A2"
		if self.quad4.get():
			quadValue =  quadValue + "A3"
		if self.quad5.get():
			quadValue =  quadValue + "B0"
		if self.quad6.get():
			quadValue =  quadValue + "B1"
		if self.quad7.get():
			quadValue =  quadValue + "B2"
		if self.quad8.get():
			quadValue =  quadValue + "B3"
		if self.quad9.get():
			quadValue =  quadValue + "C0"
		if self.quad10.get():
			quadValue =  quadValue + "C1"
		if self.quad11.get():
			quadValue =  quadValue + "C2"
		if self.quad12.get():
			quadValue =  quadValue + "C3"
		if self.quad13.get():
			quadValue =  quadValue + "D0"
		if self.quad14.get():
			quadValue =  quadValue + "D1"
		if self.quad15.get():
			quadValue =  quadValue + "D2"
		if self.quad16.get():
			quadValue =  quadValue + "D3"			

		quadCode = 'Z' + quadValue
		print(quadValue)
		self.ser1.write(quadCode.encode())
	
	def go(self):
		self.loopStep.set(100/self.loops.get())
		self.perStep.set(100/self.switchKey.get())
		self.perComplete.set(0)
		self.configSweep()
		
		if self.holdMode.get() == 0:
			self.a.hold(False)
		elif self.holdMode.get() == 1:
			self.a.hold(True)
			
		if self.QUADmode.get() == 0:
			op=self.loopSweeps()
			self.exportFile(op)
			self.filenamenumber.set(1 + self.filenamenumber.get())
			self.setfilename()
		
		elif self.QUADmode.get() == 1:
			for p in range(0, self.switchKey.get()):
				self.a.hold(False)
				print(p)
				self.QUADserialAuto(p)
				time.sleep(5) #Enough time for Bilateral switches to active in the correct order
				op=self.loopSweeps1()
				print("Sweep Complete")
				self.perComplete.set(self.perComplete.get() + self.perStep.get())
				self.perCompleteInt.set(int(self.perComplete.get()))
				self.filenamenumber.set(p)
				self.setfilename()
				self.exportFile(op)
		
		
plt.ion()
app = Application()
app.master.title('Keithley 2400 Sweeper')
app.mainloop()


