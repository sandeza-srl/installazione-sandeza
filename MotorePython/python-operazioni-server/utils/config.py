config = {
    'connection_type':'RESTAPI', #RESTAPI per connettersi alle rest API o ODBC. Se non definito, default ODBC
    'endpoint':'https://localhost', # Endpoint di base per le chiamate API
    'occurrence':1800,
    'username_file':'UTENTEWEB',
    'pwd_file':'5U1U3RDH',
    'username_console':'SandezaServer',
    'pwd_console':'admin',
    'pwd_sistema':'password',
    'driver_mac':'/Library/ODBC/FileMaker ODBC.bundle/Contents/MacOS/fmodbc.so',
    'driver_win':'{FileMaker ODBC}',
    'path_python':'/opt/FileMaker/FileMaker Server/Data/Databases/Sandeza/RC_Data_FMS/Updater/Updater/Python/',
    'path_clone':'/opt/FileMaker/FileMaker Server/Data/Databases/Sandeza/RC_Data_FMS/Updater/Updater/Clone/',
    'path_databases':'/opt/FileMaker/FileMaker Server/Data/Databases/Sandeza/',
    'version':'0.0.6',
    'script':3
}

special_characters = ('/','\\','\'','\"')
