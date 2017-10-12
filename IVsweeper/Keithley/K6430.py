#!/usr/bin python 
import tkinter as tk
import visa
import csv
import numpy as np
import matplotlib.pyplot as plt
import tkinter.filedialog # Otherwise it won't compile to .exe
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import time

"""Keithley.K6430
    
    Module including the sweep configuration and execution, and data manipulation
and recovery functions for the Keithley 6430 SourceMeter.

    Currently it supports communications over the serial (RS-232) and GPIB (488.1
protocol) ports. Communications with the SMU use the SCPI language.
"""



def configSweep(commPort, start = 0, stop = 0.2, steps = 100, delay = 0.02, compliance = 0.0005, NPLC = 0.05, smu = 'smua'):
    """
    Configure Keithley 2400 before performing a source voltage - measure current sweep.
        - comPort: Serial or GPIB port used to communicate with the SMU
        - start: First point of the voltage sweep (in volts)
        - stop: Last point of the voltage sweep (in volts)
        - steps: Number of points in the sweep
        - delay: Delay between measurements (in seconds)
        - compliance: Upper current limit (in amperes, absolute value)
        - NPLC: Number of power line cycles until the measurement is considered stable.
            Rule of thumb is the smaller the NPLC, the faster the sweep, at a cost of precision.
        - smu: String containing the channel for machines with more than one SMU. Not used in
            2400, remove in next version.
    """
    stepsize = (stop-start)/steps	#Step size
    commPort.write("*RST\n".encode())	#Reset SMU
    commPort.write(":SENS:FUNC:CONC OFF\n".encode())
    commPort.write(":SOUR:FUNC VOLT\n".encode())	#Source Voltage
    commPort.write(":SENS:FUNC 'CURR:DC'\n".encode())	#Sense current (DC)
    commPort.write((":SENS:CURR:PROT "+str(compliance)+"\n").encode())	#Set compliance (A)
    commPort.write(":SENS:CURR:NPLC 0.05\n".encode())
    commPort.write((":SOUR:VOLT:STAR "+str(start)+"\n").encode())	#Set sweep start point (V)
    commPort.write((":SOUR:VOLT:STOP "+str(stop)+"\n").encode())	#Set sweep start point (V)
    commPort.write((":SOUR:VOLT:STEP "+str(stepsize)+"\n").encode())	#Set sweep step size (V)
    commPort.write(":SOUR:VOLT:MODE SWE\n".encode())	#Change to sweep mode
    commPort.write(":SOUR:SWE:RANG BEST\n".encode())	#Set source range AUTO/BEST/FIXED
    commPort.write(":SOUR:SWE:SPAC LIN\n".encode())	#Set steps spacing LIN/LOG
    commPort.write((":TRIG:COUN "+str(steps+1)+"\n").encode())	#Set amount of points to store in memory (steps + 1)
    commPort.write((":SOUR:DEL "+str(delay)+"\n").encode())	#Set delay

def runSweep(commPort, smu = 'smua'):
    switchSource(commPort, smu, True)
    commPort.write(":READ?\n".encode())

def switchSource(commPort, smu = 'smua', on = False):
    if on == True:
        commPort.write(":OUTP ON\n".encode())
    else:
        commPort.write(":OUTP OFF\n".encode())

def loopSweeps(app, commPort, loops, loopvar, loopDelay, start, stop, steps, oneWay = False, smu = 'smua'):
    dataArray = []
    for l in range(0,loops):
            if oneWay:
               commPort.write(":SOUR:SWE:DIR UP\n".encode())
            else:
                if l % 2 == 0:
                        commPort.write(":SOUR:SWE:DIR UP\n".encode())	
                else:
                        commPort.write(":SOUR:SWE:DIR DOWN\n".encode())
            loopvar.set(l + 1)
            app.update()
            runSweep(commPort, smu)
            a = commPort.readline()
            a = a.decode()
            output = recoverData(a, steps)
            plotCurve(app, app.a, app.figureCanvas, output)
            dataArray = joinData(dataArray, output)
            switchSource(commPort, smu, False)
            time.sleep(loopDelay)
    switchSource(commPort, smu, False)
    return dataArray

def go(app, commPort, start, stop, steps, loops, delay, loopDelay, compliance, NPLC, loopvar, filename, filenameNumber, filenameText, smu, comms): #change comms in all functions
    print("It's ALIVE!!!!")
    app.a.hold(False)
    compliance = app.compliance.get()
    configSweep(commPort, start, stop, steps, delay, compliance, NPLC, 'smua')
    op=loopSweeps(app, commPort, loops, loopvar, loopDelay, start, stop, steps, oneWay = False, smu = 'smua') ###Add this functionality hera and in the main program
    exportFile(filenameText, steps, op)
    filenameNumber.set(1 + filenameNumber.get())
    setFilename(filename, filenameText, filenameNumber)


#########################################################
####       DATA RECOVERY AND PARSING FUNCTIONS       ####
#########################################################

def recoverData(data, steps):
    """Converts the binary data stream acquired from the SMU into a 2-column human-readable list containing voltage and current (as string lists)
    for ease of manipulation and its later conversion into csv files.
    """
    datacsv=csv.reader(data.split(',')) 
    print(datacsv)	#Convert binary data into a csv structure containing strings, and split using the commas (,) as separators
    list=[]                                                 #Empty list that will temporarily keep the extracted data (it comes as series of 5 values V,I,?,?,?)
    results=[[],[]]                                         #Empty list that will store the data as [[V1, V2..., Vn],[I1,I2,...,In]]
    for row in datacsv:
            list.append(row)                                #Extract data from the csv structure into list
    for ii in range(0, steps+1):
            for jj in range(0,2):
                    results[jj].append(list.pop(0).pop())   #Extract the first two values of each serias (V,I) into results
    return results

def joinData(data1, data2):
    for ii in range(0, len(data2)): 
            data1.append(data2[ii])                         #Append the second set of data to the former one
    return data1

def plotCurve(app, figure, figCanvas, data):
    figure.plot(data[0],data[1])
    figure.hold(True)
    figure.grid(b=True, which='major', color='r', linestyle='--')
    figure.axis([app.XStart.get(), app.XStop.get() , app.YStart.get() , app.YStop.get()]) ######################CHANGE
    figCanvas.show()
    #plt.pause(0.001)
    app.update()

def setFilename(filename, filenameText, filenameNumber):
    filenameText.set(filename.get()+str(filenameNumber.get()))
                
def exportFile(filename, steps, dataToExport):
    with open(filename.get() + ".txt", 'wt') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_NONE)
            array = np.asarray(dataToExport).T.tolist()
            for ii in range(0, steps + 1):
                    writer.writerow(array[ii])

__author__ = "Ramón Bernardo Gavito, and Benjamin Astbury"
__copyright__ = "Copyright 2017, Young-Quantum Group, Lancaster University"
__credits__ = ["Ramón Bernardo Gavito", "Benjamin Astbury", "Hamzah Shokeir",
               "Thomas McGrath", "Robert J. Young"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Ramón Bernardo Gavito"
__email__ = "r.bernardogavito1@lancaster.ac.uk"
__status__ = "Development"
