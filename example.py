#!/usr/bin/env python3
import serial
import time
import uuid 
import sys
import pyTekMSO
import os

#This script can be used to automate measurements with our textronix mso6 scope.
#Locations with EDITABLE configuration are marked with "EDIT"
#Overview: 
#1) Configure: Setup Save Locations for the traces on the scope and for the case log files on the pc
#             Save configuration together with the logs. Aks user if directories are not empty, to avoid mixed data
#2) Measure Loop: Configure Measure on Trigger, Wait for Scope to be ready, measure untill fast frame is full
# wait for scope to write data. Sometimes the scope does not detect a trigger. Thus there is a timeout for the save
# which restarts the measuremt.


#Function to Initialize the Serial Port
def init_serial():
    global ser          #Must be declared in Each Function
    ser = serial.Serial()
    
    ser.baudrate = 115200
    #ser.port = 'COM5'

    #dev = serial.Serial("/dev/ttyUSB0", 115200)
    ser.port = '/dev/ttyUSB0'                   #If Using Linux
    #ser.port = '/dev/tty.usbmodem1423' #If Using Mac
    
   #Specify the TimeOut in seconds
    ser.timeout = 200000
    ser.open()          

#Returns true if the path points to an empty folder on the scope
def isScopeDirEmpty(scope,path):
	scope.set_cwd(path)
	print("scope.get_cwd() is",scope.get_cwd())
	content = str(scope.get_ldir())
	print("scope.get_ldir is",content, 'with type ',type(content))
	return content == '""'


###STATIC CONFIG, EDIT###
#save traces in subfolders (created by this script) on the scope under this path
#must end with /
standardPathScope="E:/Traces/"
#save case files in subfolders (created by this sript) on this pc under this path. TODO: there is a file transwer command but the encoding is weird
#must end with /
standardPathPC="/home/its/Nextcloud/Tek_traces/"



#check and parse cli args
if len(sys.argv) != 3:
	print("Usage: example.py <folder> <number of aquisitions>")
	exit(1)
#folder in standard path where data should be saved
measurementFolder=sys.argv[1]
#number of aquisitions
ACQ_N = int(sys.argv[2])

print('Connecting to scope...')
#EDIT
scope = pyTekMSO.TekMSO('141.83.62.51')


#set traces per frame to max and check if aquisitions count is divisble by that
nframes=scope.get_fastframe_count_max()
if ACQ_N % nframes != 0:
	print("Number of aquisitions must be a multiple of the fast frame size(",nframes,").")
	exit(1)
	pass

print("Setting fast frame to ",nframes, "measurements.")

#create dir on scope if it does not exists
scope.set_mkdir(standardPathScope+measurementFolder)
#warn user if dir is not empty
if not isScopeDirEmpty(scope,standardPathScope+measurementFolder):
	answer = input('Scope dir ' + standardPathScope+measurementFolder +' is not empty. Are you sure you want shoot yourself in the foot [y/n]?')
	if answer != "y":
		exit(1)


#create dir on pc if it does not exist
if not os.path.exists(standardPathPC+measurementFolder):
	os.mkdir(standardPathPC+measurementFolder)
#warn user if dir is not empty
if len(os.listdir(standardPathPC+measurementFolder)) != 0:
	answer = input('PC dir ' + standardPathPC+measurementFolder +' is not empty. Are you sure you want shoot yourself in the foot [y/n]?')
	if answer != "y":
		exit(1)


#configur scope
scope.disable_header() #controls whether query results are prefixed with command header
scope.setup_opc()
scope.set_save_on_trigger_file_path(standardPathScope+measurementFolder)
print('Setting save path to', scope.get_save_on_trigger_file_path())


answer = input( ("Sample rate is {}, record length {}. Also check you save the correct channel!,"
"Start measurement [y/n]?").format(scope.get_horizontal_samplerate(),scope.get_horizontal_length()))
if answer != "y":
	exit(1)

print("Saving setup to ",standardPathScope+measurementFolder+"/setup.set"," for later reference")
scope.save_setup(standardPathScope+measurementFolder+"/setup.set")


ser = 0
init_serial()

#prepare log files
fullLog = None
caseOnlyLog = None
f_time=time.strftime('%Y%m%d-%H%M_%S')
pathFullLog = "{}/fullLog-{}.txt".format(standardPathPC+measurementFolder,f_time)
pathCaseOnlyLog = "{}/caseOnlyLog-{}.txt".format(standardPathPC+measurementFolder,f_time)
fullLog = open(pathFullLog,'wb')
caseOnlyLog = open(pathCaseOnlyLog,'wb')

acquisitionSuccessful=True
acq=0
while acq < ACQ_N :
	if acquisitionSuccessful:

		print('Running acquisition [', acq+1, '/', ACQ_N, ']')
		
		print('Save Location:'+scope.get_save_on_trigger_file_path())
		print('File Name:' + scope.get_save_on_trigger_file_name())

		scope.enable_fastframe()
		scope.set_fastframe_count(nframes) #set measurements/triggers per fast frame
		scope.enable_save_on_trigger()
		scope.enable_acq_mode_sequence()
		scope.start_acq()
		scope.set_opc()
	
		while scope.get_trigger_state() != 'READY':
			print('scope not ready')
			time.sleep(0.1)
	else:
		print("repeating measurement")

	###CUSTOM CODE TO START TARGET CODE ON BOARD AND LOG DESIRED DATA, EDIT###
	for i in range(nframes):
		print("Running ", i+1, "out of ", nframes, "ff measurements")
		ser.write(str.encode('a')) #send start signal
		print("start signal send")
		case = ser.readline() # asci string, 0 for fixed, 1 for random
		print("ping")
		plain_message = ser.readline() # asci hex string
		print("ping")

		signature = ser.readline() # asci hex string
		print("ping")
		print("case=",case,"\nmessage=",plain_message,"\nsignature=",signature,"\n")
		fullLog.write(case+plain_message+signature)
		caseOnlyLog.write(case)


	print("waiting for scope to write")
	#busy wait with timeout, if timeout occurs we had a misalignment and don't increase the count
	longestSleepInSec = 20
	sleepCnt = 0
	sleepSecs = 0.5
	acquisitionSuccessful=False
	while sleepCnt * sleepSecs < longestSleepInSec:
		if scope.get_esr() == 1:
			acquisitionSuccessful=True
			break
		time.sleep(sleepSecs)
		sleepCnt = sleepCnt+1
	#only increment loop var if we have been successfull
	if acquisitionSuccessful:
		acq = acq+nframes
		

print('\nDone. Check the python source for the format of the output file\n')
ser.close()
fullLog.close()
caseOnlyLog.close()
