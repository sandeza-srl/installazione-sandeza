try:
    import pyodbc as pypyodbc
except Exception as e:
    import pypyodbc as pypyodbc

config = {
    'occurrence':1800,
    'username_file':'UTENTEWEB',
    'pwd_file':'5U1U3RDH',
    'username_console':'Admin',
    'pwd_console':'admin',
    'driver':'/Library/ODBC/FileMaker ODBC.bundle/Contents/MacOS/fmodbc.so',
    'path_python':'../Sandeza/RC_Data_FMS/Updater/Updater/Python/',
    'path_clone':'../Sandeza/RC_Data_FMS/Updater/Updater/Clone/',
    'path_databases':'../Sandeza/',
    'version':'0.0.6',
    'script':1
}

special_characters = ('/','\\','\'','\"')

CONNECTION_STRINGS = {
    'dati': 'DRIVER=' + config['driver'] + ';SERVER=127.0.0.1;PORT=2399;charset=utf8;Database=Updater;UID=' + config['username_file'] + ';PWD=' + config['pwd_file'] + ''
}

def parse_select_query(query):
    fields_string = (query.split('SELECT '))[1].split(' FROM')[0].replace(" ", "")
    my_list = fields_string.split(',')
    return my_list 

# Funzione che ritorna un oggetto db, se connessione avvenuta
def get_connector_object(source):
    try:
        db = pypyodbc.connect(source)
        db.setencoding(encoding='utf-8')
        db.setdecoding(pypyodbc.SQL_WMETADATA, encoding='utf-8')
        db.setdecoding(pypyodbc.SQL_CHAR, encoding='utf-8')
        db.setdecoding(pypyodbc.SQL_WCHAR, encoding='utf-8')
        query = "SELECT CodiceVersione FROM Master_FilesInterfaccia where IdFile='E9EC8CC9-6B5E-46AF-924A-3313254CABA9'"
        cursor = db.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        result = row[0]
        return db
    except pypyodbc.Error as e:
        print(e)
        return False


if __name__ == '__main__':
    db = get_connector_object(CONNECTION_STRINGS['dati'])