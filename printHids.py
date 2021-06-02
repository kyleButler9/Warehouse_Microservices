from donationBanner import *
import tkinter as tk
import sys
import os
import tkinter as tk
from config import DBI
import psycopg2
import socket
class GetPrinterName(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        tk.Label(parent,text='Printer Name').pack()
        self.printer_name=kwargs['printer_name']
        self.e=tk.Entry(parent,width=30)
        self.e.pack()
        self.e.insert(0,'USB003 ZPL')
        self.set_it = tk.Button(parent,
            text='Set Printer Name',
            width = 20,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.printIt.bind('<Button-1>',self._setit)
    def _setit(self,event):
        self.printer_name.set(self.e.get())
        return self
    def get(self):
        return self.printer_name.get()

class PrintHids(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        self.donationIDVar = tk.StringVar(parent)
        self.printer=kwargs['printer']
        DonationBanner(parent,ini_section=kwargs['ini_section'],donationIDVar=self.donationIDVar)
        tk.Label(parent,text='How Many Hids?').pack()
        self.hidCount = tk.Entry(parent,width=10)
        self.hidCount.pack()
        self.printIt = tk.Button(parent,
            text='Print',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.printIt.bind('<Button-1>',self.printToZebra)
        self.printIt.pack()
        self.err = tk.StringVar(parent)
        self.errMsg = tk.Label(parent,textvariable=self.err).pack()
    def printToZebra(self,event):
        try:
            hidCount = int(self.hidCount.get())
        except ValueError:
            self.err.set("Count: " +self.hidCount.get()+" \ncan't be converted to an integer.")
            self.hidCount.delete(0,'end')
            return self
        try:
            maxmin = self.UpdateHidsLog(hidCount)
            getLotNumber = \
            """
            SELECT lotnumber from donations where donation_id = %s;
            """
            lotnum = self.fetchone(getLotNumber,self.donationIDVar.get())[0]
            #headerFile = open('header.prn','r')
            #header = headerFile.read()
            # I got header by printing in python the reading of the non-repeating lenguage of the print statement
            # from the zebra print from ip app
            header = 'ï»¿\x10CT~~CD,~CC^~CT~\n^XA~TA000~JSN^LT0^MNW^MTT^PON^PMN^LH0,0^JMA^PR4,4~SD25^JUS^LRN^CI0^XZ'
            file = open('out.prn','w')
            file.write(header)
            #mysocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            #host='192.168.8.186'
            #port=9100
            #mysocket.connect((host, port))
            for i in range(maxmin[1]+1,maxmin[0]+1):
                file.write(self.hidTemplate(lotnum,i))
                #mysocket.send(self.hidTemplate(lotnum,i).encode('UTF-8'))
            #mysocket.close()
            file.close()
        except TypeError:
            self.err.set('No lotnumber associated with that donation...')
        #ip='192.168.8.186'
        ip=None
        if ip is None:
            self.ZebraViaUSB(self.printer.get())
        else:
            file = open('out.prn','r')
            out=file.read()
            self.ZebraViaNet(out,'192.168.8.186')
    def ZebraViaUSB(self,PRINTER_NAME):
        try:
            os.system("powershell \" Get-Content -Path .\out.prn | Out-Printer -Name '{}'\"".format(PRINTER_NAME))
        except:
            self.err.set('problem printing.')
        finally:
            return self
    def ZebraViaNet(self,zpl,ip):
        mysocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        host = ip
        port = 9100
        try:
            mysocket.connect((host, port)) #connecting to host
            print('connected!')
            #mysocket.send(b"^XA^A0N,50,50^FO50,50^FDSocket Test^FS^XZ")#using bytes
            print(zpl)
            #mysocket.send(zpl)
            mysocket.send(zpl.encode('UTF-8'))
            mysocket.close() #closing connection
        except:
        	print("Error with the connection at zebra IP: " + host )
        finally:
            pass
    def UpdateHidsLog(self,max):
        try:
            logStatement = \
            """
            With currentMax as (SELECT maxHidIter,donation_id from donations
                                WHERE donation_id = %s)
            UPDATE donations
            SET maxHidIter = maxHidIter + %s
            WHERE donation_id = (select donation_id from currentMax)
            RETURNING maxHidIter,(select maxHidIter from currentMax);
            """
            maxmin = self.fetchone(logStatement,self.donationIDVar.get(),max)
            self.conn.commit()
            return maxmin
        except (Exception, psycopg2.DatabaseError) as error:
             self.err.set(error)
             return None

    def hidTemplate(self,prefix,iter):
        Hid = \
"""
^XA
^MMT
^PW450
^LL0180
^LS0
^BY3,3,79^FT83,114^BCN,,Y,N
^FD>;{}>6{}-{}^FS
^PQ1,0,1,Y^XZ""".format(str(prefix)[:-1],str(prefix)[-1],iter)
        return Hid

if __name__ == "__main__":
    root = tk.Tk()
    root.title("HD ID Printer")
    printer = tk.StringVar(root)
    if sys.argv[1]:
        printer.set(sys.argv[1])
    else:
        pop_up=tk.Toplevel(root)
        pn=GetPrinterName(pop_up,printer_name=printer)
    app = PrintHids(root,ini_section='local_launcher',printer=printer)
    app.mainloop()
