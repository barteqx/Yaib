#!/usr/bin/env python
import socket, random
import datetime,urllib,time
import subprocess
import os
from math import *
def calculate(self):
                    channel=self.msg_channel
                    print "calculating\n"
                    self.sendMessage(channel, 'Test message added' )
                    if "answer to the universe and everything" in self.data:
                       self.sendMessage(channel, 'Let google help you: http://www.google.co.uk/search?aq=0&oq=the+answer+to&sourceid=chrome&ie=UTF-8&q=the+answer+to+life+the+universe+and+everything\r\n' )
                    else:
                       print "clac"
                       if "sqrt" in str(self.data.split()[4]):
                         calc=str(self.data.split()[4]).split("sqrt(")[1]
                         calc=calc.split(")")[0]
                         calc=sqrt(float(eval(calc)))
                         calc=eval(str(calc)+(self.data.split()[4]).split(")")[1])
                         if calc==42:
                           self.sendMessage(channel, 'You found the answer to the universe and everything!\r\n' )
                         self.sendMessage(channel, 'Ans: ' + str(calc)+ '\r\n' )
                       elif "=" in str(self.data.split()[4]):
                        t0 = datetime.datetime.now()
                        self.sendMessage(channel, ''+self.data.split()[4]+'\r\n' )
                        if "x" in self.data.split()[4]:
                            calc=self.data.split()[4]
                            x=0
                            while 1:
                                 x=x+1
                                 print x,calc
                                 a=eval(calc)
                                 print a
                                 if a==True or a==0:
                                    self.sendMessage(channel, 'Ans'+str(x)+'\r\n' )
                                    break
                                 delta_t = datetime.datetime.now() - t0
                                 delta_t=str(delta_t).split(".")[0]
                                 delta_t=str(delta_t).split(":")[2]
                                 if int(delta_t)>3:
                                    self.sendMessage(channel, 'dont work, or takes to long time\r\n' )
                                    print "dont work, or takes to long time"
                                    break
                        else:
                            self.sendMessage(channel, 'I can only do equations whit "x"\r\n' )
                       else:
                        try:
                         print "kj"
                         self.sendMessage(channel, 'Ans: ' + str(eval(self.data.split()[4]))+ '\r\n' )
                        except:
                             self.sendMessage(channel, 'Error in calculation\r\n' )