#!/usr/bin python 
import tkinter as tk
import visa
import serial
import serial.tools.list_ports
import csv
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.pyplot as plt
import tkinter.filedialog # Otherwise it won't compile to .exe
import time
import Keithley.K2602B as K2602B
import Keithley.K2400 as K2400
import Keithley.K6430 as K6430

smu_modules = {
        'K2602B': K2602B,
        'K2400': K2400,
        'K6430': K6430
        }
comm_modules = ['TCPIP', 'GPIB', 'Serial']

#09/06/2016
#Remove the try-except?
#Add Enable/Disable Button for MUX and QUAD or re-address the ports in the arduino
#Version including the MUX and the QUAD SWITCH interfacing


class Application(tk.Frame):
        def __init__(self, master=None):
                """Application initialization
                """
                tk.Frame.__init__(self, master)

                #Module variables
                self.SMUVar = tk.StringVar()
                self.SMUVar.set(list(smu_modules.keys())[0])
                self.commsVar = tk.StringVar()
                self.commsVar.set(comm_modules[0])

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
                self.loopCount = tk.IntVar()
                self.loopCount.set(1)
                self.delayLoop = tk.DoubleVar()
                self.delayLoop.set(1)
                
                self.filenameNumber = tk.IntVar()
                self.filenameNumber.set(0)
                
                self.filename = tk.StringVar()
                self.filename.set("Sweep_")

                self.filenameText = tk.StringVar()
                self.setfilename()
                self.modes = tk.IntVar()
                self.modes.set(0)

                #Graph Variables
                self.XStart = tk.DoubleVar()
                self.XStart.set(0.0)
                self.XStop = tk.DoubleVar()
                self.XStop.set(0.5)
                self.YStop = tk.DoubleVar()
                self.YStop.set(0.005)
                self.YStart = tk.DoubleVar()
                self.YStart.set(-self.YStop.get())

                self.createMenu()
                self.createWidgets()
                self.grid()

        def createWidgets(self):
                self.fileFrame = tk.Frame()
                self.filenameLabel = tk.Label(text = "File Name: ")
                self.filenameLabel.grid(row = 0, column = 0, sticky = tk.W, padx = 5, pady = 5, in_ = self.fileFrame)
                self.filenameEntry = tk.Entry(textvariable = self.filename)
                self.filenameEntry.grid(row = 0, column = 1, sticky = tk.W+tk.E, padx = 5, pady = 5, in_ = self.fileFrame)
                self.filenamenumberEntry = tk.Entry(textvariable = self.filenameNumber, width = 3, justify = tk.RIGHT)
                self.filenamenumberEntry.grid(row = 0, column = 2, sticky = tk.W, padx = 5, pady = 5, in_ = self.fileFrame)
                self.setButton = tk.Button(self.fileFrame, text='Set', command=self.setfilename)
                self.setButton.grid(row = 0, column = 3, sticky = tk.W)
                self.saveToLabel = tk.Label(text = "Next: ")
                self.saveToLabel.grid(row = 1, column = 0, sticky = tk.W, padx = 5, pady = 5, in_ = self.fileFrame)
                self.saveToLabelName = tk.Label(textvariable = self.filenameText)
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

        def createMenu(self):
                self.menubar = tk.Menu(self)
                smumenu = tk.Menu(self.menubar, tearoff = 0)
                commmenu = tk.Menu(self.menubar, tearoff = 0)
                
                self.menubar.add_cascade(label="SMU", menu=smumenu)
                self.menubar.add_cascade(label="Communications", menu=commmenu)
                
                for smu in smu_modules:
                        if smu == 'K2602B':
                                st = tk.NORMAL
                        else:
                                st = tk.DISABLED
                        smumenu.add_radiobutton(label=smu, state = st, var = self.SMUVar, value = smu, command = self.config)

                for comm in comm_modules:
                        if comm == 'TCPIP':
                                st = tk.NORMAL
                        else:
                                st = tk.DISABLED
                        commmenu.add_radiobutton(label = comm, state = st, var = self.commsVar, value = comm, command = self.config)
                
                self.master.config(menu=self.menubar)

        def setfilename(self):
                self.filenameText.set(self.filename.get()+str(self.filenameNumber.get()))

        def go(self):
                commPort = ser
                start = self.start.get()
                stop = self.stop.get()
                steps = self.steps.get()
                loops = self.loops.get()
                delay = self.delay.get()
                loopDelay = self.delayLoop.get()
                NPLC = self.NPLC.get()
                loopvar = self.loopCount
                filename = self.filename
                filenameNumber = self.filenameNumber
                filenameText = self.filenameText
                compliance = self.compliance.get()

                F.go(self, commPort, start, stop, steps, loops, delay, loopDelay, compliance, NPLC, loopvar, filename, filenameNumber, filenameText, 'smua', C)

