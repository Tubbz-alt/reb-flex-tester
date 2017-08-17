
#!/usr/bin/python
import datetime
import socket
import time
import SCPI




# open remote measurement device (replace "hostname" by its actual name)
device = SCPI.SCPI("192.168.0.2",1394)

print("Connected.")

print("Factory configuration.")
device.s.send("SYST:PRES\n")

time.sleep(2)

print("Clears buffer.")
device.s.send("TRAC:CLE\n")
print("Disables continuous initiation.")
device.s.send("INIT:CONT OFF\n")
print("Immediate trigger control source.")
device.s.send("TRIG:SOUR IMM\n")
print("One Scan.")
device.s.send("TRIG:COUN 1\n")
print("Scan 40 channels.")
device.s.send("SAMP:COUN 40\n")
print("Scan List.")
device.s.send("ROUT:SCAN (@101:140)\n")
print("Start scan when enabled and triggered.")
device.s.send("ROUT:SCAN:TSO IMM\n")
print("Enables scan.")
device.s.send("ROUT:SCAN:LSEL INT\n")
print("Setup Complete.")
print("Triggers scan and requests the readings.")
device.s.send("READ?\n")
print("Disable scan")
device.s.send("ROUT:SCAN:LSEL NONE\n")

time.sleep(10)

print("Read buffer.")
buf = ""
while True:
    try:
        data = device.s.recv(1024)
        buf+=(data)
    except socket.timeout:
        break

raw=buf.split(',')
voltages=[]
for i in range(0,len(raw),3):
    voltages.append( (float(raw[i][:-3])))

print("Export to file.")

labels = ["SS1","OD7","OS7","OD6","OS6","OD5","OS5","OD4","OS4","RD","N/C","RTD_M","GD0","N/C","PCLK2","PCLK1","PCLK0","RTD_P1","RG","SCLK0","SCLK1","SCLK2","GD1","RTD_P0","N/C","OG","OS3","OD3","OS2","OD2","OS1","OD1","OS0","OD0","N/C","SS2","VIM_MON","24V","GND"]
pin=[1]+list(range(3,41))

file = open("results_%s.txt" %datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"), "w")

print("IDC40 Pin\t7702 Channel\tLabel\tVDC\n")
file.write("IDC40 Pin\t7702 Channel\tLabel\tVDC\n")


for i in range(len(labels)):
    print ("%i\t%i\t%s\t%e" % (pin[i],i+1, labels[i], voltages[i]))
    file.write("%i\t%i\t%s\t%e\n" % (pin[i],i+1, labels[i], voltages[i]))

file.close()

print("Finished")


