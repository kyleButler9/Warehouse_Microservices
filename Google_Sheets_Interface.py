# google sheets references:
#   https://www.youtube.com/watch?v=VLdrgE8iJZI
#   https://developers.google.com/sheets/api/guides/concepts
#   https://developers.google.com/sheets/api/quickstart/python

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import *
# If modifying these scopes, delete the file token.pickle allowing it to be regenerated.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
def creds():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds
def HTTP_decorator(http):
    # This function shaves off the front part of the (user input relevent)
    # provided http address if the provided string is longer then
    # a google sheets id (length ~ 42)
    if len(http) > 45:
        bc = r'/d/'
        try:
            ec = r'/edit'
        except:
            ec = r'/'
        finally:
            begin = http.index(bc) + len(bc)
            end = http.index(ec)
            return http[begin:end]
    else:
        return http
def create_Sanitization_Sheet(title):
    service = build('sheets', 'v4', credentials=creds())

    # Call the Sheets API
    sheet = service.spreadsheets()
    # here is where the input to the function is applied
    # to label the document on google sheets.
    spreadsheet = {
        "sheets" : [
                    {'properties': {'title': 'Sanitization Log'}},
                    {'properties': {'title': 'Quality Check'},}
                    ],
        'properties' : {'title': title}
        }
    spreadsheet = service.spreadsheets().create(body=spreadsheet,
                                        fields='spreadsheetId').execute()
    # In order to print the id needed to put into the http address of the sheet at:
    # https://docs.google.com/spreadsheets/d/ + spreadsheet.get('spreadsheetId')

    return spreadsheet.get('spreadsheetId')

def write_to_sheet(*args,**kwargs):
    """
    overwrites values in a given spreadsheet.
    """
    # values is the list of lists that is to be written to spreadsheet_id.
    # it is structured like  [[row],[row],...].
    if 'tab' in kwargs:
        tab=kwargs['tab']
    else:
        tab='Sanitization Log'
    try:
        spreadsheet_id, values = args
        # print('Sheet Located Here: \n\n\thttps://docs.google.com/spreadsheets/d/'+spreadsheet_id)
    except ValueError:
        # that's values -> [columns] -> [[row],[row]]
        values = [[None,2,4],['12345',None,'765']]
        spreadsheet_id='1Ayl6fnWNx1doFUhdrLKJRKi7vksYh-h2lFDD2kJ8n7A'
        print(f'DEMO VALS USED - Navigate to: \n\n\thttps://docs.google.com/spreadsheets/d/{spreadsheet_id}')

    service = build('sheets', 'v4', credentials=creds())

    # Call the Sheets API
    sheet = service.spreadsheets()

    # here are some example values:
    #   spreadsheet_id='1CTNI6vX1wi-9VKdQVpOfpqnZ1XOy-xCe9zIltSX08o4'
    #   values = [[1,2,3],['a','b','c']]
    # the use of None as an entry
    # i.e. [[1,None,3],['a','b',None]]
    # will toggle the command to not overwrite legacy values in place in those cells.
    # recall that write_to_sheet, as opposed to append_to_sheet, requires a statement of the entire sheet
    # starting at the first column of the first row all the way to the cell you actually want to update the contents of
    #
    # note that the input to body is a list of lists as:
    body = {
        'values': values
    }
    range_name=f'{tab}!A1:I10000'
    value_input_option = 'USER_ENTERED'
    result = service.spreadsheets().values().update(
        spreadsheetId=HTTP_decorator(spreadsheet_id), range=range_name,
        valueInputOption=value_input_option, body=body).execute()
    out='{0} cells updated.'.format(result.get('updatedCells'))
    return out
def append_to_sheet(*args):
    """Shows basic usage of the Sheets API.
    appends values to a given spreadsheet.
    """
    try:
        spreadsheet_id, values = args
    except ValueError:
        # that's values -> [columns] -> [[row],[row]]
        values = [[1,2,3],['a','b','c']]
        spreadsheet_id='1Ayl6fnWNx1doFUhdrLKJRKi7vksYh-h2lFDD2kJ8n7A'
        print('DEMO VALS {0} USED - Navigate to: \n\n\thttps://docs.google.com/spreadsheets/d/{1}'.format(values,spreadsheet_id))
    service = build('sheets', 'v4', credentials=creds())

    # Call the Sheets API
    sheet = service.spreadsheets()
    body = {
        'values': values
    }
    range_name='Sheet1!A1:I10000'
    value_input_option = 'USER_ENTERED'
    insert_Data_Option = 'INSERT_ROWS'
    result = service.spreadsheets().values().append(
        spreadsheetId=HTTP_decorator(spreadsheet_id), range=range_name,
        valueInputOption=value_input_option,insertDataOption=insert_Data_Option, body=body).execute()
    out='{0} cells updated.'.format(result.get('updatedCells'))
    return out
