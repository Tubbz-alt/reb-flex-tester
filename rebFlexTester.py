
#!/usr/bin/python
import datetime
import socket
import time
import SCPI
SS_Div = 0.9091
passes = 0
fails = 0
OS7_Hi = 4.2
OS7_Lo = 5.2    # 4.7 +/- 0.5
OS6_Hi = 5.6
OS6_Lo = 6.6    # 6.1 +/- 0.5
OS5_Hi = 7.1
OS5_Lo = 8.1    # 7.6 +/- 0.5
OS4_Hi = 8.5
OS4_Lo = 9.5    # 9.0 +/-0.5
OS3_Hi = 9.9
OS3_Lo = 10.9   # 10.4 +/-0.5
OS2_Hi = 11.3
OS2_Lo = 12.3   # 11.8 +/-0.5
OS1_Hi = 12.6
OS1_Lo = 13.6   # 13.1 +/-0.5
OS0_Hi = 14.1
OS0_Lo = 15.1   # 14.6 +/- 0.5
RD_Div = 0.5426
RTD_M_Div = 0.3835
GD0_Div = 0.3210
PCLK2_Div = 0.8264
PCLK1_Div = 0.8554
PCLK0_Div = 0.8850
RTD_P1_Div = 0.3333
RG_Div = 0.5000
RTD_P0_Div = 0.3333
SCLK0_Div = 0.8006
SCLK1_Div = 0.7692
SCLK2_Div= 0.7353
GD1_Div = 0.3210
OG_Div = 0.6289



