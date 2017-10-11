import serial
import csv
import numpy as np
import time

def run(ser):
	"""Orders the SMU to perform the previously configured measuremen.
	"""
	ser.write(":OUTP ON\n".encode())
	ser.write(":READ?\n".encode())

def config(ser,lev):
    """Configure Keithley 2400 SMU to perform current pulses
    Takes the following arguments: 
    -ser: Serial port
    -lev: current level
    """
    ser.write("*RST\n".encode())	#Reset SMU
    ser.write(":SYST:BEEP:STAT 0\n".encode())	#Turn off beeper
    ser.write(":SOUR:FUNC CURR\n".encode())	#Source Voltage
    ser.write(":SOUR:CURR:MODE FIXED\n".encode())
    ser.write(":SOUR:CURR:RANG 10E-3\n".encode())
    ser.write((":SOUR:CURR:LEV "+lev+"\n").encode())
    ser.write((":SENS:VOLT:PROT 1.2\n").encode())	
    ser.write(":SENS:FUNC 'VOLT'\n".encode())	
    ser.write(":SENS:VOLT:RANG 2\n".encode())
    ser.write(":FORM:ELEM VOLT\n".encode())

def recoverData(data):
	"""Converts the binary data stream acquired from the SMU into a 2-column human-readable list containing voltage and current (as string lists)
	for ease of manipulation and its later conversion into csv files.
	"""
	datacsv=csv.reader(data.decode().split(','))	#Convert binary data into a csv structure containing strings, and split using the commas (,) as separators
	list=[]	#Empty list that will temporarily keep the extracted data (it comes as series of 5 values V,I,?,?,?)
	results=[[],[]] #Empty list that will store the data as [[V1, V2..., Vn],[I1,I2,...,In]]
	for row in datacsv:
		list.append(row)	#Extract data from the csv structure into list
	results[0].append(list.pop(0).pop())	#Extract the first two values of each serias (V,I) into results...
	return results

def joinData(data1, data2):
	"""Function that merges two differents sets of data so they can be exported into a single file
	"""
	for ii in range(0, len(data2)): 
		data1.append(data2[ii])	#Append the secon set of data to the former one
	return data1

def exportFile(dataToExport):
    with open("archivo.txt", 'wt') as csvfile:
	    writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_NONE)
	    array = np.asarray(dataToExport).T.tolist()
	    #print(array)
	    for ii in range(0, 2000): #mirar esto
		    writer.writerow(array[ii])


ser=serial.Serial('COM4', 9600, timeout=10, parity = serial.PARITY_NONE) #COM4/COM5
dataArray = []
for iii in range(0,500):
	config(ser,"0")
	run(ser)
	output = recoverData(ser.readline())
	dataArray = joinData(dataArray, output)
	ser.write(":OUTP OFF\n".encode())
	config(ser,"2.97E-3")
	run(ser)
	output = recoverData(ser.readline())
	dataArray = joinData(dataArray, output)
	ser.write(":OUTP OFF\n".encode())
exportFile(dataArray)
