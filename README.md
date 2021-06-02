
# Warehouse Management Microservices

The current iteration requires connection to a local Postgresql database
And Google Sheets

Prerequisites:



    1)    A Postgresql instance installed locally. Download from: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads

    2)    Google Credentials for the Google Sheets API
                Option 1:
                    In order to get access token,
                    Follow the steps at https://developers.google.com/sheets/api/quickstart/python
                    With SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
                Option 2:
                    Download the credentials for the google sheets API, move them
                    to your current working directory, rename them to credentials.json
                    and then run 'py Google_Sheets_Interface.py' to get a token from credentials.

<h1> Getting Started: </h1>
Download this repo, python and navigate here in powershell

        Step 1) Run "pip install -r Requirements.txt"
        Step 2) Create a database.ini file in your working directory with a section with the Postgresql install info
              [local_sheet]
              host=localhost
              port=5432
              database=database
              user=postgres
              password=password
        Step 2 cont.) Make sure database.ini is a ini file, not a text file.
        If not already selected, in file explorer, under view, under show/hide
        make sure that 'show file extensions' is checked
        Step 3) Run the 'py Initialize_Database.py' script to instantiate your Postgresql database
        Step 4) Run 'py Google_Sheets_Interface.py' to get a token. First you need to rename
        the credentials downloaded from Google to "credentials.json" and copy them to the working directory
        Step 5) Run 'py Extraction_Station.py' and insert some rows into the database

<h1>In order to compile a microservice:</h1>

        Step 1)  In Powershell, type "pyinstaller <example_micro>.py"
        Step 2)  Copy the following google directories below from your
                  Python Application install locations' Python//Lib/site-packages directory
                  To the dist/<example_micro> directory created by pyinstaller
                    {
                        google_api_core-1.25.0.dist-info
                        google_api_core-1.25.0-py3.9.egg-info
                        google_api_python_client-1.12.8.dist-info
                        google_auth_httplib2-0.0.4.dist-info
                        google_auth_oauthlib
                        google_auth_oauthlib-0.4.2.dist-info
                        google_auth-1.24.0.dist-info
                        googleapiclient
                        googleapis_common_protos-1.52.0.dist-info
                    }