device = SCPI.SCPI("192.168.0.2",1394)
print("Connected.")
for loop in range(0,4,1):
    #print("Factory configuration.")
    device.s.send("SYST:PRES\n")

    time.sleep(2)

    #print("Clears buffer.")
    device.s.send("TRAC:CLE\n")
    #print("Disables continuous initiation.")
    device.s.send("INIT:CONT OFF\n")
    #print("Immediate trigger control source.")
    device.s.send("TRIG:SOUR IMM\n")
    #print("One Scan.")
    device.s.send("TRIG:COUN 1\n")
    #print("Scan 40 channels.")
    device.s.send("SAMP:COUN 40\n")
    #print("Scan List.")
    device.s.send("ROUT:SCAN (@101:140)\n")
    #print("Start scan when enabled and triggered.")
    device.s.send("ROUT:SCAN:TSO IMM\n")
    #print("Enables scan.")
    device.s.send("ROUT:SCAN:LSEL INT\n")
    #print("Setup Complete.")
    print("Triggers scan and requests the readings.")
    device.s.send("READ?\n")
    #print("Disable scan")
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

    #print("Export to file.")

    labels = ["SS1","OD7","OS7","OD6","OS6","OD5","OS5","OD4","OS4","RD","N/C","RTD_M","GD0","N/C","PCLK2","PCLK1","PCLK0","RTD_P1","RG","SCLK0","SCLK1","SCLK2","GD1","RTD_P0","N/C","OG","OS3","OD3","OS2","OD2","OS1","OD1","OS0","OD0","N/C","SS2","VIN_MON","24V","GND"]
    pin=[1]+list(range(3,41))

    #file = open("results_%s.txt" %datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"), "w")

    print("\nIDC40 Pin\t7702 Channel\tLabel\tVDC\n")
    #file.write("IDC40 Pin\t7702 Channel\tLabel\tVDC\n")


    for i in range(len(labels)):
        print ("%i\t%i\t%i\t%s\t%.2f" % (i , pin[i],i+1, labels[i], voltages[i]))
        #file.write("%i\t%i\t%s\t%.2f\n" % (pin[i],i+1, labels[i], voltages[i]))

    Vset = voltages[36]
    Vrun = voltages[37]
    Imon = (Vset-Vrun) * 100
    Vnorm = Vrun/24
    print("Vset %.2f" % Vset)
    print("Vrun %.2f" % Vrun)

    if (20.00 < Vset <28.00):
        # print ("Vset %.2f\t Vrun %.2f\t Imon %.2fmA\t\n" % (Vset, Vrun, Imon))
        if (60.0 < Imon < 90.0):
            passes += 1
        else:
            fails += 1
            print ("Imon out of spec, Imon = %.2f, Imon_Lo = 60mA, Imon_Hi = 90mA" % Imon)

        OD_Sum = voltages[1] + voltages[3] + voltages[5] + voltages[7] + voltages[27] + voltages[29] + voltages[31] + \
                 voltages[33]
        ##print (" OD_sum = %.2f" % OD_Sum)

        if (0.997 * 8 * Vrun) < OD_Sum < (1.003 * 8 * Vrun):
            passes += 1
        else:
            fails += 1
            print("OD_Sum = %.2f\t, OD_Lo = %.2f\t, OD_Hi = %.2f\t" % (OD_Sum, (0.997 * 8 * Vrun), (1.003 * 8 * Vrun)))

        if ((0.99 * SS_Div * Vrun) < voltages[0] < (1.01 * SS_Div * Vrun)):
            passes += 1
        else:
            fails += 1
            print("SS1 = %.2f\t, SS_Lo = %.2f\t, SS_Hi = %.2f\t" % (voltages[0], (0.99 * SS_Div * Vrun), (1.01 * SS_Div * Vrun)))

        if ((0.99 * SS_Div * Vrun) < voltages[35] < (1.01 * SS_Div * Vrun)):
            passes += 1
        else:
            fails += 1
            print(
            "SS2 = %.2f\t, SS_Lo = %.2f\t, SS_Hi = %.2f\t" % (voltages[35], (0.99 * SS_Div * Vrun), (1.01 * SS_Div * Vrun)))

        if (Vrun - (OS7_Lo) < voltages[2] < Vrun - (OS7_Hi)):
            passes += 1
            #print("OS7 = %.2f\t, OS_Lo = %.2f\t, OS_Hi = %.2f\t" % ((voltages[2]), (Vrun - (OS7_Lo)), (Vrun - (OS7_Hi))))
        else:
            fails += 1
            print("OS7 = %.2f\t, OS_Lo = %.2f\t, OS_Hi = %.2f\t" % ((voltages[2]), (Vrun - (OS7_Lo)), (Vrun - (OS7_Hi))))

        if (Vrun - (OS6_Lo) < voltages[4] < Vrun - (OS6_Hi)):
            passes += 1
            #print("OS6 = %.2f\t, OS_Lo = %.2f\t, OS_Hi = %.2f\t" % ((voltages[4]), (Vrun - (OS6_Lo)), (Vrun - (OS6_Hi))))
        else:
            fails += 1
            print("OS6 = %.2f\t, OS_Lo = %.2f\t, OS_Hi = %.2f\t" % ((voltages[4]), (Vrun - (OS6_Lo)), (Vrun - (OS6_Hi))))

        if (Vrun - (OS5_Lo) < voltages[6] < Vrun - (OS5_Hi)):
            passes += 1
            #print("OS5 = %.2f\t, OS_Lo = %.2f\t, OS_Hi = %.2f\t" % ((voltages[6]), (Vrun - (OS5_Lo)), (Vrun - (OS5_Hi))))
        else:
            fails += 1
            print("OS5 = %.2f\t, OS_Lo = %.2f\t, OS_Hi = %.2f\t" % ((voltages[6]), (Vrun - (OS5_Lo)), (Vrun - (OS5_Hi))))

        if (Vrun - (OS4_Lo) < voltages[8] < Vrun - (OS4_Hi)):
            passes += 1
            #print("OS4 = %.2f\t, OS_Lo = %.2f\t, OS_Hi = %.2f\t" % ((voltages[8]), (Vrun - (OS4_Lo)), (Vrun - (OS4_Hi))))
        else:
            fails += 1
            print("OS4 = %.2f\t, OS_Lo = %.2f\t, OS_Hi = %.2f\t" % ((voltages[8]), (Vrun - (OS4_Lo)), (Vrun - (OS4_Hi))))

        if (Vrun - (OS3_Lo) < voltages[26] < Vrun - (OS3_Hi)):
            passes += 1
            #print("OS3 = %.2f\t, OS_Lo = %.2f\t, OS_Hi = %.2f\t" % ((voltages[26]), (Vrun - (OS3_Lo)), (Vrun - (OS3_Hi))))
        else:
            fails += 1
            print("OS3 = %.2f\t, OS_Lo = %.2f\t, OS_Hi = %.2f\t" % ((voltages[26]), (Vrun - (OS3_Lo)), (Vrun - (OS3_Hi))))

        if (Vrun - (OS2_Lo) < voltages[28] < Vrun - (OS2_Hi)):
            passes += 1
            #print("OS2 = %.2f\t, OS_Lo = %.2f\t, OS_Hi = %.2f\t" % ((voltages[28]), (Vrun - (OS2_Lo)), (Vrun - (OS2_Hi))))
        else:
            fails += 1
            print("OS2 = %.2f\t, OS_Lo = %.2f\t, OS_Hi = %.2f\t" % ((voltages[28]), (Vrun - (OS2_Lo)), (Vrun - (OS2_Hi))))

        if (Vrun - (OS1_Lo) < voltages[30] < Vrun - (OS1_Hi)):
            passes += 1
            #print("OS1 = %.2f\t, OS_Lo = %.2f\t, OS_Hi = %.2f\t" % ((voltages[30]), (Vrun - (OS1_Lo)), (Vrun - (OS1_Hi))))
        else:
            fails += 1
            print("OS1 = %.2f\t, OS_Lo = %.2f\t, OS_Hi = %.2f\t" % ((voltages[30]), (Vrun - (OS1_Lo)), (Vrun - (OS1_Hi))))

        if (Vrun - (OS0_Lo) < voltages[32] < Vrun - (OS0_Hi)):
            passes += 1
            #print("OS0 = %.2f\t, OS_Lo = %.2f\t, OS_Hi = %.2f\t" % ((voltages[32]), (Vrun - (OS0_Lo)), (Vrun - (OS0_Hi))))
        else:
            fails += 1
            print("OS0 = %.2f\t, OS_Lo = %.2f\t, OS_Hi = %.2f\t" % ((voltages[32]), (Vrun - (OS0_Lo)), (Vrun - (OS0_Hi))))

        if ((0.99 * RD_Div * Vrun) < voltages[9] < (1.01 * RD_Div * Vrun)):
            passes += 1
        else:
            fails += 1
            print("RD = %.2f\t, RD_Lo = %.2f\t, RD_Hi = %.2f\t" % (voltages[9], (0.99 * RD_Div * Vrun), (1.01 * RD_Div * Vrun)))

        if ((0.99 * RTD_M_Div * Vrun) < voltages[11] < (1.01 * RTD_M_Div * Vrun)):
            passes += 1
        else:
            fails += 1
            print("RTD_M = %.2f\t, RTD_M_Lo = %.2f\t, RTD_M_Hi = %.2f\t" % (voltages[11], (0.99 * RTD_M_Div * Vrun), (1.01 * RTD_M_Div * Vrun)))

        if ((0.99 * GD0_Div * Vrun) < voltages[12] < (1.01 * GD0_Div * Vrun)):
            passes += 1
        else:
            fails += 1
            print("GD0 = %.2f\t, GD0_Lo = %.2f\t, GD0_Hi = %.2f\t" % (voltages[12], (0.99 * GD0_Div * Vrun), (1.01 * GD0_Div * Vrun)))

        if ((0.99 * PCLK2_Div * Vrun) < voltages[14] < (1.01 * PCLK2_Div * Vrun)):
            passes += 1
        else:
            fails += 1
            print("PCLK2 = %.2f\t, PCLK2_Lo = %.2f\t, PCLK2_Hi = %.2f\t" % (voltages[14], (0.99 * PCLK2_Div * Vrun), (1.01 * PCLK2_Div * Vrun)))

        if ((0.99 * PCLK1_Div * Vrun) < voltages[15] < (1.01 * PCLK1_Div * Vrun)):
            passes += 1
        else:
            fails += 1
            print("PCLK1 = %.2f\t, PCLK1_Lo = %.2f\t, PCLK1_Hi = %.2f\t" % (voltages[15], (0.99 * PCLK1_Div * Vrun), (1.01 * PCLK1_Div * Vrun)))

        if ((0.99 * PCLK0_Div * Vrun) < voltages[16] < (1.01 * PCLK0_Div * Vrun)):
            passes += 1
        else:
            fails += 1
            print("PCLK0 = %.2f\t, PCLK0_Lo = %.2f\t, PCLK0_Hi = %.2f\t" % (voltages[16], (0.99 * PCLK0_Div * Vrun), (1.01 * PCLK0_Div * Vrun)))

        if ((0.99 * RTD_P1_Div * Vrun) < voltages[17] < (1.01 * RTD_P1_Div * Vrun)):
            passes += 1
        else:
            fails += 1
            print("RTD_P1 = %.2f\t, RTD_P1_Lo = %.2f\t, RTD_P1_Hi = %.2f\t" % (voltages[17], (0.99 * RTD_P1_Div * Vrun), (1.01 * RTD_P1_Div * Vrun)))

        if ((0.99 * RG_Div * Vrun) < voltages[18] < (1.01 * RG_Div * Vrun)):
            passes += 1
        else:
            fails += 1
            print("RG = %.2f\t, RG_Lo = %.2f\t, RG_Hi = %.2f\t" % (voltages[18], (0.99 * RG_Div * Vrun), (1.01 * RG_Div * Vrun)))

        if ((0.99 * SCLK0_Div * Vrun) < voltages[19] < (1.01 * SCLK0_Div * Vrun)):
            passes += 1
        else:
            fails += 1
            print("SCLK0 = %.2f\t, SCLK0_Lo = %.2f\t, SCLK0_Hi = %.2f\t" % (voltages[19], (0.99 * SCLK0_Div * Vrun), (1.01 * SCLK0_Div * Vrun)))

        if ((0.99 * SCLK1_Div * Vrun) < voltages[20] < (1.01 * SCLK1_Div * Vrun)):
            passes += 1
        else:
            fails += 1
            print("SCLK1 = %.2f\t, SCLK1_Lo = %.2f\t, SCLK1_Hi = %.2f\t" % (voltages[20], (0.99 * SCLK1_Div * Vrun), (1.01 * SCLK1_Div * Vrun)))

        if ((0.99 * SCLK2_Div * Vrun) < voltages[21] < (1.01 * SCLK2_Div * Vrun)):
            passes += 1
        else:
            fails += 1
            print("SCLK2 = %.2f\t, SCLK2_Lo = %.2f\t, SCLK2_Hi = %.2f\t" % (voltages[21], (0.99 * SCLK2_Div * Vrun), (1.01 * SCLK2_Div * Vrun)))

        if ((0.99 * GD1_Div * Vrun) < voltages[22] < (1.01 * GD1_Div * Vrun)):
            passes += 1
        else:
            fails += 1
            print("GD1 = %.2f\t, GD1_Lo = %.2f\t, GD1_Hi = %.2f\t" % (voltages[22], (0.99 * GD1_Div * Vrun), (1.01 * GD1_Div * Vrun)))

        if ((0.99 * RTD_P0_Div * Vrun) < voltages[23] < (1.01 * RTD_P0_Div * Vrun)):
            passes += 1
        else:
            fails += 1
            print("RTD_P0 = %.2f\t, RTD_P0_Lo = %.2f\t, RTD_P0_Hi = %.2f\t" % (voltages[23], (0.99 * RTD_P0_Div * Vrun), (1.01 * RTD_P0_Div * Vrun)))

        if ((0.99 * OG_Div * Vrun) < voltages[25] < (1.01 * OG_Div * Vrun)):
            passes += 1
        else:
            fails += 1
            print("OG = %.2f\t, OG_Lo = %.2f\t, OG_Hi = %.2f\t" % (voltages[25], (0.99 * OG_Div * Vrun), (1.01 * OG_Div * Vrun)))

    else:
        print("Voltage %.2f and/or current %.2f out of bounds" % (Vset, Imon))
    print loop

print ("Tests Passed %i\t, Tests Failed %i\t" % (passes, fails))

#file.close()

print("Finished")


