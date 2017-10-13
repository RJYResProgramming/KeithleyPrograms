#!/usr/bin python
"""Documentation
    
    Is it printed?
    
    Indentation ok?
    """

import tkinter as tk
import visa
import csv
import numpy as np
import matplotlib.pyplot as plt
import tkinter.filedialog # Otherwise it won't compile to .exe
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import time





#########################################################
####    CONFIGURATION AND SWEEP RELATED FUNCTIONS    ####
#########################################################

def sendMessage(commPort, comms, message):
    if comms == 'TCPIP':
        commPort.write(message)
    elif comms == 'Serial':
        commPort.write(str(message+"\n").encode())
    else: pass

def configSweep(commPort, start, stop, steps, delay, compliance, NPLC, smu, comms):
    """
    Configure Keithley 2602B
    Works with Ethernet and GPIB conections, I don't know if it will work using the serial port
    -commPort - Communications port, either TCPIP identifier or GPIB object.
    """
    sendMessage(commPort, comms, ""+smu+".reset()")  #Resets the smu
    sendMessage(commPort, comms, ""+smu+".nvbuffer2.clear()")    #Clears the data buffer, in this case buffer 2
    sendMessage(commPort, comms, ""+smu+".nvbuffer2.collectsourcevalues = 1")    #Sets the buffer to save both measured data AND source values
    sendMessage(commPort, comms, "errorqueue.clear()")    #Clears the error queue, shouldn't be neccesary in the future
    sendMessage(commPort, comms, "display."+smu+".measure.func = display.MEASURE_DCAMPS")    #...in particular the measured current
    sendMessage(commPort, comms, "format.data = format.ASCII")    #Outputs data in ASCII
    sendMessage(commPort, comms, "beeper.enable = beeper.OFF")        #Turn off beeper             
    sendMessage(commPort, comms, ""+smu+".sense = "+smu+".SENSE_LOCAL")     #CHECK THIS COMMAND
    sendMessage(commPort, comms, ""+smu+".trigger.measure.i("+smu+".nvbuffer2)")    #Measure current
    sendMessage(commPort, comms, ""+smu+".source.limiti = "+str(compliance)+"") #Set compliance (A)
    sendMessage(commPort, comms, ""+smu+".measure.nplc = "+str(NPLC)+"")    #Set NPLC 
    sendMessage(commPort, comms, ""+smu+".trigger.endsweep.action = "+smu+".SOURCE_IDLE")   #After each pulse, sen the source back to 0
    sendMessage(commPort, comms, ""+smu+".trigger.source.action = "+smu+".ENABLE")   #Change to sweep mode
    sendMessage(commPort, comms, ""+smu+".source.autorangev = "+smu+".AUTORANGE_ON ")        #Set source range AUTO/BEST/FIXED
    sendMessage(commPort, comms, ""+smu+".nvbuffer2.fillcount = "+str(steps+1)+"")   #Set amount of points to store in memory (steps + 1)
    sendMessage(commPort, comms, ""+smu+".measure.delay = "+str(delay)+"")   #Set delay
    sendMessage(commPort, comms, ""+smu+".trigger.count = "+str(steps+1)+"")    #Set number of pulses

def runSweep(commPort, smu, comms):
    switchSource(commPort, smu, True, comms)
    sendMessage(commPort, comms, ""+str(smu)+".trigger.measure.action = "+str(smu)+".ENABLE")
    sendMessage(commPort, comms, ""+str(smu)+".trigger.initiate()")

def sweep(commPort, start, stop, steps, smu, up, comms):
    sendMessage(commPort, comms, (""+smu+".trigger.source.linearv("+str(start)+","+str(stop)+","+str(steps+1)+")\n" )) #Set sweep start point (V), stop point (V) and steps

def switchSource(commPort, smu, on, comms):
    if on == True:
        sendMessage(commPort, comms, ""+str(smu)+".source.output = "+str(smu)+".OUTPUT_ON")
    else:
        sendMessage(commPort, comms, ""+str(smu)+".source.output = "+str(smu)+".OUTPUT_OFF")

def loopSweeps(app, commPort, loops, loopvar, loopDelay, start, stop, steps, oneWay, smu, comms):
    dataArray = []
    for l in range(0,loops):
            if oneWay:
               sweep(commPort, start, stop, steps, smu, True, comms)
            else:
                if l % 2 == 0:
                        sweep(commPort, start, stop, steps, smu, True, comms)
                else:
                        sweep(commPort, stop, start, steps, smu, False, comms)
            loopvar.set(l + 1)
            app.update()
            runSweep(commPort, smu, comms)
            if comms == 'TCPIP':
                a=commPort.query("x = printbuffer(1,"+str(steps+1)+","+str(smu)+".nvbuffer2.sourcevalues, "+str(smu)+".nvbuffer2.readings)")
            elif comms == 'Serial':
                sendMessage(commPort, comms, "x = printbuffer(1,"+str(steps+1)+","+str(smu)+".nvbuffer2.sourcevalues, "+str(smu)+".nvbuffer2.readings)")
                a = commPort.readline()
                a = a.decode()
            else:
                a = []
            sendMessage(commPort, comms, "waitcomplete(0)")
            output = recoverData(a, steps)
            plotCurve(app, app.a, app.figureCanvas, output)
            dataArray = joinData(dataArray, output)
            switchSource(commPort, smu, False, comms)
            time.sleep(loopDelay)
    switchSource(commPort, smu, False, comms)
    return dataArray

def go(app, commPort, start, stop, steps, loops, delay, loopDelay, compliance, NPLC, loopvar, filename, filenameNumber, filenameText, smu, comms):
    print("It's ALIVE!!!!")
    app.a.hold(False)
    compliance = app.compliance.get()
    configSweep(commPort, start, stop, steps, delay, compliance, NPLC, smu, comms)
    op=loopSweeps(app, commPort, loops, loopvar, loopDelay, start, stop, steps, True, smu, comms) ###Add this functionality hera and in the main program
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
    datacsv=csv.reader(data.split(','))             #Convert binary data into a csv structure containing strings, and split using the commas (,) as separators
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
    plt.pause(0.001)
    app.update()

def setFilename(filename, filenameText, filenameNumber):
    filenameText.set(filename.get()+str(filenameNumber.get()))
                
def exportFile(filename, steps, dataToExport):
    with open(filename.get() + ".txt", 'wt') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_NONE)
            array = np.asarray(dataToExport).T.tolist()
            for ii in range(0, steps + 1):
                    writer.writerow(array[ii])
