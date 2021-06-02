import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import datetime
import re
from config import DBI

# improvements include:
# creating dropdowns of common issues.
# such as missing RAM.

class InsertLog(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        deviceQualities = self.fetchall("SELECT quality FROM beta.qualities;")
        qtypes =[quality[0] for quality in deviceQualities]
        self.qualityName = tk.StringVar(parent,value="quality:")
        self.qualityDD = tk.OptionMenu(parent,self.qualityName,"quality:",*qtypes)
        self.pid = tk.Entry(parent,width=25)
        self.log = tk.Entry(parent,width=50)
        self.notes = tk.Text(parent,height=4,width=25)
        self.pallet = tk.Entry(parent,width=25)
        self.passBackSelection = tk.Button(parent,
            text='Log',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.pidLabel = tk.Label(parent,text="pid:").grid(column=0,row=2)
        self.logLabel = tk.Label(parent,text="log:").grid(column=0,row=3)
        self.notesLabel = tk.Label(parent,text="notes:").grid(column=0,row=4)
        self.palletlabel = tk.Label(parent,text='location:').grid(column=0,row=0)
        self.qualityDD.grid(column=1,row=1)
        self.passBackSelection.bind('<Button-1>',self.logit)
        self.pid.grid(column=1,row=2)
        self.log.grid(column=1,row=3)
        self.notes.grid(column=1,row=4)
        self.pallet.grid(column=1,row=0)
        self.passBackSelection.grid(column=1,row=5)
        self.outVar = tk.StringVar()
        self.outVarLabel = tk.Label(parent,textvariable=self.outVar)
        self.outVarLabel.grid(column=0,row=5)
    def logit(self,event):
        pid_ = self.pid.get()
        pid = ''
        for item in pid_.split(' '):
            if len(item) > 0:
                pid+=item
        quality = self.qualityName.get()
        log = self.log.get()
        notes = self.notes.get('1.0',tk.END)
        pallet = self.pallet.get()
        insertLog = \
        """
        INSERT INTO beta.missingparts(quality,
            resolved,
            issue,
            notes,
            pc_id,
            pallet)
        VALUES((SELECT quality_id from beta.qualities where quality=%s),%s,%s,%s,(SELECT pc_id
                            FROM beta.computers
                            WHERE pid LIKE LOWER(%s)),%s)
        RETURNING mp_id,pc_id;
        """
        back = self.fetchone(insertLog,quality,False,
                            log,notes,pid,pallet)
        bool = True
        if back == None:
            bool = False
            err = 'log not inserted.'
        else:
            for id in back:
                if id == None:
                    bool = False
                    err = 'pid not registered.'
        if bool is True:
            self.conn.commit()
            self.pid.delete(0,'end')
            self.log.delete(0,'end')
            self.notes.delete('1.0',tk.END)
            err = 'success!'
        self.outVar.set(err)

class AssociatePidAndLicense(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent)
        DBI.__init__(self,ini_section=kwargs['ini_section'])
        getDeviceQualities = \
        """
        SELECT q.quality
        FROM beta.qualities q;
        """
        deviceQualities = self.fetchall(getDeviceQualities)
        qtypes =[quality[0] for quality in deviceQualities]
        self.qualityName = tk.StringVar(parent,value="quality:")
        self.qualityDD = tk.OptionMenu(parent,self.qualityName,"quality:",*qtypes)
        self.snLabel = tk.Label(parent,text="Microsoft Serial Number:")
        self.pidLabel = tk.Label(parent,text="device PID:")
        self.pid = tk.Entry(parent,fg='black',bg='white',width=15)
        self.sn = tk.Entry(parent,fg='black',bg='white',width=15)
        self.submitMatch = tk.Button(parent,
            text='submit',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.submitMatch.bind('<Button-1>',self.submit)
        self.pidLabel.grid(row=0,column=0)
        self.pid.grid(row=0,column=1)
        self.snLabel.grid(row=1,column=0)
        self.sn.grid(row=1,column=1)
        self.qualityDD.grid(row=2,column=1)
        self.submitMatch.grid(row=3,column=1)
        self.err = tk.StringVar()
        self.errorLabel = tk.Label(parent,textvariable=self.err)
        self.errorLabel.grid(row=3,column=0)
    def submit(self,event):
        quality = self.qualityName.get()
        sn = self.sn.get()
        pid = self.pid.get()
        back=None
        if quality != "quality:":
            licenseToPid_QualityIncluded = \
            """
            UPDATE beta.computers c
            SET license_id = (SELECT license_id
                                FROM beta.licenses
                                WHERE serialNumber=%s),
                quality_id = (SELECT quality_id
                                FROM beta.qualities q
                                WHERE q.quality = %s)
            WHERE c.pid = %s
            RETURNING pc_id,license_id;
            """
            back=self.fetchone(licenseToPid_QualityIncluded,sn,quality,pid)
        else:
            licenseToPid = \
            """
            UPDATE beta.computers c
            SET license_id = (SELECT license_id
                                FROM beta.licenses
                                WHERE serialNumber='we4rty')
            WHERE pid = 'md123-123'
            RETURNING pc_id,license_id;
            """
            back=self.fetchone(licenseToPid,sn,pid)
        bool = True
        if back == None:
            bool = False
            err = 'most likely error is that the pid is not registered'
        else:
            for id in back:
                if id == None:
                    bool = False
                    err = 'most likely error is license serial number not registered'
        if bool == True:
            # updates take no effect until we commit them here.
            # note that the DBI method insertToDB(sql,*args) has a commit in it
            self.conn.commit()
            self.err.set('success!')
            self.pid.delete(0,'end')
            self.sn.delete(0,'end')
        else:
            self.err.set(err)
class Banner(tk.Frame):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent)
        tk.Label(parent,text='Please attach licenses to devices.').pack()
class testGUI(ttk.Notebook):
    def __init__(self,parent,*args,**kwargs):
        self.donationIDVar = tk.StringVar()
        Banner(parent)
        ttk.Notebook.__init__(self,parent,*args)
        self.tab1 = ttk.Frame()
        self.tab2 = ttk.Frame()
        #self.tab3 = ttk.Frame()
        #SNPK(self.tab3,ini_section=kwargs['ini_section'])
        InsertLog(self.tab2,ini_section=kwargs['ini_section'])
        AssociatePidAndLicense(self.tab1,ini_section=kwargs['ini_section'])
        self.add(self.tab1,text="Attach Licenses to Devices")
        self.add(self.tab2,text="Log Issue")
        #self.add(self.tab3,text="Insert More Licenses")
        #self.add(self.banner)
        self.pack(expand=True,fill='both')
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Test Station")
    app = testGUI(root,ini_section='local_launcher')
    app.mainloop()