class UpdateSheets(DBI):
    def __init__(self,*args,**kwargs):
        if 'ini_section' in kwargs:
            DBI.__init__(self,ini_section = kwargs['ini_section'])
        self.donation_id=kwargs['donation_id']
        print('google_sheets/UpdateSheets successfully initialized.')
    def overWrite_qc(self,**kwargs):
        if 'tab_id' in kwargs:
            tab_id = kwargs['tab_id']
        else:
            tab_id='Quality Check'
        if 'sheet_id' in kwargs:
            sheet_id = kwargs['sheet_id']
        else:
            get_sheet_id = \
            """
            SELECT sheetid FROM beta.donations WHERE donation_id = %s;
            """
            try:
                sheet_id = self.fetchone(get_sheet_id,self.donation_id)[0]
            except:
                print('no sheet id returned for that lot')
                print('returned:',self.fetchone(get_sheet_id,self.donation_id))
        get_donationInfo = \
            """
            SELECT d.name, don.dateReceived, don.lotNumber
            FROM beta.donors d
            INNER JOIN beta.donations don USING (donor_id)
            WHERE don.donation_id = %s;
            """
        donationInfo=self.fetchone(get_donationInfo,self.donation_id)
        report = [
            ['Company Name: {}'.format(donationInfo[0])],
            ['Date Received: {} '.format(donationInfo[1].strftime('%m/%d/%Y'))],
            ['Lot Number: {}'.format(donationInfo[2])],
            ['']
        ]
        cols = 'Sample	HD Serial Number	Date Reviewed	Staff'
        report.append(cols.split('	'))
        # The use of the inner joins below necessitates the insertion of both
        # device type and staff into database in association with the
        # device in order to be returned by this query.
        qcInfo = \
        """
        SELECT hd.hdsn, TO_CHAR(qc.qcDate,'MM/DD/YYYY'),s.nameabbrev
        FROM beta.qualitycontrol qc
        LEFT OUTER JOIN beta.staff s USING (staff_id)
        INNER JOIN beta.harddrives hd USING (hd_id)
        INNER JOIN beta.donatedgoods g USING (hd_id)
        WHERE g.donation_id = %s;
        """
        devices = self.fetchall(qcInfo,self.donation_id)
        drive = [1]
        for device in devices:
            dlist = list(device)
            try:
                dlist[-1] = dlist[-1].strftime("%m/%d/%Y %H:%M")
            except:
                # raise exception here instead of print.
                # print('no datetime or datetime unacceptable so skipping time -> string conversion to "%m/%d/%Y %H:%M" format.')
                pass
            finally:
                report.append(drive + dlist)
                drive[0]+=1
        write_to_sheet(sheet_id,report,tab=tab_id)
        return self
    def overWrite_sanitization(self,**kwargs):
        if 'tab_id' in kwargs:
            tab_id = kwargs['tab_id']
        else:
            tab_id='Sanitization Log'
        if 'sheet_id' in kwargs:
            sheet_id = kwargs['sheet_id']
        else:
            get_sheet_id = \
            """
            SELECT sheetid FROM beta.donations WHERE donation_id = %s;
            """
            try:
                sheet_id = self.fetchone(get_sheet_id,self.donation_id)[0]
            except:
                print('no sheet id returned for that lot.')
                print('\nQuery returned:',self.fetchone(get_sheet_id,self.donation_id))
        get_donationInfo = \
            """
            SELECT d.name, don.dateReceived, don.lotNumber
            FROM beta.donations don
            INNER JOIN beta.donors d USING (donor_id)
            WHERE don.donation_id = %s;
            """
        donationInfo=self.fetchone(get_donationInfo,self.donation_id)
        report = [
            ['Company Name: {}'.format(donationInfo[0])],
            ['Date Received: {} '.format(donationInfo[1].strftime('%m/%d/%Y'))],
            ['Lot Number: {}'.format(donationInfo[2])],
            ['']
        ]
        cols = 'Drive	Item Type	Item Serial	HD Serial Number	Asset Tag	Destroyed	Data Sanitized	Staff	Entry Date'
        report.append(cols.split('	'))
        # The use of the inner joins below necessitates the insertion of both
        # device type and staff into database in association with the
        # device in order to be returned by this query.
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
        devices = self.fetchall(deviceInfo,self.donation_id)
        drive = [1]
        for device in devices:
            dlist = list(device)
            try:
                dlist[-1] = dlist[-1].strftime("%m/%d/%Y %H:%M")
            except:
                # raise exception here instead of print.
                # print('no datetime or datetime unacceptable so skipping time -> string conversion to "%m/%d/%Y %H:%M" format.')
                pass
            finally:
                report.append(drive + dlist)
                drive[0]+=1
        write_to_sheet(sheet_id,report,tab=tab_id)
        return self
def get_google_token(SCOPES = 'https://www.googleapis.com/auth/spreadsheets'):
    from google.oauth2.credentials import Credentials
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    SCOPES = [SCOPES]
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    return service
if __name__ == '__main__':
    if not os.path.exists('token.json'):
        get_google_token()
    # You need to have a credentials.json file and a token.pickle file in your
    # working directory
    # run createSheet('sheetName') in order to create a sheet named sheetname
    # i.e.:
    # createSheet('demo42')
    # write_to_sheet()
    pass
