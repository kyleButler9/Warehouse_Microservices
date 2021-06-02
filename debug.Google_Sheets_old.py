from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import config
# If modifying these scopes, delete the file token.pickle.
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
    if 'sheet_' in kwargs:
        sheet_=kwargs['sheet_']
    else:
        sheet_='Sanitization Log'
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
    range_name=f'{sheet_}!A1:I10000'
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
        print('DEMO VALS USED - Navigate to: \n\n\thttps://docs.google.com/spreadsheets/d/1Ayl6fnWNx1doFUhdrLKJRKi7vksYh-h2lFDD2kJ8n7A')
        # that's values -> [columns] -> [[row],[row]]
        values = [[1,2,3],['a','b','c']]
        spreadsheet_id='1Ayl6fnWNx1doFUhdrLKJRKi7vksYh-h2lFDD2kJ8n7A'
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
if __name__ == '__main__':
    # You need to have a credentials.json file and a token.pickle file in your
    # working directory
    # run createSheet('sheetName') in order to create a sheet named sheetname
    # i.e.:
    # createSheet('demo42')
    print(createSheet('blopbleep'))
    pass
