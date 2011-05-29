import socket, random
import datetime,urllib,time
import subprocess
import os
from math import *
import calc_irc
class bot:
    def __init__(self):
        self.msg_channel=""
        self.connect("Sobot")
        subprocess.Popen(self.check_for_messages(),()).pid
        print "running"
    def sendMessage(self,channel, message):
        self.irc.send('PRIVMSG ' + channel + ' :' + message + '\r\n')
    def connect(self,nick):
        network = 'irc.freenode.org'
        port = 6667
        self.irc = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
        self.irc.connect ( ( network, port ) )
        print self.irc.recv ( 4096 )
        self.irc.send ( 'NICK '+nick+'\r\n' )
        self.irc.send ( 'USER botty botty botty :yaib\r\n' )
        self.irc.send ( 'JOIN #Silasle-bot-management\r\n' )
        if nick=="Sobot":
            self.irc.send ( 'PRIVMSG NickServ : identify xw9md99\r\n' )
    def check_for_messages(self):
        ops=["Silasle","Siekacz"]
        print "checking"
        while True:
            try:
                data = self.irc.recv ( 4096 )
                self.data=data
                try:
                    user=(data.split(":")[1]).split("!")[0]
                except:
                    user="unknown"
                try:    
                    self.msg_channel=(data.split("PRIVMSG ")[1]).split(":")[0]
                    print self.msg_channel,user
                except:
                    pass
                channel=self.msg_channel
                print data.split()
                if "#Silasle-bot-management" in self.msg_channel:
                    if user in ops:
                        print user, ops
                        if data.find ( '!bot quit' ) != -1:
                            #sendMessage(channel, 'Fine, if you dont want me\r\n' )
                            break
                        if data.find ( '!reload' ) != -1:
                            reload(calc_irc)
                            self.sendMessage(self.msg_channel, 'Reloaded all modules\r\n' )
                        if data.find ( '!join' ) != -1:
                            channel_to_join=data.split()[4]
                            self.irc.send ( 'JOIN '+channel_to_join+'\r\n' )
                        if data.find ( '!part' ) != -1:
                            channel_to_join=data.split()[4]
                            self.irc.send ( 'PART '+channel_to_join+'\r\n' )
                        if data.find ( '!command' ) != -1:
                            command=str(data).split("!command ")[1]
                            print command
                            process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
                            os.waitpid(process.pid, 0)
                            output = process.stdout.read().strip()
                            print output
                            self.irc.send('PRIVMSG ' + self.msg_channel + ' :' + output + '\r\n')
                if data.find ( '!calc' ) != -1:
                    calc_irc.calculate(self)
    
    
                if data.find ( 'ping' ) != -1:
                      server=data.split(":")[1]
                      server=server.split()[0]
                      print "server:",server
                      print "Message :PONG :"+server
                      self.irc.send("PONG :"+server)
                      print "Ping sent..."
                print data
            except:
                pass
bot()