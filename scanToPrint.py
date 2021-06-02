import tkinter as tk
import psycopg2
from config import config,dbOps
from queryGoogleSheets import QueryOverview_cColumn
import sqlStatements
import pandas as pd
import socket
from os import path,system
from datetime import date

class GUI:
    def __init__(self,**kwargs):
        self.connectToDB(kwargs['ini_section'])
        self.tableName = kwargs['table']
        if 'zebraIP' in kwargs:
            self.zebraIP = kwargs['zebraIP']
        elif 'zebraName' in kwargs:
            self.zebraName = kwargs['zebraName']
        else:
            print('zebra info not provided.')
        self.root = tk.Tk()
        self.root.geometry("500x150")
        self.root.title('Sales Process Appendage')
        self.UpdateOrgs(QueryOverview_cColumn())
        self.CreateFields()
        self.pallet.insert(0,self.GetLastPalletNumber())
        self.Start()
    def GetIncompleteOrgs(self):
        sql = \
        """
        SELECT org_name
        FROM orgs
        WHERE not complete;
        """
        self.cur.execute(sql)
        incompleteOrgs = []
        for item in self.cur.fetchall():
            incompleteOrgs.append(item[0])
        return incompleteOrgs
    def UpdateOrgsOld(self,sheetYield):
        sql1 = \
        """
        SELECT org_name
        FROM orgs;
        """
        self.cur.execute(sql1)
        inAlready=[]
        for item in self.cur.fetchall():
            inAlready.append(item[0])
        orgNames = []
        orgCompletion = []
        print(type(sheetYield[0][1]))
        for item in sheetYield:
            orgNames.append(item[0])
            orgCompletion.append(item[1])

        newOrgs = set(orgNames) - set(inAlready)
        reducedSheetYield = []
        for item in sheetYield:
            if item[0] in newOrgs:
                reducedSheetYield.append(item)
        sql2 = \
        """
        INSERT INTO orgs(org_name,complete)
        VALUES(%s,%s);
        """
        for org in reducedSheetYield:

            self.cur.execute(sql2,(org[0],org[1],))
        self.conn.commit()
    def UpdateOrgs(self,sheetYield):
        self.cur.execute(sqlStatements.sqlTempTableCreation)
        self.cur.executemany(sqlStatements.sqlUploadMany,sheetYield)
        self.cur.execute(sqlStatements.sqlUpsert)
        self.conn.commit()
        pass
    def updateCompletionStatus(self):
        sql = \
        """
        UPDATE orgs
        Set complete = %s
        WHERE org_name = %s;
        """
        try:
            self.cur.execute(sql,(self.isChecked.get(),self.dest.get()))
            print("updated " + str(self.cur.rowcount) + " rows.")
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            return self
    def CreateFields(self):
        self.isChecked = tk.BooleanVar()
        self.checkedBox = tk.Checkbutton(text='Complete',
                                    variable=self.isChecked,
                                    height = 5,
                                    width=20)
        self.dest = tk.StringVar()
        self.dest.set('select a value:')
        self.destDropdown = tk.OptionMenu(self.root,self.dest,*self.GetIncompleteOrgs())
        self.palletLabel = tk.Label(text="Pallet ID #")
        self.pidLabel = tk.Label(text="PID")
        self.catLabel = tk.Label(text="Category")
        self.qualityLabel = tk.Label(text="Quality")

        self.quality = tk.Entry(fg="black", bg="white", width=15)
        self.cat = tk.Entry(fg="black", bg="white", width=15)
        self.pid = tk.Entry(fg="black", bg="white", width=15)
        self.pallet = tk.Entry(fg="black", bg="white", width=15)
        self.insertAndPrint = tk.Button(
            text="Insert PID and Print",
            width=15,
            height=2,
            bg="blue",
            fg="yellow",
        )
        self.justInsert = tk.Button(
            text="Just Insert PID",
            width=15,
            height=2,
            bg="blue",
            fg="yellow",
        )
        self.exportCSV = tk.Button(
            text="Export CSV for Dest",
            width=15,
            height=2,
            bg="blue",
            fg="yellow",
        )
        self.insertAndPrint.bind('<Button-1>', self.InsertAndPrint)
        self.justInsert.bind('<Button-1>', self.JustInsert)
        self.exportCSV.bind('<Button-1>', self.ExportCSV)
        self.root.bind('<Return>',self.InsertAndPrint)
        self.destDropdown.grid(row=0,column=0,columnspan=1)
        self.palletLabel.grid(row=2,column=2)
        self.pallet.grid(row=2,column=3)
        self.pidLabel.grid(row=2,column=0)
        self.pid.grid(row=2,column=1)
        self.catLabel.grid(row=1,column=2)
        self.cat.grid(row=1,column=3)
        self.qualityLabel.grid(row=1,column=0)
        self.quality.grid(row=1,column=1)
        self.insertAndPrint.grid(row=3,column=0)
        self.justInsert.grid(row=3,column=1)
        self.exportCSV.grid(row=3,column=3)
        self.checkedBox.grid(row=3,column=2)
    def ExportCSV(self,event):
        try:
            sql = \
            """
            SELECT pid
            FROM pids
            INNER JOIN orgs ON pids.org_id = orgs.org_id
            WHERE org_name = '{}'
            """
            dest = self.dest.get()
            df = pd.read_sql_query(sql.format(dest),self.conn)
            file = open(path.join(path.expanduser('~'),
                'Downloads\{}.csv'.format(dest[:6])),'w')
            print(df)
            file.write(df.to_csv(index=False))
            file.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            self.updateCompletionStatus()
            pass
    def connectToDB(self,ini_section):
        try:
            # read database configuration
            params = config(ini_section=ini_section)
            # connect to the PostgreSQL database
            self.conn = psycopg2.connect(**params)
            # create a new cursor
            self.cur = self.conn.cursor()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            return self
    def InsertAndPrint(self,event):
        try:
            sql = \
                """
                INSERT INTO pids(pid,category,quality,pallet,org_id)
                VALUES (
                    %s,%s,%s,%s,
                    (SELECT org_id FROM orgs WHERE org_name = %s)
                    )
                RETURNING device_id;
                """
            pallet = str(self.pallet.get())
            pid = str(self.pid.get())
            cat = str(self.cat.get())
            quality = str(self.quality.get())
            dest = str(self.dest.get())

            self.pid.delete(0,15)
            templateFile = open('Label.prn','r')
            file = open('out.prn','w')
            template = templateFile.read()
            dashIndex = pid.index('-')
            zpl = template.format(pid[:dashIndex+1],
                pid[dashIndex+1:],
                quality,
                cat,
                date.today().strftime("%m/%d/%Y"))
            if hasattr(self,'zebraIP'):
                self.SendToZebraIP(zpl)
            elif hasattr(self,'zebraName'):
                file.write(zpl)
                file.close()
                self.SendToZebraUSB()
            templateFile.close()


            self.cur.execute(sql,(pid,cat,quality,pallet,dest))
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            pass
    def JustInsert(self,event):
        try:
            sql = \
                """
                INSERT INTO pids(pid,category,quality,pallet,org_id)
                VALUES (
                    %s,%s,%s,%s,(SELECT org_id FROM orgs WHERE org_name = %s))
                RETURNING device_id;
                """
            pallet = self.pallet.get()
            pid = self.pid.get()
            cat = self.cat.get()
            quality = self.quality.get()
            dest = self.dest.get()

            self.pid.delete(0,15)

            self.cur.execute(sql,(pid,cat,quality,pallet,dest))
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            pass
    def SendToZebraIP(self,zpl):
        mysocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        host = self.zebraIP
        port = 9100
        try:
            mysocket.connect((host, port)) #connecting to host
        	#mysocket.send(b"^XA^A0N,50,50^FO50,50^FDSocket Test^FS^XZ")#using bytes
            mysocket.send('${' + zpl + '}$')
            mysocket.close() #closing connection
        except:
        	print("Error with the connection at zebra IP: " + self.zebraIP )
        finally:
            pass
    def SendToZebraUSB(self):
        system("powershell \" Get-Content -Path .\out.prn | Out-Printer -Name '{}'\"".format(self.zebraName))
    def GetLastPalletNumber(self):
        try:
            sql = \
            """
            SELECT MAX(pallet)
            FROM pids;
            """
            self.cur.execute(sql)
            pallet = self.cur.fetchone()[0]
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            pallet = 'error'
        finally:
            return str(pallet)

    def Start(self):
        self.root.mainloop()
    def CloseGUI(self,event):
        self.root.destroy()
if __name__ == "__main__":
    gui = GUI(ini_section='sales_appendage',
            table='pids',
            zebraName='Zout')
            #zebraIP="10.80.209.106")
