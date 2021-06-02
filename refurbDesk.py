import tkinter as tk
from tkinter import ttk
from config import *
from sql import *
class Banner(tk.Frame):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent)
        self.headermessage = tk.Entry(parent,text='Log new issue \n or retrieve a log')
class InsertLog(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        deviceQualities = self.fetchall(DeviceInfo.getDeviceQualities)
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
        back = self.fetchone(testStation.insertLog,quality,False,
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
class RetrieveLog(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        deviceQualities = self.fetchall(DeviceInfo.getDeviceQualities)
        qtypes =[quality[0] for quality in deviceQualities]
        self.qualityName = tk.StringVar(parent,value="quality:")
        self.qualityDD = tk.OptionMenu(parent,self.qualityName,"quality:",*qtypes)
        self.pid = tk.Entry(parent,width=25)
        self.logV = tk.StringVar(parent)
        self.log = tk.Entry(parent,width=50,textvariable=self.logV)
        self.notes = tk.Text(parent,height=4,width=25)
        self.palletV = tk.StringVar(parent)
        self.pallet = tk.Entry(parent,width=25,textvariable=self.palletV)
        self.retrieveLogs = tk.Button(parent,
            text='Get Log',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.pidLabel = tk.Label(parent,text="pid:").grid(column=0,row=0)
        self.logLabel = tk.Label(parent,text="log:").grid(column=0,row=3)
        self.notesLabel = tk.Label(parent,text="notes:").grid(column=0,row=4)
        self.palletlabel = tk.Label(parent,text='location:').grid(column=0,row=2)
        self.qualityDD.grid(column=1,row=1)
        self.retrieveLogs.bind('<Button-1>',self.getLog)
        self.pid.grid(column=1,row=0)
        self.log.grid(column=1,row=3)
        self.notes.grid(column=1,row=4)
        self.pallet.grid(column=1,row=2)
        self.retrieveLogs.grid(column=2,row=0)
        self.outVar = tk.StringVar()
        self.outVarLabel = tk.Label(parent,textvariable=self.outVar)
        self.outVarLabel.grid(column=0,row=5)
        self.updateLogs = tk.Button(parent,
            text='Update Log',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.updateLogs.bind('<Button-1>',self.updateLog)
        self.updateLogs.grid(column=1,row=5)
        self.isChecked = tk.BooleanVar()
        self.checkedBox = tk.Checkbutton(parent,text='Complete',
                                    variable=self.isChecked,
                                    height = 5,
                                    width=20)
        self.checkedBox.grid(column=2,row=5)
    def getLog(self,event):
        log = self.fetchone(testStation.getLog,self.pid.get())
        if log is not None:
            self.qualityName.set(log[0])
            self.isChecked.set(log[1])
            self.logV.set(log[2])
            self.notes.insert('1.0',log[3])
            self.palletV.set(log[4])
            self.outVar.set('success!')
        else:
            self.outVar.set('pid not in logs')
    def updateLog(self,event):
        pid_ = self.pid.get()
        pid = ''
        for item in pid_.split(' '):
            if len(item) > 0:
                pid+=item
        quality = self.qualityName.get()
        log = self.logV.get()
        done = bool(self.isChecked.get())
        notes = self.notes.get('1.0',tk.END)
        pallet = self.palletV.get()
        back = self.fetchone(testStation.updateLog,quality,done,log,notes,pallet)
        bool_ = True
        if back == None:
            bool_ = False
            err = 'log not inserted.'
        else:
            for id in back:
                if id == None:
                    bool_ = False
                    err = 'pid not registered.'
        if bool_ is True:
            self.conn.commit()
            self.pid.delete(0,'end')
            self.log.delete(0,'end')
            self.notes.delete('1.0',tk.END)
            self.isChecked.set(False)
            err = 'success!'
        self.outVar.set(err)
class refurbDeskGUI(ttk.Notebook):
    def __init__(self,parent,*args,**kwargs):
        self.donationIDVar = tk.StringVar()
        self.donorIdentifier = Banner(parent)
        ttk.Notebook.__init__(self,parent,*args)
        self.tab1 = ttk.Frame()
        self.tab2 = ttk.Frame()
        RetrieveLog(self.tab1,ini_section=kwargs['ini_section'])
        InsertLog(self.tab2,ini_section=kwargs['ini_section'])
        self.add(self.tab1,text="Retrieve Log")
        self.add(self.tab2,text="Update Logs")
        self.pack(expand=True,fill='both')
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Tech Station")
    app = refurbDeskGUI(root,ini_section='local_appendage')
    app.mainloop()
