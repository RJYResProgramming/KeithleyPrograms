#!/usr/bin python 
import tkinter as tk
import serial
import csv
import numpy as np
import matplotlib.pyplot as plt
import tkinter.filedialog # Otherwise it won't compile to .exe
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import time

#09/06/2016
#Remove the try-except?
#Add Enable/Disable Button for MUX and QUAD or re-address the ports in the arduino
#Version including the MUX and the QUAD SWITCH interfacing

#14/12/2016
#Only UpSweeps


class Application(tk.Frame):
	def __init__(self, master=None):
		"""Application initialization
		"""
		tk.Frame.__init__(self, master)
		try: 
			self.ser=serial.Serial('/dev/ttyUSB0', 115200, timeout=10, parity = serial.PARITY_NONE) #Keithley serial port - COM4: Deskotp, COM5: Laptop
		except:
			print("No serial port for keithley")
		try: 
			self.ser1=serial.Serial('/dev/ttyACM0', 9600, timeout=10, parity = serial.PARITY_NONE) #Arduino serial port
		except:
			print("No serial port for arduino")
		
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
		self.loops = tk.IntVar()
		self.loops.set(1)
		self.loopCount = tk.IntVar()
		self.loopCount.set(1)
		self.filenamenumber = tk.IntVar()
		self.filenamenumber.set(0)
		self.filename = tk.StringVar()
		self.filename.set("Sweep_")
		self.filenametext = tk.StringVar()
		self.setfilename()
		self.modes = tk.IntVar()
		self.modes.set(0)
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
		self.YStart.set(-self.YStop.get())
		
		self.mux = tk.IntVar()
		self.mux.set(0)
		self.quad0 = tk.BooleanVar()
		self.quad0.set(False)
		self.quad1 = tk.BooleanVar()
		self.quad1.set(False)
		self.quad2 = tk.BooleanVar()
		self.quad2.set(False)
		self.quad3 = tk.BooleanVar()
		self.quad3.set(False)
		self.columnconfigure(0, pad = 2)
		self.createWidgets()
		self.grid()

	def createWidgets(self):
		self.fileFrame = tk.Frame()
		self.filenameLabel = tk.Label(text = "File Name: ")
		self.filenameLabel.grid(row = 0, column = 0, sticky = tk.W, padx = 5, pady = 5, in_ = self.fileFrame)
		self.filenameEntry = tk.Entry(textvariable = self.filename)
		self.filenameEntry.grid(row = 0, column = 1, sticky = tk.W, padx = 5, pady = 5, in_ = self.fileFrame)
		self.setButton = tk.Button(self.fileFrame, text='Set', command=self.setfilename)
		self.setButton.grid(row = 0, column = 2, sticky = tk.W)
		self.saveToLabel = tk.Label(text = "Next: ")
		self.saveToLabel.grid(row = 1, column = 0, sticky = tk.W, padx = 5, pady = 5, in_ = self.fileFrame)
		self.saveToLabelName = tk.Label(textvariable = self.filenametext)
		self.saveToLabelName.grid(row = 1, column = 1, sticky = tk.W, padx = 5, pady = 5, in_ = self.fileFrame)
		self.fileFrame.grid(row = 0, column = 0, sticky = tk.W + tk.N, padx = 5, pady = 5, in_ = self)
		
		self.infoFrame = tk.Frame()
		self.loopCountLabel = tk.Label(textvariable = self.loopCount)
		self.loopCountLabel.grid(row = 0, column = 0, in_ = self.infoFrame)
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
		self.pulsedRadio.grid(row = 1, column = 0, sticky = tk.W)
		self.sweepModeFrame.grid(row = 3, column = 0, sticky = tk.W + tk.N, padx = 5, pady = 5, in_ = self)
		
		self.figureCanvas = FigureCanvasTkAgg(self.fig, master=self)
		self.figureCanvas.get_tk_widget().grid(row = 1, column = 1, columnspan = 15, rowspan = 15, sticky = tk.N, in_ = self)
		
		self.buttonsFrame = tk.Frame()
		self.goButton = tk.Button(self.buttonsFrame, text='GO!', command=self.go)
		self.goButton.grid(row = 0, column = 2)
		self.quitButton = tk.Button(self.buttonsFrame, text='Quit', command=self.quit)
		self.quitButton.grid(row = 0, column = 4)
		self.buttonsFrame.grid(row = 4, column = 0, in_ = self)
		
		self.MUXFrame = tk.Frame()
		self.MUXLabel = tk.Label(text = "MUX line: ")
		self.MUXLabel.grid(row = 0, column = 0, sticky = tk.W+tk.E, in_ = self.MUXFrame)
		self.MUXRadio0 = tk.Radiobutton(self.MUXFrame, text ="0", variable = self.mux, value = 0, command=self.MUXserial)
		self.MUXRadio0.grid(row = 0, column = 1, sticky = tk.W)
		self.MUXRadio1 = tk.Radiobutton(self.MUXFrame, text ="1", variable = self.mux, value = 1, command=self.MUXserial)
		self.MUXRadio1.grid(row = 0, column = 2, sticky = tk.W)
		self.MUXRadio2 = tk.Radiobutton(self.MUXFrame, text ="2", variable = self.mux, value = 2, command=self.MUXserial)
		self.MUXRadio2.grid(row = 0, column = 3, sticky = tk.W)
		self.MUXRadio3 = tk.Radiobutton(self.MUXFrame, text ="3", variable = self.mux, value = 3, command=self.MUXserial)
		self.MUXRadio3.grid(row = 0, column = 4, sticky = tk.W)
		self.MUXRadio4 = tk.Radiobutton(self.MUXFrame, text ="4", variable = self.mux, value = 4, command=self.MUXserial)
		self.MUXRadio4.grid(row = 0, column = 5, sticky = tk.W)
		self.MUXRadio5 = tk.Radiobutton(self.MUXFrame, text ="5", variable = self.mux, value = 5, command=self.MUXserial)
		self.MUXRadio5.grid(row = 0, column = 6, sticky = tk.W)
		self.MUXRadio6 = tk.Radiobutton(self.MUXFrame, text ="6", variable = self.mux, value = 6, command=self.MUXserial)
		self.MUXRadio6.grid(row = 0, column = 7, sticky = tk.W)
		self.MUXRadio7 = tk.Radiobutton(self.MUXFrame, text ="7", variable = self.mux, value = 7, command=self.MUXserial)
		self.MUXRadio7.grid(row = 0, column = 8, sticky = tk.W)
		self.MUXFrame.grid(row = 5, column = 0, in_ = self)
		
		self.QUADFrame = tk.Frame()
		self.QUADLabel = tk.Label(text = "Arduino: ")
		self.QUADLabel.grid(row = 0, column = 0, sticky = tk.W+tk.E, in_ = self.QUADFrame)
		self.QUADCheck0 = tk.Checkbutton(self.QUADFrame, text ="Pin 5", variable = self.quad0, offvalue = False, onvalue = True, command=self.QUADserial)
		self.QUADCheck0.grid(row = 0, column = 1, sticky = tk.W)
		self.QUADCheck1 = tk.Checkbutton(self.QUADFrame, text ="Pin 4", variable = self.quad1, offvalue = False, onvalue = True, command=self.QUADserial)
		self.QUADCheck1.grid(row = 0, column = 2, sticky = tk.W)
		self.QUADCheck2 = tk.Checkbutton(self.QUADFrame, text ="Pin 3", variable = self.quad2, offvalue = False, onvalue = True, command=self.QUADserial)
		self.QUADCheck2.grid(row = 0, column = 3, sticky = tk.W)
		self.QUADCheck3 = tk.Checkbutton(self.QUADFrame, text ="Pin 2", variable = self.quad3, offvalue = False, onvalue = True, command=self.QUADserial)
		self.QUADCheck3.grid(row = 0, column = 4, sticky = tk.W)
		self.QUADFrame.grid(row = 6, column = 0, in_ = self)
		
		self.holdModeFrame = tk.Frame()
		self.holdOffRadio = tk.Radiobutton(self.holdModeFrame, text ="Hold Off", variable = self.holdMode, value = 0)
		self.holdOffRadio.grid(row = 0, column = 0, sticky = tk.W)
		self.HoldOnRadio = tk.Radiobutton(self.holdModeFrame, text ="Hold On", variable = self.holdMode, value = 1)
		self.HoldOnRadio.grid(row = 0, column = 1, sticky = tk.W)
		self.holdModeFrame.grid(row = 7, column = 0, sticky = tk.W + tk.N, padx = 5, pady = 5, in_ = self)
	
	def setfilename(self):
		self.filenametext.set(self.filename.get()+str(self.filenamenumber.get()))
	
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
		stepsize = (self.stop.get()-self.start.get())/self.steps.get()	#Step size
		self.ser.write("smua.reset()\n".encode())	#Reset SMU
		self.ser.write("smua.nvbuffer2.clear()\n".encode())
		self.ser.write("smua.nvbuffer2.collectsourcevalues = 1\n".encode())
		self.ser.write("errorqueue.clear()\n".encode())
		self.ser.write("display.screen = display.SMUA\n".encode())		
		self.ser.write("display.smua.measure.func = display.MEASURE_DCAMPS\n".encode())		
		self.ser.write("format.data = format.ASCII\n".encode())
		self.ser.write("beeper.enable = beeper.OFF \n".encode())	#Turn off beeper
		self.ser.write("smua.sense = smua.SENSE_LOCAL \n".encode())	#Sense current (DC)
		self.ser.write("smua.trigger.measure.i(smua.nvbuffer2)\n".encode())
		self.ser.write(("smua.source.limiti = "+str(self.compliance.get())+"\n").encode())	#Set compliance (A)
		self.ser.write("smua.measure.nplc = 0.05\n".encode())
		self.ser.write(("smua.trigger.source.linearv("+str(self.start.get())+","+str(self.stop.get())+","+str(self.steps.get())+")\n" ).encode()) #Set sweep start point (V), stop point (V) and steps
		self.ser.write("smua.trigger.endsweep.action = smua.SOURCE_IDLE\n".encode())
		self.ser.write("smua.trigger.source.action = smua.ENABLE\n".encode())	#Change to sweep mode
		self.ser.write("smua.source.autorangev = smua.AUTORANGE_ON \n".encode())	#Set source range AUTO/BEST/FIXED
		self.ser.write(("smua.nvbuffer2.fillcount = "+str(self.steps.get()+1)+"\n").encode())	#Set amount of points to store in memory (steps + 1)
		self.ser.write(("smua.measure.delay = "+str(self.delay.get())+"\n").encode())	#Set delay
		self.ser.write(("smua.trigger.count = "+str(self.steps.get())+"\n").encode())
		

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
		self.ser.write(("smua.nvbuffer2.fillcount = "+str(self.steps.get())+"\n").encode())	#Set amount of points to store in memory (steps + 1)
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
		datacsv=csv.reader(data.decode().split(','))	#Convert binary data into a csv structure containing strings, and split using the commas (,) as separators
		list=[]	#Empty list that will temporarily keep the extracted data (it comes as series of 5 values V,I,?,?,?)
		results=[[],[]] #Empty list that will store the data as [[V1, V2..., Vn],[I1,I2,...,In]]
		for row in datacsv:
			list.append(row)	#Extract data from the csv structure into list
		for ii in range(0, self.steps.get()):
			for jj in range(0,2):
				results[jj].append(list.pop(0).pop())	#Extract the first two values of each serias (V,I) into results...
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
			data1.append(data2[ii])	#Append the secon set of data to the former one
		return data1
	
	def exportFile(self, dataToExport):
		with open(self.filenametext.get()+".txt", 'wt') as csvfile:
			csvfile.write(str(self.start.get())+"\t"+str(self.start.get())+"\n")
			writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_NONE)
			array = np.asarray(dataToExport).T.tolist()
			for ii in range(0, self.steps.get()):
				writer.writerow(array[ii])
	
	def loopSweeps(self):
		dataArray = []
		for l in range(0,self.loops.get()):
			#if l % 2 == 0:
				#self.ser.write(":SOUR:SWE:DIR UP\n".encode())
			#else:
				#self.ser.write(":SOUR:SWE:DIR DOWN\n".encode())
			self.loopCount.set(l + 1)
			self.runSweep()
			self.ser.write(("x = printbuffer(1,"+str(self.steps.get())+",smua.nvbuffer2.sourcevalues, smua.nvbuffer2.readings)\n").encode())
			self.ser.write("waitcomplete(0)\n".encode())
			output = self.recoverData(self.ser.readline())
			self.plotCurve(output)
			dataArray = self.joinData(dataArray, output)
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
		
	def QUADserial(self):
		quadState = ""
		if self.quad0.get():
			quadState = quadState + "A1"
		else: quadState = quadState + "A0"
		if self.quad1.get():
			quadState = quadState + "B1"
		else: quadState = quadState + "B0"
		if self.quad2.get():
			quadState = quadState + "C1"
		else: quadState = quadState + "C0"
		if self.quad3.get():
			quadState = quadState + "D1"
		else: quadState = quadState + "D0"
		print(quadState)
		self.ser1.write(quadState.encode())
		
	def go(self):
		if self.holdMode.get() == 0:
			self.a.hold(False)
		elif self.holdMode.get() == 1:
			self.a.hold(True)
		else:
			return 0
		if self.modes.get() == 0:
			self.configSweep()
		elif self.modes.get() == 1:
			self.configCustomSweep()
		else:
			return 0
		op=self.loopSweeps()
		self.exportFile(op)
		self.filenamenumber.set(1 + self.filenamenumber.get())
		self.setfilename()

plt.ion()
app = Application()
app.master.title('Keithley 2600B Sweeper')
app.mainloop()


