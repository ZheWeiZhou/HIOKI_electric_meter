# -*- coding: utf-8 -*-

"""
This program connects to the instrument and sends and receives commands.
Enter the command and click the [Transmit and Receive] button to send it.
If the command has a response (command contains "?"), the response is displayed in the textbox.

System requirements (software)
    Python 3.7 Windows

Required packages
    None
"""

import tkinter
import lan


class SampleWindow(tkinter.Frame):

    TIMEOUT_DEFAULT = 1                                                                 # Timeout on blocking socket operations(1 sec)

    def __init__(self, window):
        """ Constructor """
        super().__init__(window)
        window.title("Sample")
        window.geometry("497x309")
        self.__Label1 = None
        self.__Label2 = None
        self.__Label4 = None
        self.__Label5 = None
        self.__Label6 = None
        self.__TextBox1 = None
        self.__TextBox2 = None
        self.__TextBox3 = None
        self.__TextBox4 = None
        self.__TextBox5 = None
        self.__Scrollbar1 = None
        self.__Scrollbar2 = None
        self.__Button1 = None
        self.__Button2 = None
        self.__Button3 = None
        self.__Button4 = None
        self.__Communication = None
        self.__CreateWidgets()
        self.__TextBox1.insert(tkinter.END, "192.168.0.1")
        self.__TextBox2.insert(tkinter.END, "3500")
        self.__TextBox3.insert(tkinter.END, "*IDN?")
        self.__TextBox4.insert(tkinter.END, "1")
        # Process for Enable/Disable on the buttons and textboxes
        self.__Button1.configure(state=tkinter.NORMAL)
        self.__Button2.configure(state=tkinter.DISABLED)
        self.__Button3.configure(state=tkinter.DISABLED)
        self.__TextBox1.configure(state=tkinter.NORMAL)
        self.__TextBox2.configure(state=tkinter.NORMAL)
        self.__TextBox3.configure(state=tkinter.DISABLED)
        self.__TextBox4.configure(state=tkinter.DISABLED)
        self.__TextBox5.configure(state=tkinter.DISABLED)

    def __CreateWidgets(self):
        """ Create widgets """
        self.__Label1 = tkinter.Label(text="IP address")
        self.__Label1.place(anchor=tkinter.NE, x=84, y=18)
        self.__TextBox1 = tkinter.Entry()
        self.__TextBox1.place(x=87, y=18, width=102, height=19)
        self.__Label2 = tkinter.Label(text="Port")
        self.__Label2.place(anchor=tkinter.NE, x=241, y=18)
        self.__TextBox2 = tkinter.Entry(justify=tkinter.RIGHT)
        self.__TextBox2.place(x=244, y=18, width=51, height=19)
        self.__Label4 = tkinter.Label(text="Commands")
        self.__Label4.place(anchor=tkinter.NE, x=84, y=58)
        self.__TextBox3 = tkinter.Entry()
        self.__TextBox3.place(x=87, y=58, width=229, height=19)
        self.__Label5 = tkinter.Label(text="Timeout")
        self.__Label5.place(anchor=tkinter.NE, x=84, y=83)
        self.__TextBox4 = tkinter.Entry(justify=tkinter.RIGHT)
        self.__TextBox4.place(x=87, y=83, width=51, height=19)
        self.__Label6 = tkinter.Label(text="sec")
        self.__Label6.place(x=141, y=83)
        self.__TextBox5 = tkinter.Text(wrap=tkinter.NONE)
        self.__TextBox5.place(x=11, y=119, width=298, height=168)
        self.__Scrollbar1 = tkinter.Scrollbar(orient=tkinter.VERTICAL, command=self.__TextBox5.yview)
        self.__Scrollbar1.place(x=310, y=119, width=16, height=160)
        self.__TextBox5["yscrollcommand"] = self.__Scrollbar1.set
        self.__Scrollbar2 = tkinter.Scrollbar(orient=tkinter.HORIZONTAL, command=self.__TextBox5.xview)
        self.__Scrollbar2.place(x=11, y=280, width=298, height=16)
        self.__TextBox5["xscrollcommand"] = self.__Scrollbar2.set
        self.__Button1 = tkinter.Button(text="Connect", command=self.__Button1_Click)
        self.__Button1.place(x=331, y=12, width=73, height=30)
        self.__Button2 = tkinter.Button(text="Disconnect", command=self.__Button2_Click)
        self.__Button2.place(x=410, y=12, width=73, height=30)
        self.__Button3 = tkinter.Button(text="Transmit and Receive", command=self.__Button3_Click)
        self.__Button3.place(x=331, y=52, width=152, height=50)
        self.__Button4 = tkinter.Button(text="Clear", command=self.__Button4_Click)
        self.__Button4.place(x=331, y=119, width=73, height=30)

    def __Button1_Click(self):
        """ Events when "Connect" button is clicked """
        ip = self.__TextBox1.get()
        port = int(self.__TextBox2.get())
        # Create a Lan object
        self.__Communication = lan.Lan(self.TIMEOUT_DEFAULT, True)
        # Connect
        if not self.__Communication.open(ip, port):
            return
        # Process for Enable/Disable on the buttons and textboxes
        self.__Button1.configure(state=tkinter.DISABLED)
        self.__Button2.configure(state=tkinter.NORMAL)
        self.__Button3.configure(state=tkinter.NORMAL)
        self.__TextBox1.configure(state=tkinter.DISABLED)
        self.__TextBox2.configure(state=tkinter.DISABLED)
        self.__TextBox3.configure(state=tkinter.NORMAL)
        self.__TextBox4.configure(state=tkinter.NORMAL)

    def __Button2_Click(self):
        """ Events when "Disconnect" button is clicked """
        # Disconnect
        self.__Communication.close()
        # Process for Enable/Disable on the buttons and textboxes
        self.__Button1.configure(state=tkinter.NORMAL)
        self.__Button2.configure(state=tkinter.DISABLED)
        self.__Button3.configure(state=tkinter.DISABLED)
        self.__TextBox1.configure(state=tkinter.NORMAL)
        self.__TextBox2.configure(state=tkinter.NORMAL)
        self.__TextBox3.configure(state=tkinter.DISABLED)
        self.__TextBox4.configure(state=tkinter.DISABLED)

    def __Button3_Click(self):
        """ Events when "Transmit and Receive" button is clicked """
        self.__Button3.configure(state=tkinter.DISABLED)
        command = self.__TextBox3.get()
        timeout = int(self.__TextBox4.get())
        self.__TextBox5.configure(state=tkinter.NORMAL)
        self.__TextBox5.insert(tkinter.END, "<< " + command + "\n")                     # Output logs of transmitting data
        self.__TextBox5.see(tkinter.END)
        self.__TextBox5.configure(state=tkinter.DISABLED)
        if "?" in command:                                                              # If the command contains "?"
            msgBuf = self.__Communication.SendQueryMsg(command, timeout)                # Transmit and receive commands
            self.__TextBox5.configure(state=tkinter.NORMAL)
            self.__TextBox5.insert(tkinter.END, ">> " + msgBuf + "\n")                  # Output logs of receiving data
            self.__TextBox5.see(tkinter.END)
            self.__TextBox5.configure(state=tkinter.DISABLED)
        else:
            self.__Communication.sendMsg(command)                                       # Transmit commands
        self.__Button3.configure(state=tkinter.NORMAL)

    def __Button4_Click(self):
        """ Events when "Clear" button is clicked """
        # Clear the textbox
        self.__TextBox5.configure(state=tkinter.NORMAL)
        self.__TextBox5.delete(1.0, tkinter.END)
        self.__TextBox5.configure(state=tkinter.DISABLED)


if __name__ == "__main__":
    root = tkinter.Tk()
    window = SampleWindow(root)
    window.mainloop()
