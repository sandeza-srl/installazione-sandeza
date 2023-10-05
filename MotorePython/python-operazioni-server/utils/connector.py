from utils.config import config
from utils.system_commands import isMac

# Provo a capire che tipo di connessione usare
try:
    connection_type = config['connection_type']
except Exception as e:
    # se non trovo la chiave che specifica il tipo, default a ODBC
    connection_type = 'ODBC'

# Ricavo username e password
username = config['username_file']
password = config['pwd_file']

if connection_type == 'RESTAPI':
    
    # importo la libreria
    import fmrest
    
    # memorizzo l'endpoint
    base_endpoint = config['endpoint']

else:

    # importo le librerie
    try:
        import pyodbc as pypyodbc
    except Exception as e:
        import pypyodbc as pypyodbc

    # definisco le stringhe di connessione
    if isMac():
        CONNECTION_STRINGS = {
            'dati': 'DRIVER=' + config['driver_mac'] + ';SERVER=127.0.0.1;PORT=2399;DATABASE=Updater;UID=' + username + ';PWD=' + password + ''
        }
    else:
        CONNECTION_STRINGS = {
            'dati': 'DRIVER=' + config['driver_win'] + ';SERVER=127.0.0.1;PORT=2399;DATABASE=Updater;UID=' + username + ';PWD=' + password + ''
        }

# Funzione per ottenere il tipo di connessione
def get_connection_type():
    return connection_type

# Funzione che ritorna un oggetto db, se connessione avvenuta
def get_connector_object(source):
    try:
        db = pypyodbc.connect(source)
        db.setencoding(encoding='utf-8')
        db.setdecoding(pypyodbc.SQL_WMETADATA, encoding='utf-8')
        db.setdecoding(pypyodbc.SQL_CHAR, encoding='utf-8')
        db.setdecoding(pypyodbc.SQL_WCHAR, encoding='utf-8')
        return db
    except pypyodbc.Error as e:
        print(e)
        return False


# Funzione che ritorna una lista dei campi in una select query
def parse_select_query(query):
    fields_string = (query.split('SELECT '))[1].split(' FROM')[0].replace(" ", "")
    my_list = fields_string.split(',')
    return my_list


# Funzione per select query, che ritorna un dizionario
def do_select_query(query, params):

    # Initialize result
    result = []

    # Inizializzo i messaggi di errori 
    error = {'error': 'Query non eseguita. Problemi con connessione!'}

    db = get_connector_object(CONNECTION_STRINGS['dati'])
    if db:
        cursor = db.cursor()
        cursor.execute(query, params)

        # Loop result
        while True:
            row = cursor.fetchone()
            if not row:
                break
 
            query_result = {}

            fields = parse_select_query(query)
            i = 0
            for field in fields:
                content = row[i]
                query_result[field] = content
                i += 1 

            result.append(query_result)

        # Close
        cursor.close()
        db.close()

        return result

    else:
        return error


# Funzione per update o insert query
def do_query(query):
    db = pypyodbc.connect(CONNECTION_STRINGS['dati'])
    db.setencoding(encoding='utf-8')
    db.setdecoding(pypyodbc.SQL_WMETADATA, encoding='utf-8')
    db.setdecoding(pypyodbc.SQL_CHAR, encoding='utf-8')
    db.setdecoding(pypyodbc.SQL_WCHAR, encoding='utf-8')
    error = {'error': 'Query non eseguita. Problemi con connessione!'}
    if db:
        # Execute Query
        cursor = db.cursor()
        cursor.execute(query)

        # Close
        db.commit()
        cursor.close()
        db.close()
    else:
        return error


# Funzione per selezionare dei campi via API
def api_query(database, layout, action, search_params=None, update_params=None, creation_params=None):

    """Funzione utilizzata per eseguire query via api

    Parameters:
        database (str): nome del database a cui connettersi
        layout (str): nome del layout dove effettuare la query
        action (str): nome dell'azione da eseguire. Può essere ('find', 'update')
        (optional) search_params (list): lista contenente i dati da utilizzare nella query di ricerca, nel formato {'nome_campo':'valore'}
        (optional) update_params (dict): dict contenente i dati da utilizzare nella query di update, nel formato {'nome_campo':'valore'}
        (optional) creation_params (dict): dict contenente i dati da utilizzare nella query di creazione, nel formato {'nome_campo':'valore'}

    Returns:
        list: Una lista contenente i record trovati o vuota nel caso di update o insert
    """

    # inizializzo le azioni possibili
    ACTIONS = ('find', 'update', 'create')

    # inizializzo il risultato
    result = []

    # mi assicuro che l'azione sia fra quelle eseguibili
    if action in ACTIONS:

        # autenticazione
        fms = fmrest.Server(base_endpoint,
                    user=username,
                    password=password,
                    database=database,
                    layout=layout,
                    verify_ssl=False
                   )
        fms.login()

        # capisco l'azione da eseguire
        if action == 'find' and search_params:

            # eseguo una ricerca se ci sono dei parametri
            try:
                foundset = fms.find(search_params)
            except Exception as e:
                return result

            # aggiungo alla variabile risultato
            result.extend([record for record in foundset])

        elif action == 'update' and search_params and update_params:

            # trovo il record da aggiornare
            try:
                foundset = fms.find(search_params)
            except Exception as e:
                return result

            # aggiorno tutti i record trovati
            for record in foundset:

                # eseguo un update
                fms.edit_record(record.record_id, update_params)

        elif action == 'create' and creation_params:
            # creo il record
            record = fms.create_record(creation_params)
    
    return result
 