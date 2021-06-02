import tkinter as tk
from config import DBI
import psycopg2
class ComputerFacts(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        self.parent=parent
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        hdpidL=tk.Label(parent,text='HD PID:')
        self.hdpid=tk.Entry(parent,width=25)
        devicehdsnL=tk.Label(parent,text='HD SN:')
        self.devicehdsn=tk.Entry(parent,width=25)
        self.lotNumber=tk.StringVar(parent)
        self.donorName=tk.StringVar(parent)
        self.name=tk.StringVar(parent)
        self.entryDate=tk.StringVar(parent)
        self.wipeDate=tk.StringVar(parent)
        self.devicesn=tk.StringVar(parent)
        self.devicePid=tk.StringVar(parent)
        lotNumberL=tk.Label(parent,textvariable=self.lotNumber)
        donorNameL=tk.Label(parent,textvariable=self.donorName)
        nameL=tk.Label(parent,textvariable=self.name)
        entryDateL=tk.Label(parent,textvariable=self.entryDate)
        wipedateL=tk.Label(parent,textvariable=self.wipeDate)
        devicePidL=tk.Label(parent,textvariable=self.devicePid)
        devicesnL=tk.Label(parent,textvariable=self.devicesn)
        self.SqlGetHdInfo = \
        """
        SELECT d.lotnumber,donor.name,s.name,
                g.intakedate,hd.wipedate,hd.hdsn,c.sn,c.pid,
                hd.sanitized,hd.destroyed,hd.hdpid
        FROM beta.donatedgoods g
        INNER JOIN beta.harddrives hd USING (hd_id)
        LEFT OUTER JOIN beta.computers c USING (pc_id)
        INNER JOIN beta.donations d USING (donation_id)
        INNER JOIN beta.donors donor USING (donor_id)
        INNER JOIN beta.staff s ON s.staff_id=hd.staff_id
        WHERE hd.{};
        """
        if 'pid' in kwargs:
            rowIdentifier="hdpid = LOWER('%s')" % (kwargs['pid'],)
            self.hdpid.insert(0,kwargs['pid'])
            self.hdpidLog = kwargs['pid']
            self.hdsnLog = None
        else:
            rowIdentifier="sn = LOWER('%s')" % (kwargs['sn'],)
            self.devicehdsn.insert(0,kwargs['sn'])
            self.hdpidLog = None
        hdInfo=self.fetchone(self.SqlGetHdInfo.format(rowIdentifier))
        if hdInfo:
            self.updateFrame(hdInfo,True)
        else:
            self.updateFrame(hdInfo,False)
        hdpidL.pack()
        self.hdpid.pack()
        devicehdsnL.pack()
        self.devicehdsn.pack()
        lotNumberL.pack()
        donorNameL.pack()
        nameL.pack()
        entryDateL.pack()
        wipedateL.pack()
        wipedBool.pack()
        destroyedBool.pack()
        devicePidL.pack()
        devicesnL.pack()
        getInfoB = tk.Button(parent,
            text='Get Info',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        getInfoB.bind('<Button-1>',self.getNewInfo)
        getInfoB.pack()
        self.err=tk.StringVar(parent)
        tk.Label(parent,textvariable=self.err).pack()
    def getNewInfo(self,event):
        if self.hdpid.get() != self.hdpidLog:
            rowIdentifier='hdpid = LOWER(%s)' % (self.hdpid.get(),)
        elif self.devicehdsn.get() != self.hdsnLog:
            rowIdentifier='hdsn = LOWER(%s)' % (self.devicehdsn.get(),)
        else:
            self.err.set('please enter a new PID or SN.')
            return self
        try:
            hdInfo=self.fetchone(self.SqlGetHdInfo.format(rowIdentifier))
            if hdInfo:
                self.updateFrame(hdInfo,True)
            else:
                hdInfo=self.fetchone(self.SqlGetHdInfo.format(rowIdentifier))
                self.updateFrame(hdInfo,False)
        except (Exception, psycopg2.DatabaseError) as error:
            self.err.set(error)
        finally:
            return self
    def updateFrame(self,hdInfo):
        try:
            self.lotNumber.set('lotnumber: '+str(hdInfo[0]))
            self.donorName.set('donorName: '+str(hdInfo[1]))
            self.name.set('Wiper name: '+str(hdInfo[2]))
            self.entryDate.set('entryDate: '+str(hdInfo[3])[:20])
            self.wipeDate.set('wipedate: '+str(hdInfo[4])[:20])
            self.devicesn.set('computer SN: '+str(hdInfo[5]))
            self.devicePid.set('PC ID: ' + str(hdInfo[10]))
            self.devicehdsn.delete(0,'end')
            self.hdpid.delete(0,'end')
            self.devicehdsn.insert(0,str(hdInfo[6]))
            self.hdpid.insert(0,str(hdInfo[7]))
            self.hdsnLog = self.devicehdsn.get()
            self.hdpidLog=self.hdpid.get()
        except:
            self.err.set('incompatable values for updating pane.')
        finally:
            return self
class HdFacts(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        self.parent=parent
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        hdpidL=tk.Label(parent,text='HD PID:')
        self.hdpid=tk.Entry(parent,width=25)
        devicehdsnL=tk.Label(parent,text='HD SN:')
        self.devicehdsn=tk.Entry(parent,width=25)
        self.lotNumber=tk.StringVar(parent)
        self.donorName=tk.StringVar(parent)
        self.name=tk.StringVar(parent)
        self.entryDate=tk.StringVar(parent)
        self.wipeDate=tk.StringVar(parent)
        self.wipedBool=tk.StringVar(parent)
        self.destroyedBool=tk.StringVar(parent)
        self.devicesn=tk.StringVar(parent)
        self.devicePid=tk.StringVar(parent)
        lotNumberL=tk.Label(parent,textvariable=self.lotNumber)
        donorNameL=tk.Label(parent,textvariable=self.donorName)
        nameL=tk.Label(parent,textvariable=self.name)
        entryDateL=tk.Label(parent,textvariable=self.entryDate)
        wipedateL=tk.Label(parent,textvariable=self.wipeDate)
        wipedBool=tk.Label(parent,textvariable=self.wipedBool)
        destroyedBool=tk.Label(parent,textvariable=self.destroyedBool)
        devicePidL=tk.Label(parent,textvariable=self.devicePid)
        devicesnL=tk.Label(parent,textvariable=self.devicesn)
        self.SqlGetHdInfo = \
        """
        SELECT d.lotnumber,donor.name,s.name,
                g.intakedate,hd.wipedate,
                c.sn,hd.hdsn,hd.hdpid,
                hd.sanitized,hd.destroyed,c.pid
        FROM beta.donatedgoods g
        INNER JOIN beta.harddrives hd USING (hd_id)
        LEFT OUTER JOIN beta.computers c USING (pc_id)
        INNER JOIN beta.donations d USING (donation_id)
        INNER JOIN beta.donors donor USING (donor_id)
        INNER JOIN beta.staff s ON s.staff_id=hd.staff_id
        WHERE hd.{};
        """
        self.SqlGet_NonWiped_HdInfo = \
        """
        SELECT d.lotnumber,donor.name,s.name,
                g.intakedate,hd.wipedate,
                c.sn,hd.hdsn,hd.hdpid,
                hd.sanitized,hd.destroyed,c.pid
        FROM beta.donatedgoods g
        INNER JOIN beta.harddrives hd USING (hd_id)
        LEFT OUTER JOIN beta.computers c USING (pc_id)
        INNER JOIN beta.donations d USING (donation_id)
        INNER JOIN beta.donors donor USING (donor_id)
        INNER JOIN beta.staff s ON s.staff_id=g.staff_id
        WHERE hd.{};
        """
        if 'hdpid' in kwargs:
            rowIdentifier="hdpid = LOWER('%s')" % (kwargs['hdpid'],)
            self.hdpid.insert(0,kwargs['hdpid'])
            self.hdpidLog = kwargs['hdpid']
            self.hdsnLog = None
        elif 'hdsn' in kwargs:
            rowIdentifier="hdsn = LOWER('%s')" % (kwargs['hdsn'],)
            self.devicehdsn.insert(0,kwargs['hdsn'])
            self.hdsnLog = kwargs['hdsn']
            self.hdpidLog = None
        else:
            print('include hdpid or hdsn in object kwargs')
        hdInfo=self.fetchone(self.SqlGetHdInfo.format(rowIdentifier))
        if hdInfo:
            self.updateFrame(hdInfo,True)
        else:
            hdInfo=self.fetchone(self.SqlGet_NonWiped_HdInfo.format(rowIdentifier))
            self.updateFrame(hdInfo,False)
        hdpidL.pack()
        self.hdpid.pack()
        devicehdsnL.pack()
        self.devicehdsn.pack()
        lotNumberL.pack()
        donorNameL.pack()
        nameL.pack()
        entryDateL.pack()
        wipedateL.pack()
        wipedBool.pack()
        destroyedBool.pack()
        devicePidL.pack()
        devicesnL.pack()
        getInfoB = tk.Button(parent,
            text='Get Info',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        getInfoB.bind('<Button-1>',self.getNewInfo)
        getInfoB.pack()
        self.err=tk.StringVar(parent)
        tk.Label(parent,textvariable=self.err).pack()
    def getNewInfo(self,event):
        if self.hdpid.index('end') !=0 and self.hdpid.get() != self.hdpidLog:
            rowIdentifier='hdpid = LOWER(%s)' #% (self.hdpid.get(),)
        elif self.devicehdsn.index('end')!=0 and self.devicehdsn.get() != self.hdsnLog:
            rowIdentifier='hdsn = LOWER(%s)' #% (self.devicehdsn.get(),)
        else:
            self.err.set('please enter a new HD PID or HD SN.')
            return self
        try:
            hdInfo=self.fetchone(self.SqlGetHdInfo.format(rowIdentifier),self.hdpid.get())
            if hdInfo:
                self.updateFrame(hdInfo,True)
            else:
                hdInfo=self.fetchone(self.SqlGet_NonWiped_HdInfo.format(rowIdentifier),self.hdpid.get())
                self.updateFrame(hdInfo,False)
        except (Exception, psycopg2.DatabaseError) as error:
            self.err.set(error)
        finally:
            return self
    def updateFrame(self,hdInfo,wipedOrDestroyed):
        try:
            if wipedOrDestroyed:
                self.lotNumber.set('lotnumber: '+str(hdInfo[0]))
                self.donorName.set('donorName: '+str(hdInfo[1]))
                self.name.set('Wiper name: '+str(hdInfo[2]))
                self.entryDate.set('entryDate: '+str(hdInfo[3])[:20])
                self.wipeDate.set('wipedate: '+str(hdInfo[4])[:20])
                self.wipedBool.set('wiped?: ' + str(hdInfo[8]))
                self.destroyedBool.set('Destroyed?: ' + str(hdInfo[9]))
                self.devicesn.set('computer SN: '+str(hdInfo[5]))
                self.devicePid.set('PC ID: ' + str(hdInfo[10]))

                self.devicehdsn.delete(0,'end')
                self.hdpid.delete(0,'end')
                self.devicehdsn.insert(0,str(hdInfo[6]))
                self.hdpid.insert(0,str(hdInfo[7]))
                self.hdsnLog = self.devicehdsn.get()
                self.hdpidLog=self.hdpid.get()
            else:
                self.lotNumber.set('lotnumber: '+str(hdInfo[0]))
                self.donorName.set('donorName: '+str(hdInfo[1]))
                self.name.set('Extractor: '+str(hdInfo[2]))
                self.entryDate.set('entryDate: '+str(hdInfo[3])[:20])
                self.wipeDate.set('wipedate: '+str(hdInfo[4])[:20])
                self.wipedBool.set('wiped?: ' + str(hdInfo[8]))
                self.destroyedBool.set('Destroyed?: ' + str(hdInfo[9]))
                self.devicesn.set('computer SN: '+str(hdInfo[5]))
                self.devicePid.set('PC ID: ' + str(hdInfo[10]))

                self.devicehdsn.delete(0,'end')
                self.hdpid.delete(0,'end')
                self.devicehdsn.insert(0,str(hdInfo[6]))
                self.hdpid.insert(0,str(hdInfo[7]))
                self.hdsnLog = self.devicehdsn.get()
                self.hdpidLog=self.hdpid.get()
        except:
            self.err.set('incompatable values for updating pane.')
        finally:
            return self
# self.SqlGetHdInfo = \
# """
# SELECT don.lotnumber,d.name,s.name,
#         p.entrydate,hd.wipedate,
#         p.devicesn,hd.hdsn,hd.hdpid
# FROM processing p
# INNER JOIN harddrives hd USING (hd_id)
# INNER JOIN donations don USING (donation_id)
# INNER JOIN donors d USING (donor_id)
# INNER JOIN staff s ON s.staff_id=hd.staff_id
# WHERE hd.{};
# """
# self.SqlGetHdInfo = \
# """
# SELECT don.lotnumber,d.name,s.name,
#         p.entrydate,hd.wipedate,
#         p.devicesn,hd.hdsn,hd.hdpid
# FROM processing p
# INNER JOIN harddrives hd USING (hd_id)
# INNER JOIN donations don USING (donation_id)
# INNER JOIN donors d USING (donor_id)
# INNER JOIN staff s ON s.staff_id=hd.staff_id
# WHERE hd.{};
# """
