#!/usr/bin/env python

import serial
import time

from Tkinter import *

default_speed = 2.0

def mph2pw( mph ):
    if mph > 5.0:
        mph = 5.0;
    lpw = -0.0620747 * mph + 0.92;
    # linear regression is not perfect
    if mph <= 0.5:
        lpw = 1
    return lpw


class App:
    def __init__(self, master):
        self.running = False

        self.currentspeed = default_speed
        self.currentspeedString = StringVar()
        self.currentspeedString.set(str(self.currentspeed))

        self.currentdistance = 0.0
        self.currentdistanceString = StringVar()
        self.currentdistanceString.set(str(self.currentdistance))

        self.seconds = 0.0
        self.miles = 0.0
        self.prev_speed = 0.0
        
        self.starttime = time.time()
        self.endtime = time.time()
        
        self.ser = serial.Serial('/dev/ttyACM0', baudrate=115200, dsrdtr=False)
        self.ser.setDTR(False)

        frame = Frame(master);
        frame.pack()

        self.start = Button(frame, text="START", fg="green", command=self.start)
        self.start.pack(side=LEFT)

        self.stop = Button(frame, text="STOP", fg="red", command=self.stop)
        self.stop.pack(side=LEFT)

        self.quit = Button(frame, text="QUIT", command=frame.quit)
        self.quit.pack(side=LEFT)

        self.speedup = Button(frame, text="Speed +0.5mph", command=self.speedup)
        self.speedup.pack(side=LEFT)

        self.slowdown = Button(frame, text="Speed -0.5mph", command=self.slowdown)
        self.slowdown.pack(side=LEFT)

        self.speedlabelLabel = Label(frame, text="Speed: ")
        self.speedlabelLabel.pack(side=LEFT)

        self.speedLabel = Label(frame, textvariable=self.currentspeedString)
        self.speedLabel.pack(side=LEFT)

        self.distancelabelButton = Button(frame, text="Distance: ", command=self.refresh)
        self.distancelabelButton.pack(side=LEFT)

        self.distanceLabel = Label(frame, textvariable=self.currentdistanceString)
        self.distanceLabel.pack(side=LEFT)

        self.resetButton = Button(frame, text="RESET", fg="red", command=self.reset)
        self.resetButton.pack(side=LEFT)

    def sendspeed(self):
        self.update_odometer(self.currentspeed)
        pw = mph2pw(self.currentspeed)
        self.ser.write(str(pw))

    def update_odometer(self, speed):
        self.endtime = time.time()
        duration = self.endtime - self.starttime
        self.miles = self.miles + self.prev_speed*duration/3600
        if(self.prev_speed > 0.001):
            self.seconds = self.seconds + duration

        self.starttime = self.endtime
        self.prev_speed = speed
        self.currentdistanceString.set(str(self.miles))
        root.update_idletasks()   

    def setspeed(self, newspeed):
        if(newspeed <= 6.0 and newspeed >= 0.0):
            self.currentspeed = newspeed
            self.currentspeedString.set(str(self.currentspeed))
            root.update_idletasks()
        else:
            print "WARNING: rejected attempt to set speed to "+str(newspeed)+": out of bounds."

    def start(self):
        self.running = True
        self.sendspeed()
        
    def stop(self):
        self.running = False
        self.update_odometer(0)
        pw = mph2pw(0)
        self.ser.write(str(pw))

    def modifyspeed(self, increment):
        self.setspeed(self.currentspeed + increment);
        
    def speedup(self):
        self.modifyspeed(0.5)
        if(self.running):
            self.sendspeed()

    def slowdown(self):
        self.modifyspeed(-0.5)
        if(self.running > 0):
            self.sendspeed()

    def refresh(self):
        self.update_odometer(self.currentspeed)

    def reset(self):
        self.miles = 0
        self.refresh()
        
root=Tk()
root.title("Treadmill Controller")

app=App(root)
root.mainloop()

