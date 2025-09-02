# coding: UTF-8

import socket
import time
import tkinter.messagebox

BUFSIZE = 4096

class Lan:

    def __init__(self, timeout, gui=False):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        self.sock.settimeout(timeout)                                   #Timeout
        self.gui = gui

    #Open port
    def open(self, IP, port):
        ret = False

        try:
            self.sock.connect((IP, port))
            ret = True
        except Exception as e:
            if self.gui == True:
                tkinter.messagebox.showerror("Open Error", e)
            else:
                print("Open error")
                print(e)
        
        return ret

    #Close port
    def close(self):
        ret = False

        try:
            self.sock.close()
            ret = True
        except Exception as e:
            if self.gui == True:
                tkinter.messagebox.showerror("Close Error", e)
            else:
                print("Close error")
                print(e)
        
        return ret

    #Send command
    def sendMsg(self, strMsg):
        ret = False

        try:
            strMsg = strMsg + '\r\n'                #Add a terminator, CR+LF, to transmitted command
            self.sock.send(bytes(strMsg, 'utf-8'))  #Convert to byte type and send
            ret = True
        except Exception as e:
            if self.gui == True:
                tkinter.messagebox.showerror("Send Error", e)
            else:
                print("Send Error")
                print(e)

        return ret
    
    #Receive
    def receiveMsg(self, timeout):

        msgBuf = bytes(range(0))                    #Received Data

        try:
            start = time.time()                     #Record time for timeout
            while True:
                rcv  = self.sock.recv(BUFSIZE)
                rcv = rcv.strip(b"\r")              #Delete CR in received data
                if b"\n" in rcv:                    #End the loop when LF is received
                    rcv = rcv.strip(b"\n")          #Ignore the terminator CR
                    msgBuf = msgBuf + rcv
                    msgBuf = msgBuf.decode('utf-8')
                    break
                else:
                    msgBuf = msgBuf + rcv
                
                #Timeout processing
                if  time.time() - start > timeout:
                    msgBuf = "Timeout Error"
                    break
        except Exception as e:
            if self.gui == True:
                tkinter.messagebox.showerror("Receive Error", e)
            else:
                print("Receive Error")
                print(e)
            msgBuf = "Error"

        return msgBuf
    
    #Transmit and receive commands
    def SendQueryMsg(self, strMsg, timeout):
        ret = Lan.sendMsg(self, strMsg)
        if ret:
            msgBuf_str = Lan.receiveMsg(self, timeout)  #Receive response when command transmission is succeeded
        else:
            msgBuf_str = "Error"

        return msgBuf_str