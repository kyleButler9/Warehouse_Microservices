from config import DBI;
import tkinter as tk
from multiprocessing import Process
from pathlib import Path
import os
from os.path import join
from donationBanner import *
from Google_Sheets_Interface import *

class InvestigateLots(DonationBanner,DBI):
    def __init__(self,parent,*args,**kwargs):
        self.donationIDVar=kwargs['donationID']
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        self.getInfoButton = tk.Button(parent,
            text='Get Info',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.getInfoButton.bind('<Button-1>',self.getInfo)
        self.num_HDSN=tk.StringVar(parent,value="Hard Drive Count: ")
        self.num_SN=tk.StringVar(parent,value="Device Count: ")
        self.how_many_HDs_left=tk.StringVar(parent,value="Count Remaining: ")
        tk.Label(parent,textvariable=self.num_HDSN).pack()
        tk.Label(parent,textvariable=self.num_SN).pack()
        tk.Label(parent,textvariable=self.how_many_HDs_left).pack()
        self.err = tk.StringVar(parent)
        tk.Label(parent,textvariable=self.err).pack()
        self.getInfo(None)

    def getInfo(self,event):
        donationID=self.donationIDVar.get()
        if len(donationID) == 0:
            self.err.set('Please select a donation.')
            return self
        getInfo = \
        """
        SELECT count(DISTINCT hd_id),count(DISTINCT pc_id)
        FROM beta.donatedgoods
        WHERE donation_id = %s;
        """ #% (donationID,)
        res = self.fetchone(getInfo,donationID)
        msg=dict()
        self.num_HDSN.set("Hard Drive Count: " + str(res[0]))
        self.num_SN.set("Device Count: "+str(res[1]))
        queryPartiallyCompletedLot = \
        """
        SELECT count(g.hd_id) as howmanyleft
        from beta.donatedgoods g
        INNER JOIN beta.harddrives hd USING (hd_id)
        where hd.destroyed=FALSE and hd.sanitized=FALSE
        and hd.hdpid is not NULL
        and donation_id = %s
        group by donation_id;
        """# % (donationID,)
        hmlRes=self.fetchone(queryPartiallyCompletedLot,donationID)
        if hmlRes:
            self.how_many_HDs_left.set("Count Remaining: "+str(hmlRes[0]))
        else:
            self.how_many_HDs_left.set("Count Remaining: "+str(0))


class Report(DonationBanner,DBI):
    def __init__(self,parent,*args,**kwargs):
        # note that optimally, g.hd_id is not null should be the proper query
        # instead of hd.hdpid is not null as g.hd_id should be null if hd.hdpid is
        # but in the current factoring it isnt
        self.ini_section = kwargs['ini_section']
        self.parent=parent
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        queryCompletedLots = \
        """
        with completedlots as
        (select g.donation_id,
        bool_and(case when hd.destroyed = TRUE or hd.sanitized=TRUE THEN TRUE ELSE FALSE END)
        from beta.donatedgoods g
        INNER JOIN beta.harddrives hd USING (hd_id)
        INNER JOIN beta.donations d USING (donation_id)
        where hd.hdpid is not null and d.report=FALSE
        group by g.donation_id
        having bool_and(case when hd.destroyed = TRUE or hd.sanitized=TRUE THEN TRUE ELSE FALSE END) = TRUE)

        select donors.name, donations.lotnumber
        from completedlots
        INNER JOIN beta.donations on completedlots.donation_id=donations.donation_id
        INNER JOIN beta.donors USING(donor_id)
        order by lotnumber ASC;
        """
        tk.Label(parent,text='Completed Lots:').pack()
        completedLots = self.fetchall(queryCompletedLots)
        #completedLots_descriptors = [str(' | ').join(str(lot_info)) for lot_info in completedLots]
        completedLots_descriptors =list()
        for lot in completedLots:
            lotdesc = str()
            for lotDescriptor in lot:
                lotdesc+=str(lotDescriptor)
                if lotDescriptor !=lot[-1]:
                    lotdesc += ' | '
            completedLots_descriptors.append(lotdesc)
        self.lotvar = tk.StringVar(parent,value="donor name | lotnumber")
        self.clotsDD = tk.OptionMenu(parent,self.lotvar,"donor name | lotnumber",*completedLots_descriptors)
        self.clotsDD.pack()
        queryPartiallyCompletedLots = \
        """
        with PartiallyCompletedLots as (select donation_id, count(g.hd_id) as howmanyleft
        from beta.donatedgoods g
        inner join beta.donations d USING (donation_id)
        inner join beta.harddrives hd USING (hd_id)
        where hd.destroyed=FALSE and hd.sanitized=FALSE
        and hd.hdpid is not NULL and d.report=FALSE
        group by donation_id
        having count(hd_id) < %s
        and count(hd_id)>0)

        select donors.name,lotnumber, howmanyleft
        from PartiallyCompletedLots
        inner join beta.donations using (donation_id)
        inner join beta.donors using (donor_id)
        order by lotnumber;
        """
        tk.Label(parent,text='Partially Completed Lots with Maximum Number left: ').pack()
        self.maximum = tk.StringVar(parent,value='15')
        maxEntry=tk.Entry(parent,width=5,textvariable=self.maximum)
        maxEntry.pack()
        partialLots = self.fetchall(queryPartiallyCompletedLots % (self.maximum.get(),))
        #partialLots_descriptors = [str(' | ').join() for lot_info in partialLots]
        partialLots_descriptors =list()
        for lot in partialLots:
            lotdesc = str()
            for lotDescriptor in lot:
                lotdesc+=str(lotDescriptor)
                if lotDescriptor !=lot[-1]:
                    lotdesc += ' | '
            partialLots_descriptors.append(lotdesc)

        self.plotvar = tk.StringVar(parent,value="donor name | lotnumber | how many left")
        self.pclotsDD = tk.OptionMenu(parent,self.plotvar,"donor name | lotnumber | how many left",*partialLots_descriptors)
        self.pclotsDD.pack()

        DonationBanner.__init__(self,parent,ini_section=kwargs['ini_section'])
        self.google_sheets=UpdateSheets(self,
                            donation_id=self.donationIDVar.get(),
                            ini_section=self.ini_section)
        self.lookIntoLot = tk.Button(parent,
            text='Look into selected lot',
            width = 20,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.lookIntoLot.bind('<Button-1>',self.lookIntoLots)
        self.lookIntoLot.pack()
        self.genReport = tk.Button(parent,
            text='Get Receipts',
            width = 20,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.genReport.bind('<Button-1>',self.getTextFiles)
        self.genReport.pack()
        self.markReportedButton = tk.Button(parent,
            text='Remove from Dropdown',
            width = 20,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.markReportedButton.bind('<Button-1>',self.markReported)
        self.markReportedButton.pack()

        self.devicesTuple = tuple()
        self.err = tk.StringVar()
        tk.Label(parent,textvariable=self.err).pack()
    def markReported(self,event):
        self.donationID = self.donationIDVar.get()
        if len(self.donationID) == 0:
            self.err.set('Please select a donation.')
            return self
        markReportedSQL = \
        """
        WITH reportgen as (
        UPDATE beta.donations
        SET report = TRUE
        WHERE donation_id = %s
        RETURNING donation_id
        )
        SELECT donors.name, donations.lotnumber
        FROM beta.donors
        INNER JOIN beta.donations USING (donor_id)
        WHERE donation_id =
            (select donation_id from reportgen);
        """
        try:
            if self.conn is not None:
                donorName=self.fetchone(markReportedSQL, self.donationID)
                self.conn.commit()
                self.err.set(str(donorName[0]) + ' | '+str(donorName[1]) + ' removed from dropdown.')
            else:
                self.err.set("Database connection absent.")
        except:
            self.err.set('unable to mark provided lot reported.')
        finally:
            return self

    def getTextFiles(self,event):
        self.donationID=self.donationIDVar.get()
        if len(self.donationID) == 0:
            self.err.set('Please select a donation.')
            return self
        donationInfo = \
            """
            SELECT d.name, don.dateReceived, don.lotNumber
            FROM beta.donors d
            INNER JOIN beta.donations don USING (donor_id)
            WHERE donation_id = %s;
            """
        self.donationInfo=self.fetchone(donationInfo,self.donationID)
        devices = self.devicesToTuple()
        qcdevices=self.qcDevicesToTuple()
        devicesFilePath=self.TupleToTabDelimitedReport('',devices)
        qcFilePath=self.TupleToTabDelimitedReport('QC',qcdevices)
        report_csv=self.TupleToCommaDelimitedReport('',devices)
        report_qc_csv=self.TupleToCommaDelimitedReport('QC',qcdevices)
        # consider using something similar to the below to open the reports in seperate processes
        # this script specifically wont work but is very close..still buggy
        # procs = []
        # for outfile in [devicesFilePath,qcFilePath]:
        #     proc = Process(target=os.system,args=('notepad {}'.format(outfile),))
        #     procs.append(proc)
        #     proc.start()
        # for proc in procs:
        #     proc.join()
        self.err.set('Files successfully saved in your Downloads folder.')
        return self
    def devicesToTuple(self):
        self.google_sheets.donation_id=self.donationIDVar.get()
        self.google_sheets.overWrite_sanitization()
        deviceInfo = \
        """
        SELECT dt.deviceType, c.SN,
            CASE WHEN hd.hdsn is NULL and hd.hdpid is NULL THEN COALESCE(hd.hdsn,'')
                WHEN hd.hdsn is NULL THEN COALESCE(hd.hdsn,'N/A')
                ELSE hd.hdsn END,
            COALESCE(g.assetTag,'') as asset_tag, COALESCE(hd.destroyed,FALSE) as destroyed, COALESCE(hd.sanitized,FALSE) as sanitized,
            (select nameabbrev from beta.staff where staff_id=COALESCE(hd.staff_id,g.staff_id)),
            COALESCE(TO_CHAR(hd.wipeDate,'MM/DD/YYYY HH24:MI'),TO_CHAR(g.intakeDate,'MM/DD/YYYY HH24:MI')) as date
        FROM beta.donatedgoods g
        LEFT OUTER JOIN beta.computers c on g.pc_id = c.pc_id
        INNER JOIN beta.deviceTypes dt USING (type_id)
        LEFT OUTER JOIN beta.harddrives hd on g.hd_id = hd.hd_id
        WHERE g.donation_id = %s
        ORDER BY g.intakeDate;
        """
        devices = self.fetchall(deviceInfo,self.donationID)
        cols = 'Drive	Item Type	Item Serial	HD Serial Number	Asset Tag	Destroyed	Data Sanitized	Staff	Entry Date'
        devices.insert(0,tuple(cols.split('\t')))
        for driveNum in range(1,len(devices)):
            devices[driveNum] = (driveNum,) + devices[driveNum]
        return tuple(devices)
    def qcDevicesToTuple(self):
        self.google_sheets.donation_id=self.donationIDVar.get()
        print('did',self.google_sheets.donation_id)
        self.google_sheets.overWrite_qc()
        #note that this query avoids concern with the donations id column of the qc table
        qcInfo = \
        """
        SELECT hd.hdsn, TO_CHAR(qc.qcDate,'MM/DD/YYYY'),s.nameabbrev
        FROM beta.qualitycontrol qc
        INNER JOIN beta.staff s USING (staff_id)
        INNER JOIN beta.harddrives hd USING (hd_id)
        INNER JOIN beta.donatedgoods g USING (hd_id)
        WHERE g.donation_id = %s;
        """
        devices = self.fetchall(qcInfo,self.donationID)
        cols = 'Sample	HD Serial Number	Date Reviewed	Staff'
        devices.insert(0,tuple(cols.split('\t')))
        for driveNum in range(1,len(devices)):
            devices[driveNum] = (driveNum,) + devices[driveNum]
        return tuple(devices)
    def removeDuplicates(self):
        self.cur.execute(sql.tidyup.cutdown % (self.donationIDVar.get(),))
        self.conn.commit()
        return self
    def TupleToTabDelimitedReport(self,appendage,devicesTuple):
        downloadsFolder = join(Path.home(),'Downloads')
        fileName = '%s - %s - %s.txt' % (self.donationInfo[2],self.donationInfo[0],str(appendage))
        filepath = join(downloadsFolder,fileName)
        outfile = open(filepath,"w")
        for row in devicesTuple:
            for col in row:
                outfile.write(str(col) + '\t')
            outfile.write('\n')
        outfile.close()
        return filepath
    def TupleToCommaDelimitedReport(self,appendage,devicesTuple):
        downloadsFolder = join(Path.home(),'Downloads')
        fileName = '%s - %s - %s.csv' % (self.donationInfo[2],self.donationInfo[0],str(appendage))
        filepath = join(downloadsFolder,fileName)
        outfile = open(filepath,"w")
        for row in devicesTuple:
            for col in row:
                outfile.write(str(col) + ',')
            outfile.write('\n')
        outfile.close()
        return filepath
    def lookIntoLots(self,event):
        pop_up = tk.Toplevel(self.parent)
        pop_up.title('Lots info')
        InvestigateLots(pop_up,ini_section=self.ini_section,donationID=self.donationIDVar)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Report Generation Station")
    app = Report(root,ini_section='local_launcher')
    app.mainloop()
# getInfo = \
# """
# SELECT count(DISTINCT hd.hd_id),count(DISTINCT p.devicesn)
# FROM processing p INNER JOIN harddrives hd using (hd_id)
# WHERE p.donation_id = %s;
# """ % (donationID)
# queryPartiallyCompletedLot = \
# """
# SELECT count(hd_id) as howmanyleft
# from harddrives hd
# inner join processing USING (hd_id)
# inner join donations USING (donation_id)
# where hd.destroyed=FALSE and hd.sanitized=FALSE
# and donation_id = %s
# group by donation_id;
# """ % (donationID,)
# queryPartiallyCompletedLots = \
# """
# with PartiallyCompletedLots as (select donation_id, count(p.hd_id) as howmanyleft
# from processing p
# inner join donations USING (donation_id)
# inner join harddrives hd USING (hd_id)
# where hd.destroyed=FALSE and hd.sanitized=FALSE and reported=FALSE
# group by donation_id
# having count(p.hd_id) < %s
# and count(p.hd_id)>0)
#
# select donors.name,lotnumber, howmanyleft
# from PartiallyCompletedLots
# inner join donations using (donation_id)
# inner join donors using (donor_id)
# order by lotnumber;
# """
# deviceInfo = \
# """
# SELECT dt.deviceType, c.SN,
#     CASE WHEN hd.hdsn is NULL and hd.hdpid is NULL THEN COALESCE(hd.hdsn,'')
#         WHEN hd.hdsn is NULL THEN COALESCE(hd.hdsn,'N/A')
#         ELSE hd.hdsn END,
#     g.assetTag, hd.destroyed, hd.sanitized,COALESCE(s1.nameabbrev,s2.nameabbrev),
#     CASE WHEN (hd.sanitized=FALSE and hd.destroyed=FALSE) THEN TO_CHAR(g.intakeDate,'MM/DD/YYYY HH24:MI')
#     ELSE TO_CHAR(hd.wipeDate,'MM/DD/YYYY HH24:MI')
#     END AS date
# FROM donatedgoods g
# LEFT OUTER JOIN computers c on g.p_id = c.p_id
# LEFT OUTER JOIN harddrives hd on g.hd_id = hd.hd_id
# INNER JOIN deviceTypes dt USING (type_id)
# INNER JOIN staff s1 on hd.staff_id = s1.staff_id
# INNER JOIN staff s2 on g.staff_id=s2.staff_id
# WHERE g.donation_id = %s
# ORDER BY g.intakeDate;
# """
# deviceInfo = \
# """
# SELECT dts.deviceType, p.deviceSN,
#     CASE WHEN hd.hdsn is NULL and hd.hdpid is NULL THEN COALESCE(hd.hdsn,'')
#         WHEN hd.hdsn is NULL THEN COALESCE(hd.hdsn,'N/A')
#         ELSE hd.hdsn END,
#     p.assetTag, hd.destroyed, hd.sanitized, s.nameabbrev,
#     CASE WHEN hd.hdpid is NULL THEN TO_CHAR(p.entryDate,'MM/DD/YYYY HH24:MI')
#     ELSE TO_CHAR(hd.wipeDate,'MM/DD/YYYY HH24:MI')
#     END AS date
# FROM processing p
# INNER JOIN deviceTypes dts on dts.type_id = p.deviceType_id
# INNER JOIN staff s on s.staff_id = p.staff_id
# INNER JOIN harddrives hd USING (hd_id)
# WHERE p.donation_id = %s
# ORDER BY p.entryDate;
# """
# queryCompletedLots = \
# """
# with completedlots as
# (select avg(donors.donor_id) as donor_id, donation_id,
# bool_and(case when hd.destroyed = TRUE or hd.sanitized=TRUE THEN TRUE ELSE FALSE END)
# from processing
# inner join donations using (donation_id)
# inner join donors USING (donor_id)
# inner join harddrives hd USING (hd_id)
# where processing.hd_id is not null and reported=FALSE
# group by donation_id
# having bool_and(case when hd.destroyed = TRUE or hd.sanitized=TRUE THEN TRUE ELSE FALSE END) = TRUE)
#
# select donors.name, donations.lotnumber
# from completedlots
# inner join donors on completedlots.donor_id = donors.donor_id
# inner join donations on completedlots.donation_id=donations.donation_id
# order by lotnumber;
# """
