from config import DBI;
import tkinter as tk
import datetime
#from demoWriteSheet import *
import psycopg2
from Google_Sheets_Interface import *
from Reporting_Station import *
from Info_Queries import *
class ProcessedHardDrives(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        self.parent=parent
        tk.Frame.__init__(self,parent,*args)
        parent.geometry("300x500")
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        self.parent=parent
        self.ini_section = kwargs['ini_section']
        self.devicesTuple = tuple()
        getStaff = \
        """
        SELECT name
        FROM beta.staff
        WHERE active=TRUE;
        """
        stafflist = self.fetchall(getStaff)
        snames =[staff[0] for staff in stafflist]
        self.staffName = tk.StringVar(parent,value="staff:")
        self.staffDD = tk.OptionMenu(parent,self.staffName,"staff:",*snames)
        self.hdpidL = tk.Label(parent,text='Hard Drive PID:')
        self.hdpid = tk.Entry(parent,fg='black',bg='white',width=25)
        self.hdLabel = tk.Label(parent,text="Hard Drive Serial:")
        self.hd = tk.Entry(parent,fg='black',bg='white',width=25)
        self.wiperProduct = tk.StringVar(parent,value="Wiped?")
        self.wiperProductMenu = tk.OptionMenu(parent,self.wiperProduct,
                                            "Wiped.","Destroyed.")
        self.finishHDButton = tk.Button(parent,
            text='submit',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.finishHDButton.bind('<Button-1>',self.finishHD)
        self.qcbutton = tk.Button(parent,
            text='Quality Check',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.genReport = tk.Button(parent,
            text='Get Reports',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.qcbutton.bind('<Button-1>',self.manualQC)
        self.genReport.bind('<Button-1>',self.getReport)
        self.err = tk.StringVar()
        self.errorFlag = tk.Label(parent,textvariable=self.err)
        self.staffDD.pack()
        self.hdpidL.pack()
        self.hdpid.pack()
        self.hdLabel.pack()
        self.hd.pack()
        self.wiperProductMenu.pack()
        self.errorFlag.pack()
        self.finishHDButton.pack()
        self.qcbutton.pack()
        self.genReport.pack()
        self.hdpidVal = tk.StringVar(parent)
        self.hdVal = tk.StringVar(parent)
        self.hdpidLog=tk.StringVar(parent)
        self.hdLog = tk.StringVar(parent)
        self.updatehdsnbutton = tk.Button(parent,
            text='Update HD SN',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.updatehdsnbutton.bind('<Button-1>',self.updatehdsn)
        self.getHdsnInfobutton = tk.Button(parent,
            text='Get HD Facts',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.getHdsnInfobutton.bind('<Button-1>',self.getHdsnInfo)
        self.getHdsnInfobutton.pack()
        tk.Label(parent,textvariable=self.hdpidLog).pack()
        tk.Label(parent,textvariable=self.hdLog).pack()
        # the following is dangerous. Its probably fine... but manually
        # logging into database and doing the update would be better.
        # self.updatehdsnbutton.pack()
    def getHdsnInfo(self,event):
        pop_up = tk.Toplevel(self.parent)
        kwargs = dict()
        kwargs['ini_section']=self.ini_section
        if self.hdpid.index('end') != 0:
            kwargs['hdpid']=self.hdpid.get()
        else:
            kwargs['hdsn']=self.hd.get()
        HdFacts(pop_up,**kwargs)

    def updatehdsn(self,event):
        updatehdSQL = \
        """
        UPDATE beta.harddrives
            set hdsn = %s
            WHERE {}
            RETURNING device_id;
        """
        if self.hdpid.index("end") != 0:
            rowIdentifier = 'hdpid = %s' % (self.hdpid.get(),)
        elif len(self.hdpidVal.get()) !=0:
            rowIdentifier = 'hdpid = %s' % (self.hdpidVal.get(),)
        else:
            self.err.set('include a Hard Drive PID in order to update SN.')
            return self
        updatehdSQL.format(rowIdentifier)
        self.fetchone(updatehdSQL,self.hd.get())
        self.hd.delete(0,'end')
        self.hdpid.delete(0,'end')
        return self
    def finishHD(self,event):
        name = self.staffName.get()
        if name == "staff:":
            self.err.set('select a staff from the drop down.')
            return self
        hdStatusUpdate = \
        """
        with logHdStatus as(
        UPDATE beta.harddrives
        set {},
            wipeDate = %s,
            staff_id = (Select staff_id from beta.staff s where s.name = %s)
        WHERE {}
        RETURNING hd_id,hdsn,hdpid
        )
        UPDATE beta.donations
        SET numwiped = (CASE WHEN numwiped is not null THEN (numwiped + 1) ELSE 0 END)
        WHERE donation_id = (
                            SELECT donation_id
                            FROM beta.donatedgoods
                            WHERE hd_id = (SELECT hd_id FROM logHdStatus)
                            )
        RETURNING numwiped,(select hdsn from logHdStatus),(select hd_id from logHdStatus),donation_id,(select hdpid from logHdStatus);
        """
        wiped = self.wiperProduct.get()
        if wiped == "Wiped.":
            wipedOrDestroyed="sanitized = TRUE, destroyed = FALSE"
        elif wiped == "Destroyed.":
            wipedOrDestroyed="sanitized = FALSE, destroyed = TRUE"
        if self.hdpid.index("end") != 0:
            hardDriveIdentifier = "hdpid = LOWER('%s')" % (self.hdpid.get(),)
            usedpid = True
        else:
            hardDriveIdentifier = "hdsn = LOWER('%s')" % (self.hd.get(),)
            usedpid = False
        hdStatusUpdate_FleshedOut = hdStatusUpdate.format(wipedOrDestroyed,hardDriveIdentifier)
        try:
            now = datetime.datetime.now()
            out = self.fetchone(hdStatusUpdate_FleshedOut,now,name)
            self.conn.commit()
            if out==None:
                self.err.set('Error! Error! provided '+ hardDriveIdentifier +' isn\'t in system!')
                pop_up = tk.Toplevel(self.parent)
                pop_up.title('Deeper Hard Drive Search')
                hdStatusUpdate_ForPassThru = hdStatusUpdate.format(wipedOrDestroyed,'{}')
                deeperHardDriveSearch(pop_up,ini_section=self.ini_section,
                                     hdserial=self.hd,name=name,wipedVar=wiped,
                                     sqlupdate=hdStatusUpdate_ForPassThru)
            else:
                if out[0] == 0:
                    self.err.set('First HD for Lot. Please do Quality Check.')
                    self.qualityCheck(name,wiped,hd_id=out[2],donation_id=out[3],hdpid=out[4])
                else:
                    self.err.set('success! Its been {} drives sence QC'.format(out[0]-1))
                self.hdpidVal = self.hdpid.get()
                self.hdVal=out[1]
                self.hdpidLog.set('HD PID: %s' % (self.hdpidVal,))
                self.hdLog.set('HD SN: %s' % (self.hdVal,))
                self.hd.delete(0,'end')
                self.hdpid.delete(0,'end')
        except (Exception, psycopg2.DatabaseError) as error:
            self.err.set(error)
        finally:
            return self
    def getReport(self,event):
        pop_up = tk.Toplevel(self.parent)
        pop_up.title('Generate CRM Report')
        Report(pop_up,ini_section=self.ini_section)
    def manualQC(self,event):
        if self.hdpid.index("end") != 0 and self.hd.index("end") != 0:
            self.qualityCheck(self.staffName.get(),self.wiperProduct.get(),
                hd=self.hd.get(),hdpid=self.hdpid.get())
        elif self.hdpid.index("end") != 0:
            self.qualityCheck(self.staffName.get(),self.wiperProduct.get(),
                hdpid=self.hdpid.get())
        elif self.hd.index("end") != 0:
            self.qualityCheck(self.staffName.get(),self.wiperProduct.get(),
                hd=self.hd.get())
        else:
            self.err.set('Please provide HD PID or SN.')
    def qualityCheck(self,name,status,**kwargs):
        pop_up = tk.Toplevel(self.parent)
        pop_up.title('Quality Check')
        qc(pop_up,name=name,status=status,ini_section=self.ini_section,**kwargs)
class deeperHardDriveSearch(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        self.parent=parent
        self.ini_section = kwargs['ini_section']
        DBI.__init__(self,ini_section = self.ini_section)
        self.sqlUpdateStatement=kwargs['sqlupdate']
        self.username = kwargs['name']
        self.hd=tk.StringVar(parent)
        self.parentHD = kwargs['hdserial']
        if self.parentHD.index("end") != 0:
            self.hd.set(self.parentHD.get())
            hds = self.fetchall(self.getQuery(self.hd.get()),self.hd.get())
            hds =[hd[0] for hd in hds]
        else:
            hds = list()
        self.stringEntry = tk.Entry(parent,width=20,textvariable=self.hd)
        self.hdvar = tk.StringVar(parent,value="select a hd:")
        self.hdDD = tk.OptionMenu(parent,self.hdvar,"select a hd:",*hds)
        self.searchButton = tk.Button(parent,
            text='Search',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.searchButton.bind('<Button-1>',self.search)
        self.stringEntry.pack()
        self.searchButton.pack()
        self.hdDD.pack()
        tk.Label(parent,text=kwargs['wipedVar']).pack()
        self.pbButton = tk.Button(parent,
            text='pass back selected HD SN',
            width = 25,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.pbButton.bind('<Button-1>',self.passBack)
        self.pbButton.pack()
        self.updateButton = tk.Button(parent,
            text='Update HD SN',
            width = 25,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.updateButton.bind('<Button-1>',self.updateSN)
        self.updateButton.pack()
        # consider adding a treeview:
        # this code specifically will not work, but is in the right direction
        # self.tv = tk.ttk.Treeview(self,columns=(1,),show='headings',height=8)
        # self.tv.heading(1,text='HDSN')
        # self.tv.pack()
        # sb = tk.Scrollbar(self, orient=tk.VERTICAL)
        # sb.pack(side=tk.RIGHT, fill=tk.Y)
        # self.tv.config(yscrollcommand=sb.set)
        # sb.config(command=self.tv.yview)
        # style = tk.ttk.Style()
        # style.theme_use("default")
        # style.map("Treeview")

    def getQuery(self,hd):
        if len(hd) < 6:
            return """
            with userinput as (SELECT LOWER(%s) as value)
            SELECT hdsn
            FROM beta.harddrives
            WHERE destroyed = FALSE
            AND sanitized = FALSE
            AND hdsn ~* (SELECT SUBSTRING(
                (SELECT value from userinput),2,
                LENGTH((SELECT value from userinput))-2
            ))
            LIMIT 10;
            """
        else:
            return """
            with userinput as (SELECT LOWER(%s) as value)
            SELECT hdsn
            FROM beta.harddrives
            WHERE destroyed = FALSE
            AND sanitized = FALSE
            AND hdsn ~* (SELECT SUBSTRING(
                (SELECT value from userinput),3,
                LENGTH((SELECT value from userinput))-3
            ))
            LIMIT 10;
            """
    def search(self,event):
        hds =self.fetchall(self.getQuery(self.hd.get()),self.hd.get())
        self.hdDD['menu'].delete(0,'end')
        filtered_hds = self.fetchall(self.getQuery(self.hd.get()),self.hd.get())
        for hd in filtered_hds:
            self.hdDD['menu'].add_command(label=hd[0],
                command=tk._setit(self.hdvar,hd[0]))
        return self
    def passBack(self,event):
        hd = self.hdvar.get()
        if hd == "select a hd:":
            self.err.set('please select a value from drop down.')
        else:
            self.parentHD.delete(0,'end')
            self.parentHD.insert(0,hd)
            self.parent.destroy()
    def updateSN(self,event):
        hdBanked = self.hdvar.get()
        if hdBanked == "select a hd:":
            self.err.set('please select a value from drop down.')
        else:
            pop_up = tk.TopLevel(self.parent)
            UpdateHD(pop_up,ini_section=self.ini_section,hdBanked=hdBanked)
class UpdateHD(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        self.parent=parent
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        self.hdBanked = kwargs['hdBanked']
        tk.Label(parent,text='Update HD SN: ' + self.hdBanked + ' \nwith:').pack()
        self.newHD = tk.Entry(parent,width=20)
        self.newHD.pack()
        self.err = tk.StringVar(parent)
        tk.Label(parent,textvariable=self.err).pack()
        updateButton = tk.Button(parent,
            text='Update HD SN',
            width = 25,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        updateButton.bind('<Button-1>',self.updateHD)
        updateButton.pack()

    def updateHD(self,event):
        try:
            updateSQL = \
            """
            UPDATE beta.harddrives
            SET hdsn = %s
            WHERE hdsn = %s;
            """
            out=self.insertToDB(updateSQL,self.newHD.get(),self.hdBanked)
            self.err.set(out)
        except (Exception, psycopg2.DatabaseError) as error:
            self.err.set(error)
        finally:
            return self
class qc(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        if "hd" in kwargs and "hdpid" in kwargs:
            self.hd = kwargs['hd']
            self.hdpid = kwargs['hdpid']
        elif "hdpid" in kwargs:
            self.hdpid = kwargs['hdpid']
            hdSQL = \
            """
            SELECT hdsn
            FROM beta.harddrives
            WHERE hdpid = LOWER(%s);
            """
            res = self.fetchone(hdSQL,self.hdpid)
            if res != None:
                self.hd = res[0]
            else:
                self.hd = None
        else:
            self.hd = kwargs['hd']
            hdpidSQL = \
            """
            SELECT hdpid
            FROM beta.harddrives
            WHERE hdsn = LOWER(%s);
            """
            res = self.fetchone(hdpidSQL,self.hd)
            if res != None:
                self.hdpid = res[0]
            else:
                self.hdpid = None
        self.hdstatus=kwargs['status']
        if 'donation_id' in kwargs:
            self.donation_id = kwargs['donation_id']
        else:
            donationIDFromHDinfo= \
            """
            SELECT donation_id
            FROM beta.donatedgoods
            INNER JOIN beta.harddrives hd USING (hd_id)
            WHERE {};
            """
            print(self.hdpid)
            print(type(self.hdpid))
            if self.hdpid is not None:
                donationIDFromHDPID = donationIDFromHDinfo.format("hd.hdpid = LOWER(%s)")
                print(donationIDFromHDPID)
                self.donation_id = self.fetchone(donationIDFromHDPID,self.hdpid)[0]
            else:
                donationIDFromHDSN = donationIDFromHDinfo.format("hd.hdsn = LOWER(%s)")
                self.donation_id = self.fetchone(donationIDFromHDSN,self.hd)[0]
        if 'hd_id' in kwargs:
            self.hd_id = kwargs['hd_id']
        else:
            get_hd_id = \
            """
            SELECT hd_id
            FROM beta.harddrives hd
            WHERE {};
            """
            if self.hdpid is not None:
                hd_id_fromHDPID = get_hd_id.format("hd.hdpid = LOWER(%s)")
                self.hd_id = self.fetchone(hd_id_fromHDPID,self.hdpid)[0]
            else:
                hd_id_fromHDSN = get_hd_id.format("hd.hdsn = LOWER(%s)")
                self.hd_id = self.fetchone(hd_id_fromHDSN,self.hd)[0]
        getStaffqc = \
        """
        SELECT name
        FROM beta.staff
        WHERE name != %s
        AND active=TRUE;
        """
        stafflist = self.fetchall(getStaffqc,kwargs['name'])
        snames =[staff[0] for staff in stafflist]
        self.staffName = tk.StringVar(parent,value="staff:")
        self.staffDD = tk.OptionMenu(parent,self.staffName,"staff:",*snames)
        instructions=tk.Label(parent,text='please get another staff member to perform quality check\nfor hard drive:').pack()
        hdidlabel = tk.Label(parent,text =self.hdpid).pack()
        hdlabel = tk.Label(parent,text =self.hd).pack()
        self.wiperProduct = tk.Label(parent,text="HD is " + kwargs['status']).pack()
        self.staffDD.pack()
        self.password=tk.Entry(parent)
        self.password.pack()
        logQC = tk.Button(parent,
            text='log QC',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        logQC.bind('<Button-1>',self.logQC)
        logQC.pack()
        self.err = tk.StringVar(parent)
        tk.Label(parent,textvariable=self.err).pack()
    def staff_password_check(self,name,pwd):
        pwdCheckSQL = \
        """
        WITH UI AS (
            SELECT
                %s as name,
                %s as pwd)
        SELECT (
            CASE
                WHEN s.name = (SELECT name FROM UI)
                    AND s.password = (SELECT pwd FROM UI)
                        THEN staff_id
                ELSE
                        NULL
                END
               )
            FROM beta.staff s
            WHERE s.name = (SELECT name from UI);
        """
        try:
            if self.fetchone(pwdCheckSQL,name,pwd) is None:
                raise AttributeError("Not connected to Database.")
            elif self.fetchone(pwdCheckSQL,name,pwd)[0] is None:
                print('password incorrect.')
                return False
            else:
                return True
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            self.err.set(error)


    def logQC(self,event):
        name = self.staffName.get()
        pwd=self.password.get()
        try:
            if self.staff_password_check(name,pwd) is not True:
                self.err.set(f'password incorrect for selected user: {name}')
                return self
        except AttributeError as err:
            self.err.set(err)
            return self
        if name == "staff:":
            self.err.set('select a staff from the drop down.')
            return self
        try:
            qualityControlLog = \
            """
            DROP TABLE IF EXISTS ui;
            CREATE TEMP TABLE ui(hd_id INTEGER,qc_time TIMESTAMP,donation_id INTEGER,staff_id INTEGER);
            select * from ui;
            INSERT INTO ui(hd_id,qc_time,staff_id)
            VALUES(
                %s,
                NOW(),
                (select staff_id from beta.staff where name = %s)
                );

            UPDATE ui
            SET donation_id = (
                SELECT g.donation_id
                FROM beta.donatedgoods g
                WHERE g.hd_id = (SELECT hd_id from ui)
                              );
            INSERT INTO beta.qualitycontrol(hd_id,qcDate,donation_id,staff_id)
            SELECT hd_id,qc_time, donation_id, staff_id
            FROM ui;
            Update beta.donations
            set numwiped = 1
            WHERE donation_id = (SELECT donation_id from ui);
            DROP TABLE ui;
            """
            out=self.insertToDB(qualityControlLog,self.hd_id,name)
            self.err.set(out)
        except (Exception, psycopg2.DatabaseError) as error:
            self.err.set(error)
        finally:
            return self

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Wiper Station")
    app = ProcessedHardDrives(root,ini_section='local_launcher')
    app.mainloop()
