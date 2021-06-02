from config import DBI
import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import datetime
from google_sheets import *

#from demoWriteSheet import *

class DonationBanner(tk.Frame):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        # the next section harvests meaningful kwargs and updates these
        # variables accordingly.
        self.companyNameVar = tk.StringVar(parent)
        # I forget why this doesn't have the input "parent".
        self.lotNumberVar = tk.StringVar()
        self.dateReceivedVar = tk.StringVar(parent)

        if 'donationIDVar' in kwargs:
            self.donationIDVar = kwargs['donationIDVar']
        else:
            self.donationIDVar = tk.StringVar(parent)
        if 'sheet_id_var' in kwargs:
            self.sheet_id = kwargs['sheet_id_var']
        else:
            self.sheet_id = tk.StringVar(parent)
        if 'ini_section' in kwargs:
            self.ini_section=kwargs['ini_section']
        else:
            print('no ini section provided. defaulting to default local...')
            self.ini_section = 'local_launcher'
        if 'companyName' in kwargs:
            self.companyNameVar.set("Donor Name: " + kwargs['companyName'])
        else:
            self.companyNameVar.set("Donor Name: "+'NO COMPANY NAME PROVIDED')
        if 'dateReceived' in kwargs:
            self.dateReceivedVar.set("Date Media Received: " +kwargs['dateReceived'])
        else:
            self.dateReceivedVar.set("Date Media Received: "+"None")
        if 'lotNumber' in kwargs:
            self.lotNumberVar.set("Lot Number: " +kwargs['lotNumber'])
        else:
            self.lotNumberVar.set("Lot Number: "+"None")
        # here we display the variables contents:
        self.companyName = tk.Label(parent,textvariable=self.companyNameVar)
        self.dateReceived = tk.Label(parent,textvariable=self.dateReceivedVar)
        self.lotNumber = tk.Label(parent,textvariable=self.lotNumberVar)
        #self.sheetIDVar_ = tk.StringVar()
        #self.sheetID = tk.Label(parent,textvariable=self.sheetIDVar_)
        self.selDonationButton = tk.Button(parent,
            text='Select Donation',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.selDonationButton.bind('<Button-1>',self.chooseDonation)
        self.companyName.pack(padx=10,pady=10)
        self.dateReceived.pack(padx=10,pady=10)
        self.lotNumber.pack(padx=10,pady=10)
        self.selDonationButton.pack(padx=10,pady=10)

    def chooseDonation(self,event):
        pop_up = tk.Toplevel(self.parent)
        SelectDonation(pop_up,
            ini_section=self.ini_section,
            companyNameVar=self.companyNameVar,
            dateReceivedVar=self.dateReceivedVar,
            lotNumberVar=self.lotNumberVar,
            donationID=self.donationIDVar,
            sheet_id_var = self.sheet_id)
            #bannerSheetIDVar = self.sheetIDVar_)
class SelectDonation(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        self.parent = parent
        self.companyNameVar = kwargs['companyNameVar']
        self.dateReceivedVar = kwargs['dateReceivedVar']
        self.lotNumberVar = kwargs['lotNumberVar']
        self.donationIDVar = kwargs['donationID']
        self.ini_section = kwargs['ini_section']
        self.sheet_id = kwargs['sheet_id_var']
        #self.sheetIDVar_ = kwargs['bannerSheetIDVar']
        DBI.__init__(self)
        self.donorInfoVar = tk.StringVar(parent,value="select donation:")
        getDonationHeader = \
        """
        SELECT d.name,i.dateReceived,i.lotNumber
        FROM beta.donors d
            INNER JOIN beta.donations i
            ON i.donor_id = d.donor_id
        WHERE d.name ~* %s
        ORDER BY dateReceived DESC;
        """
        donationInfo = self.fetchall(getDonationHeader,'')
        donationInfo =[str(dInfo[0]) + ', '+dInfo[1].strftime('%m/%d/%y')+', '+str(dInfo[2])
            for dInfo in donationInfo]
        if len(donationInfo) == 0:
            self.NewDonationPopUp(None)
        self.donationInfoDD = tk.OptionMenu(parent,self.donorInfoVar,*donationInfo)
        self.donationFilter = tk.Entry(parent,fg='black',bg='white',width=10)
        donationFilterLabel = tk.Label(parent,text='filter donation names via:')
        self.initGoogleSheetB = tk.Button(parent,
            text='New Google Sheet',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.initGoogleSheetB.bind('<Button-1>',self.newGS)
        self.passBackSelection = tk.Button(parent,
            text='Pass Back Selection',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.passBackSelection.bind('<Button-1>',self.updateBanner)
        self.updateDDButton = tk.Button(parent,
            text='Update Dropdown',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.updateDDButton.bind('<Button-1>',self.refreshOptionMenu)
        self.insertDonationButton = tk.Button(parent,
            text='Insert New Donoation',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.insertDonationButton.bind('<Button-1>',self.NewDonationPopUp)
        self.insertDonationButton.grid(row=2,column=2)
        self.updateDDButton.grid(row=0,column=2)
        donationFilterLabel.grid(column=0,row=0)
        self.donationFilter.grid(column=1,row=0)
        self.donationInfoDD.grid(row=1,column=1)
        self.passBackSelection.grid(row=2,column=1)
        self.initGoogleSheetB.grid(row=2,column=0)
    def NewDonationPopUp(self,event):
        popUp = tk.Toplevel(self.parent)
        NewDonation(popUp,
            ini_section=self.ini_section,
            sheet_id_var=self.sheet_id,
            donationID=self.donationIDVar)
    def refreshOptionMenu(self,event):
        self.donationInfoDD['menu'].delete(0,'end')
        getDonationHeader = \
        """
        SELECT d.name,i.dateReceived,i.lotNumber
        FROM beta.donors d
            INNER JOIN beta.donations i
            ON i.donor_id = d.donor_id
        WHERE d.name ~* %s
        ORDER BY dateReceived DESC;
        """
        filtered_donorInfo = self.fetchall(getDonationHeader,self.donationFilter.get())
        for dInfo in filtered_donorInfo:
            dinfoStr = str(dInfo[0]) + ', '+dInfo[1].strftime('%m/%d/%y')+', '+str(dInfo[2])
            self.donationInfoDD['menu'].add_command(label=dinfoStr,
                command=tk._setit(self.donorInfoVar,dinfoStr))
    def newGS(self,event):
        var = self.donorInfoVar.get().split(',')
        get_lot_info = \
        """
        SELECT d.name,l.lotnumber
        FROM beta.donors d
        INNER JOIN beta.donations l USING (donor_id)
        WHERE donation_id = %s;
        """
        lot_info = self.fetchone(get_lot_info,self.donationIDVar.get())
        self.sheet_id.set(create_Sanitization_Sheet(str(lot_info[1]) + ' - '+str(lot_info[0])+' - Data Sanitization & QC Log'))
        self.updateSheetID()
        self.google_sheets=UpdateSheets(self,
                            donation_id=self.donationIDVar.get(),
                            ini_section=self.ini_section)
        self.google_sheets.donation_id=self.donationIDVar.get()
        self.google_sheets.overWrite_sanitization(sheet_id=self.sheet_id.get())
        print(f'Active Sheet: \n\n\t\t https://docs.google.com/spreadsheets/d/{self.sheet_id.get()}')
    def updateBanner(self,event):
        var = self.donorInfoVar.get().split(',')
        self.companyNameVar.set("Donor Name: "+var[0])
        self.dateReceivedVar.set("Date Media Received: "+var[1])
        self.lotNumberVar.set("Lot Number: "+var[2])
        getDonationID = \
        """
        SELECT i.donation_id,i.sheetID
        FROM beta.donors d
        INNER JOIN beta.donations i
        ON i.donor_id = d.donor_id
        WHERE d.name = %s
        AND i.dateReceived = %s
        AND i.lotNumber = %s;
        """
        ids = self.fetchone(getDonationID,*var)
        self.donationIDVar.set(ids[0])
        sheet_id = ids[1]
        if sheet_id:
            self.sheet_id.set(sheet_id)
        else:
            get_lot_info = \
            """
            SELECT d.name,l.lotnumber
            FROM beta.donors d
            INNER JOIN beta.donations l USING (donor_id)
            WHERE donation_id = %s;
            """
            lot_info = self.fetchone(get_lot_info,self.donationIDVar.get())
            self.sheet_id.set(create_Sanitization_Sheet(str(lot_info[1]) + ' - '+str(lot_info[0])+' - Data Sanitization & QC Log'))
            self.updateSheetID()
        print(f'Active Sheet: \n\n\t\t https://docs.google.com/spreadsheets/d/{self.sheet_id.get()}')
        self.parent.destroy()
    def updateSheetID(self):
        # include checks that sheet_id.get() and donationIDVar.get()
        # are returning reasonable values, and take different action if not
        # such as self.err.set('no donation selected.')
        # alternatively, trigger a pop up if sheet_id.get() is blank
        # with an entry for someone to put in a http address to a sheet,
        # or just the spreadsheet id, and have it update
        update_db_with_sheetid = \
        """
        UPDATE beta.donations
        SET sheetid = %s
        WHERE donation_id = %s;
        """
        self.insertToDB(update_db_with_sheetid,
                self.sheet_id.get(),self.donationIDVar.get())
        return self
class NewDonor(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        if 'ini_section' in kwargs:
            self.ini_section = kwargs['ini_section']
        DBI.__init__(self)
        self.donorName = tk.Entry(parent,fg='black',bg='white',width=35)
        self.dnLabel = tk.Label(parent,text="Donor Name:")
        self.donorAddress = tk.Entry(parent,fg='black',bg='white',width=50)
        self.daLabel = tk.Label(parent,text="Donor Address:")
        self.status = tk.StringVar(parent)
        self.statusNote = tk.Label(parent,textvariable=self.status)
        self.insertDonorButton = tk.Button(parent,
            text='Insert New Donor',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.insertDonorButton.bind('<Button-1>',self.insertDonor)
        self.dnLabel.grid(row=0,column=0)
        self.donorName.grid(row=0,column=1)
        self.daLabel.grid(row=1,column=0)
        self.donorAddress.grid(row=1,column=1)
        self.statusNote.grid(row=2,column=0)
        self.insertDonorButton.grid(row=2,column=1)
    def insertDonor(self,event):
        donorName = str(self.donorName.get())
        donorAddress = str(self.donorAddress.get())
        insertNewDonor = \
        """
        INSERT INTO beta.donors(name,address)
        VALUES(%s,%s);
        """
        back = self.insertToDB(insertNewDonor,donorName,donorAddress)
        self.status.set(back)
        if back == "success!":
            self.donorName.delete(0,'end')
            self.donorAddress.delete(0,'end')

class NewDonation(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        self.parent=parent
        self.ini_section=kwargs['ini_section']
        self.donationID=kwargs['donationID']
        if 'sheet_id_var' in kwargs:
            self.sheet_id=kwargs['sheet_id_var']
        else:
            self.sheet_id=tk.StringVar(parent)
        DBI.__init__(self)
        getDonors = \
        """
        SELECT name from beta.donors
        WHERE name ~* %s;
        """
        donors = self.fetchall(getDonors,'')
        donors =[donor[0] for donor in donors]
        self.donorName = tk.StringVar(parent,value="select a donor:")
        self.donorsDD = tk.OptionMenu(parent,self.donorName,*donors)
        self.insertDonoationButton = tk.Button(parent,
            text='Insert New Donation',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        now = datetime.datetime.now()
        self.cal = Calendar(parent, font="Arial 14", selectmode='day',
                   cursor="hand1", year=now.year, month=now.month, day=now.day)
        self.calLabel = tk.Label(parent,text='Date Received')
        self.donorFilter = tk.Entry(parent,fg='black',bg='white',width=10)
        self.lotNumber = tk.Entry(parent,fg='black',bg='white',width=10)
        self.lotNumberLabel = tk.Label(parent,text="Lot Number: ")
        self.donorFilterLabel = tk.Label(parent,text="Filter Donors By:")
        self.donorFilterLaunch = tk.Button(parent,
            text='Update Dropdown',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.newDonorLaunch = tk.Button(parent,
            text='Insert New Donor',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.calLabel.grid(row=2,column=1)
        self.cal.grid(row=3,column=1)
        self.donorFilterLaunch.bind('<Button-1>',self.refreshOptionMenu)
        self.insertDonoationButton.bind('<Button-1>',self.insertDonation)
        self.newDonorLaunch.bind('<Button-1>',self.NewDonorPopUp)
        self.donorsDD.grid(row=1,column=1)
        self.donorFilterLabel.grid(row=0,column=0)
        self.donorFilter.grid(row=0,column=1)
        self.donorFilterLaunch.grid(row=0,column=2)
        self.lotNumberLabel.grid(row=4,column=0)
        self.lotNumber.grid(row=4,column=1)
        self.newDonorLaunch.grid(row=5,column=0)
        self.insertDonoationButton.grid(row=5,column=2)
        self.status = tk.StringVar(parent)
        self.statusBar = tk.Label(parent,textvariable=self.status)
        self.statusBar.grid(row=5,column=1)
    def NewDonorPopUp(self,event):
        popUp = tk.Toplevel(self.parent)
        NewDonor(popUp,ini_section=self.ini_section)
    def refreshOptionMenu(self,event):
        self.donorsDD['menu'].delete(0,'end')
        getDonors = \
        """
        SELECT name from beta.donors
        WHERE name ~* %s;
        """
        filtered_donors = self.fetchall(getDonors,self.donorFilter.get())
        for donor in filtered_donors:
            self.donorsDD['menu'].add_command(label=donor[0],
                command=tk._setit(self.donorName,donor[0]))
    def insertDonation(self,event):
        donorName = self.donorName.get()
        donationDate = self.cal.selection_get()
        lotNumber = self.lotNumber.get()
        sheetID = create_Sanitization_Sheet(lotNumber + ' - '+donorName+' - Data Sanitization & QC Log')
        if lotNumber == '':
            lotNumber = 0
            statusAppendage = 'with lot number = 0'
        else:
            statusAppendage = ''
            insertNewDonation = \
            """
            INSERT INTO beta.donations(lotNumber,dateReceived,sheetid,donor_id)
            VALUES(%s,%s,%s,(
                SELECT donor_id
                FROM beta.donors
                WHERE name = %s
            ));
            """
        out = self.insertToDB(insertNewDonation,
            lotNumber,
            donationDate,
            sheetID,
            donorName)
        report = [
            ['Company Name: {}'.format(donorName)],
            ['Date Received: {} '.format(donationDate.strftime('%m/%d/%Y'))],
            ['Lot Number: {}'.format(lotNumber)],
            ['']
        ]
        cols = 'Drive	Item Type	Item Serial	HD Serial Number	Asset Tag	Destroyed	Data Sanitized	Staff	Entry Date'
        report.append(cols.split('	'))
        write_to_sheet(sheetID,report)
        self.sheet_id.set(sheetID)
        self.status.set(out+statusAppendage)
#from demoWriteSheet import *
# class GenerateReport(tk.Frame,DBI):
#     def __init__(self,parent,*args,**kwargs):
#         tk.Frame.__init__(self,parent,*args)
#         DBI.__init__(self,ini_section = kwargs['ini_section'])
#         self.donationID = kwargs['donationID']
#         # if 'sheetID' not in kwargs:
#         #     self.sheetIDLabel = tk.Label(parent,text='Google Sheet ID:').grid(column=0,row=0)
#         #     self.sheetID = tk.Entry(parent,fg='black',bg='white',width=40)
#         #     self.sheetID.grid(column=1,row=0)
#         self.getReportButton = tk.Button(parent,
#             text='Generate New Report',
#             width = 15,
#             height = 2,
#             bg = "blue",
#             fg = "yellow",
#         )
#         self.getReportButton.bind('<Button-1>',self.writeSheet)
#         self.getReportButton.grid(column=1,row=2)
#         self.err=tk.StringVar(parent)
#         tk.Label(parent,textvariable=self.err).grid(column=1,row=3)
#     def writeSheet(self,event):
#         self.err.set('google functionality restricted because compiled into .exe')
        # donationID = self.donationID.get()
        # donationInfo=self.fetchone(Report.donationInfo,donationID)
        # report = [
        #     ['Company Name: {}'.format(donationInfo[0])],
        #     ['Date Received: {} '.format(donationInfo[1].strftime('%m/%d/%Y'))],
        #     ['Lot Number: {}'.format(donationInfo[2])],
        #     ['']
        # ]
        # cols = 'Drive	Item Type	Item Serial	HD Serial Number	Asset Tag	Destroyed	Data Sanitized	Staff	Entry Date'
        # report.append(cols.split('	'))
        # devices = self.fetchall(Report.deviceInfo,donationID)
        # drive = [1]
        # for device in devices:
        #     dlist = list(device)
        #     try:
        #         dlist[-1] = dlist[-1].strftime("%m/%d/%Y %H:%M")
        #     except:
        #         pass
        #     finally:
        #         report.append(drive + dlist)
        #         drive[0]+=1
        # sid = self.sheetID.get()
        # import csv
        # with open('report.csv', 'w', newline='') as f:
        #     writer = csv.writer(f)
        #     writer.writerows(report)
        # write_to_sheet(sid,report)
# class ProcessedHardDrives(GenerateReport):
#     def __init__(self,parent,*args,**kwargs):
#         #tk.Frame.__init__(self,parent,*args)
#         GenerateReport.__init__(self,parent,
#             ini_section = kwargs['ini_section'],
#             donationID = kwargs['donationID'],
#             sheetID = kwargs['sheetID'])
#         self.sheetID = kwargs['sheetID']
#         #DBI.__init__(self,ini_section = kwargs['ini_section'])
#         self.hdLabel = tk.Label(parent,text="Hard Drive Serial:")
#         self.hd = tk.Entry(parent,fg='black',bg='white',width=15)
#         self.wiperProduct = tk.StringVar(parent,value="Wiped?")
#         self.wiperProductMenu = tk.OptionMenu(parent,self.wiperProduct,
#                                             "Wiped.","Destroyed.")
#         self.finishHDButton = tk.Button(parent,
#             text='submit',
#             width = 15,
#             height = 2,
#             bg = "blue",
#             fg = "yellow",
#         )
#         self.finishHDButton.bind('<Button-1>',self.finishHD)
#         self.updateSheetButton = tk.Button(parent,
#             text='update Sheet',
#             width = 15,
#             height = 2,
#             bg = "blue",
#             fg = "yellow",
#         )
#         self.updateSheetButton.bind('<Button-1>',self.writeSheet)
#         self.err = tk.StringVar()
#         self.errorFlag = tk.Label(parent,textvariable=self.err)
#         self.hdLabel.grid(row=0,column=0)
#         self.hd.grid(row=0,column=1)
#         self.wiperProductMenu.grid(row=1,column=1)
#         self.errorFlag.grid(row=2,column=0)
#         self.finishHDButton.grid(row=2,column=1)
#         self.updateSheetButton.grid(row=3,column=1)
#     def finishHD(self,event):
#         now = datetime.datetime.now()
#         wiped = self.wiperProduct.get()
#         hd = self.hd.get()
#         if wiped == "Wiped.":
#             sql = DeviceInfo.noteWipedHD
#         elif wiped == "Destroyed.":
#             sql = DeviceInfo.noteDestroyedHD
#         try:
#             self.cur.execute(sql,(now,hd,))
#             self.conn.commit()
#             if len(self.cur.fetchall()) == 0:
#                 self.err.set('Error! Error! provided HD SN '+hd +' isn\'t in system!')
#             else:
#                 self.err.set('success!')
#             self.hd.delete(0,'end')
#         except (Exception, psycopg2.DatabaseError) as error:
#             self.err.set(error)
#         finally:
#             pass
