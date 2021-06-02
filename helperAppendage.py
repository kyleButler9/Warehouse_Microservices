import tkinter as tk
import psycopg2
from config import DBI
from sql import *
import pyperclip
import sys
from os.path import join,dirname,isdir,exists
from os import path
import os
import subprocess
import re

class TechStation:
    def __init__(self):
        fileDir = path.dirname(__file__)
        self.outputDir = path.join(fileDir,'output')
        self.outMessage = \
        """
        PID:\t{}\n
        Serial Number:\t{}\n
        Product Key:\t{}\n
        """
    def writeSerialNumberProductKeyToFile(self,*args):
        try:
            if not path.exists(self.outputDir):
                os.mkdir(self.outputDir)
            outFilePath = join(self.outputDir,"serial Number Product Key.txt")
            outFile = open(outFilePath,'w')
            outMessage = self.outMessage.format(*args)
            outFile.write(outMessage)
            outFile.close()
        except:
            print(outFilePath+" is probably open on your computer")
            print("so i can't write to it.")
        finally:
            return outFilePath
if __name__ == "__main__":
    TechStation = TechStation()
    DBI = DBI(ini_section='local_appendage')
    SN_str = subprocess.run("wmic bios get serialnumber",
            shell=True,
            capture_output=True).stdout.decode('utf-8')
    deviceSN = re.search('\n(.+?) ',SN_str).group(1)
    snpk = DBI.fetchone(TechStationSQL.licenseFromSN,deviceSN)
    outFilePath = TechStation.writeSerialNumberProductKeyToFile(*snpk)
    subprocess.run("start notepad "+outFilePath,shell=True)
    subprocess.run(r"powershell -ExecutionPolicy Bypass -File \\server\Programs\ks\snpk.ps1",shell=True)