# deviceInfo = \
# """
# SELECT dt.deviceType, c.SN,
#     CASE WHEN hd.hdsn is NULL and hd.hdpid is NULL THEN COALESCE(hd.hdsn,'')
#         WHEN hd.hdsn is NULL THEN COALESCE(hd.hdsn,'N/A')
#         ELSE hd.hdsn END,
#     COALESCE(g.assetTag,'') as asset_tag, COALESCE(hd.destroyed,FALSE) as destroyed, COALESCE(hd.sanitized,FALSE) as sanitized,
#     (select nameabbrev from staff where staff_id=COALESCE(hd.staff_id,g.staff_id)),
#     COALESCE(TO_CHAR(hd.wipeDate,'MM/DD/YYYY HH24:MI'),TO_CHAR(g.intakeDate,'MM/DD/YYYY HH24:MI')) as date
# FROM donatedgoods g
# LEFT OUTER JOIN computers c on g.p_id = c.p_id
# INNER JOIN deviceTypes dt USING (type_id)
# LEFT OUTER JOIN harddrives hd on g.hd_id = hd.hd_id
# WHERE g.donation_id = %s
# ORDER BY g.intakeDate;
# """
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
#         donationID = self.donationID.get()
#         donationInfo = \
#             """
#             SELECT d.name, don.dateReceived, don.lotNumber
#             FROM donors d
#             INNER JOIN donations don ON don.donor_id = d.donor_id
#             WHERE don.donation_id = %s;
#             """
#         donationInfo=self.fetchone(donationInfo,donationID)
#         report = [
#             ['Company Name: {}'.format(donationInfo[0])],
#             ['Date Received: {} '.format(donationInfo[1].strftime('%m/%d/%Y'))],
#             ['Lot Number: {}'.format(donationInfo[2])],
#             ['']
#         ]
#         cols = 'Drive	Item Type	Item Serial	HD Serial Number	Asset Tag	Destroyed	Data Sanitized	Staff	Entry Date'
#         report.append(cols.split('	'))
#         # The use of the inner joins below necessitates the insertion of both
#         # device type and staff into database in association with the
#         # device in order to be returned by this query.
#         deviceInfo = \
#         """
#         SELECT dt.deviceType, c.SN,
#             CASE WHEN hd.hdsn is NULL and hd.hdpid is NULL THEN COALESCE(hd.hdsn,'')
#                 WHEN hd.hdsn is NULL THEN COALESCE(hd.hdsn,'N/A')
#                 ELSE hd.hdsn END,
#             COALESCE(g.assetTag,'') as asset_tag, COALESCE(hd.destroyed,FALSE) as destroyed, COALESCE(hd.sanitized,FALSE) as sanitized,
#             (select nameabbrev from beta.staff where staff_id=COALESCE(hd.staff_id,g.staff_id)),
#             COALESCE(TO_CHAR(hd.wipeDate,'MM/DD/YYYY HH24:MI'),TO_CHAR(g.intakeDate,'MM/DD/YYYY HH24:MI')) as date
#         FROM beta.donatedgoods g
#         LEFT OUTER JOIN beta.computers c on g.p_id = c.p_id
#         INNER JOIN beta.deviceTypes dt USING (type_id)
#         LEFT OUTER JOIN beta.harddrives hd on g.hd_id = hd.hd_id
#         WHERE g.donation_id = %s
#         ORDER BY g.intakeDate;
#         """
#         devices = self.fetchall(deviceInfo,donationID)
#         drive = [1]
#         for device in devices:
#             dlist = list(device)
#             try:
#                 dlist[-1] = dlist[-1].strftime("%m/%d/%Y %H:%M")
#             except:
#                 # raise exception here instead of print.
#                 print('no datetime or datetime unacceptable so skipping time -> string conversion to "%m/%d/%Y %H:%M" format.')
#                 pass
#             finally:
#                 report.append(drive + dlist)
#                 drive[0]+=1
#         sid = self.sheetID.get()
#         # import csv
#         # with open('report.csv', 'w', newline='') as f:
#         #     writer = csv.writer(f)
#         #     writer.writerows(report)
#         write_to_sheet(sid,report)
# """
# SELECT dts.deviceType, c.sn, hd.hdsn,
#     dg.assettag, hd.destroyed, hd.sanitized, s.nameabbrev,
#     CASE WHEN hd.hdsn = '' THEN TO_CHAR(p.entryDate,'MM/DD/YYYY HH24:MI')
#     ELSE TO_CHAR(p.wipeDate,'MM/DD/YYYY HH24:MI')
#     END AS date
# FROM donatedgoods dg
# INNER JOIN deviceTypes dts on dts.type_id = p.deviceType_id
# INNER JOIN staff s on s.staff_id = p.staff_id
# WHERE p.donation_id = %s
# ORDER BY p.entryDate;
# """