class Configuration(tk.Frame):
        def __init__(self, master=None):
                tk.Frame.__init__(self, master)
                #Module variables
                self.SMUVar = tk.StringVar()
                self.SMUVar.set(list(smu_modules.keys())[0])
                self.commsVar = tk.StringVar()
                self.commsVar.set(comm_modules[0])
                self.configWindow()
                
        def configWindow(self):
                configFrame = tk.Frame(self)
                radioFrame = tk.Frame(configFrame)
                self.okButton = tk.Button(configFrame, text='Accept', command=self.config, relief = tk.GROOVE)
                self.okButton.grid(row = 1, column = 0, padx = 5, pady = 5)
                
                SMUFrame = tk.Frame(radioFrame, relief = tk.GROOVE, bd = 2)
                SMULabel = tk.Label(SMUFrame, text = "SMU", padx = 5, pady = 5)
                SMULabel.grid(row = 0, column = 0)
                radioK2602B = tk.Radiobutton(SMUFrame, text ='Keithley 2602B', variable = self.SMUVar, value = 'K2602B')
                radioK2602B.grid(row = 1, column = 0, sticky = tk.W, padx = 5, pady = 5)
                radioK2400 = tk.Radiobutton(SMUFrame, text ='Keithley 2400', variable = self.SMUVar, value = 'K2400')
                radioK2400.grid(row = 2, column = 0, sticky = tk.W, padx = 5, pady = 5,)
                radioK2400 = tk.Radiobutton(SMUFrame, text ='Keithley 6430', variable = self.SMUVar, value = 'K6430')
                radioK2400.grid(row = 3, column = 0, sticky = tk.W, padx = 5, pady = 5,)
                SMUFrame.grid(row = 0, column = 0, padx = 5, pady = 5)

                commsFrame = tk.Frame(radioFrame, relief = tk.GROOVE, bd = 2)
                commsLabel = tk.Label(commsFrame, text = "Comms", padx = 5, pady = 5)
                commsLabel.grid(row = 0, column = 0)
                radioTCPIP = tk.Radiobutton(commsFrame, text ='TCPIP', variable = self.commsVar, value = 'TCPIP')
                radioTCPIP.grid(row = 1, column = 0, sticky = tk.W, padx = 5, pady = 5)
                radioSerial = tk.Radiobutton(commsFrame, text ='Serial', variable = self.commsVar, value = 'Serial')
                radioSerial.grid(row = 2, column = 0, sticky = tk.W, padx = 5, pady = 5)
                radioGPIB = tk.Radiobutton(commsFrame, text ='GPIB', variable = self.commsVar, value = 'GPIB')
                radioGPIB.grid(row = 3, column = 0, sticky = tk.W, padx = 5, pady = 5)
                radioX1 = tk.Radiobutton(commsFrame, text ='XXXXXX', variable = self.commsVar, value = 'XXXXXX')
                radioX1.grid(row = 4, column = 0, sticky = tk.W, padx = 5, pady = 5)
                commsFrame.grid(row = 0, column = 1, padx = 5, pady = 5)

                imageCanvas = tk.Canvas(radioFrame, width = 90, height = 90)
                photo = tk.PhotoImage(file = "qopto.gif")
                imageCanvas.create_image(45, 45, image = photo)
                imageCanvas.image = photo
                imageCanvas.grid(row = 0, column = 2, padx = 5, pady = 5)

                radioFrame.grid(row = 0, column = 0, padx = 5, pady = 5)
                configFrame.grid(row = 0, column = 0, padx = 5, pady = 5)

                self.grid()

        def config(self):
                global F, C, ser, rm
                F = smu_modules[self.SMUVar.get()]
                C = self.commsVar.get()
                if self.commsVar.get() == 'TCPIP':
                        rm = visa.ResourceManager('@py')
                        ser = rm.open_resource("TCPIP::169.254.0.1::INSTR")
                elif self.commsVar.get() == 'Serial':
                        #Tries to find the COM port of the Keithley by vendor description. Should work for both 2400 and 2602B
                        for port in serial.tools.list_ports.comports(True):
                                print(port)
                                if port.description.find('USB-to-Serial') != -1:
                                        print(port.device)
                                        #ser=serial.Serial(port.device, 115200, timeout=10, parity = serial.PARITY_NONE)
                                        ser=serial.Serial(port.device, 57600, timeout=10, parity = serial.PARITY_NONE)
                elif self.commsVar.get() == 'GPIB':
                        #rm = visa.ResourceManager('C:/windows/system32/visa32.dll')
                        #rm = visa.ResourceManager('@py')
                        rm = visa.ResourceManager()
                        ser = rm.open_resource('GPIB0::24::INSTR')
                        ser.timeout = 100000
                else: pass
                self.master.destroy()
                self.master.quit()

plt.ion()

root = tk.Tk()
root.title('Configuration')

conf = Configuration(root)
conf.mainloop()

root = tk.Tk()
root.title(F.__name__+' sweeper using '+C+' communication')

app = Application()
app.mainloop()


