# coding: UTF-8

from lan import Lan
from ftplib import FTP
from datetime import datetime
import os
import pandas as pd
import redis
import json
import time
class HIOKI_Agent():
    def __init__(self,deviceIP,devicePort,deviceTimeout,mahineID,hostIP):
        self.deviceIP       = deviceIP
        self.devicePort     = devicePort
        self.deviceTimeout  = deviceTimeout
        self.machineID      = mahineID
        self.hostIP         = hostIP 
        self.red            = redis.Redis(host=self.hostIP,port=6379,db=0)
        self.record         = False
    def connectcheck(self):
        lan = Lan(self.deviceTimeout)
        if not lan.open(self.deviceIP, self.devicePort):
            return "fail"
        return "success"
    def startrecord(self):
        command = ":STARt"
        lan = Lan(self.deviceTimeout)
        if not lan.open(self.deviceIP, self.devicePort):
            return "fail"
        lan.sendMsg(command)
        # lan.close()
        return "success"
    def stoprecord(self):
        command = ":ABORT"
        lan = Lan(self.deviceTimeout)
        if not lan.open(self.deviceIP, self.devicePort):
            return "fail"
        lan.sendMsg(command)
        # lan.close()
        return "success"    
    def getdata(self):
        ftp_host = "172.16.10.10"
        folder_path = "/sdcard/HIOKI/LR8450/DATA/"
        folder_path ="/usb/HIOKI/LR8450/DATA/"
        ftp = FTP(ftp_host)
        ftp.login()
        ftp.cwd(folder_path)
        today_str = datetime.now().strftime("%y-%m-%d")
        local_download_path = "./" 
        # 找到名字是今天日期的資料夾，有找到的話就cd到裡面
        try:
            for name, facts in ftp.mlsd():
                if facts.get("type") == "dir" and name == today_str:
                    ftp.cwd(name)
                    break
        except:
            pass
        files = []
        # 找到最新的csv檔
        try:
            for name, facts in ftp.mlsd():
                if facts.get("type") == "file":
                    modify_time = facts.get("modify")  # 例：'20250902123000'
                    if modify_time:
                        dt = datetime.strptime(modify_time, "%Y%m%d%H%M%S")
                        files.append((name, dt))
        except:
            file_names = ftp.nlst()
            for name in file_names:
                files.append((name, None))
        if not files:
            print("folder is empty")
            ftp.quit()
            exit()
        # 把最新的CSV下載另存成data.csv
        latest_file = max(files, key=lambda x: x[1] or datetime.min)
        print(f"latest file {latest_file}")
        dataname = "data.csv"
        local_file_path = os.path.join(local_download_path, dataname)
        with open(local_file_path, 'wb') as f:
            ftp.retrbinary(f'RETR {latest_file[0]}', f.write)
        ftp.quit()
    def processdata(self):
        df = pd.read_csv("data.csv",skiprows=11)
        dfheader = df.columns.to_list()
        currentdata = {}
        if "R1-1[A]" in dfheader:
            currentdata["R1-1[A]"] = df["R1-1[A]"].to_list()
        if "R1-2[A]" in dfheader:
            currentdata["R1-2[A]"] = df["R1-2[A]"].to_list()
        return currentdata
    def connecthost(self):
        try:
            self.red = redis.Redis(host=self.hostIP,port=6379,db=0)
            print("Succes connect host server, work on auto mode")
            return "success"
        except:
            print("Fail to connect host server, work on manual mode ...")
            return "fail"
    def workflow(self):
        machinestatus = self.red.get(f'{self.machineID}_status')
        machinestatus = json.loads(machinestatus)
        state         = machinestatus["machine"]["value"]
        if state != "stay":
            if self.record is False:
                self.startrecord()
                self.record = True
        else:
            if self.record is True :
                self.stoprecord()
                time.sleep(7)
                self.getdata()
                currentdata  = self.processdata()
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                currentdata["update_time"] = current_time
                self.red.set(f'{self.machineID}_current',json.dumps(currentdata))
                self.record = False

if __name__ == '__main__':
    agent = HIOKI_Agent("172.16.10.10",8802,10,"FCS-150","192.168.1.50")
    connectstatus = agent.connecthost()
    if connectstatus != "success":
        while True:
            print("send command")
            usercommand = input()
            if usercommand == "start":
                agent.startrecord()
            if usercommand == "stop":
                agent.stoprecord()
                time.sleep(7)
                agent.getdata()
                print("getdata finish")
    else : 
        while True:
            time.sleep(1)
            agent.workflow()

