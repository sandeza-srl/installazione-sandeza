'''
Programma installato su server come servizio che controlla se ci sono
operazioni da eseguire
'''

import time

from datetime import datetime
from utils.config import config
from utils.connector import do_query, get_connection_type, api_query
from utils.configuration_tester import greetings
from utils.system_commands import unzip, run_fm_schedule, execute_command, get_python_command
from utils.query_builder import QueryBuilder

# capisco il metodo di connessione
connection_type = get_connection_type()

# Funzione per comunicare a FileMaker che il motore è in esecuzione
def log_activity():
    # prendo il tempo
    hour = datetime.now().hour
    minute = datetime.now().minute
    seconds = datetime.now().second

    # scrivo nel log
    messaggio = str(hour) + ':' + str(minute) + ':' + str(seconds) + ':' + ' - Cerco operazioni..'
    print(messaggio, end='\r')
    if connection_type == 'RESTAPI':
        api_query('Updater', 'Cliente_LogOperazioniServer_API', 'create', creation_params={'Contenuto':'Motore Attivo'})
    else:
        query = "INSERT INTO Cliente_LogOperazioniServer (Contenuto) VALUES ('Motore Attivo')"
        do_query(query)


# Funzione per segnalare un errore
def log_error(file_id, err):
    # errore
    print('Errore ' + err)

    if connection_type == 'RESTAPI':
        # scrivo nel log
        api_query('Updater', 'Cliente_LogOperazioniServer_API', 'create', creation_params={'IdOperazione':file_id, 'Contenuto':err, 'FlagErroreCritico': 1})

        api_query('Updater', 'Cliente_OperazioniServer_API', 'update', search_params=[{'IdOperazione': file_id}], update_params={'FlagEseguiOra': 0} )

    else:
        # scrivo nel log
        QueryBuilder().insert('Cliente_LogOperazioniServer','IdOperazione','Contenuto','FlagErroreCritico')\
            .values(file_id,err,1).execute()

        # in caso di errore segno come da non eseguire ora, ma da eseguire al prossimo aggiornamento
        QueryBuilder().update('Cliente_OperazioniServer').set_field('FlagEseguiOra', 0).where('IdOperazione',file_id).execute()

# Funzione principale
def run():
    # saluto
    greetings()

    while True:

        # Scrivo che il motore è in esecuzione
        log_activity()

        # capisco se ci siano dei files dati da aggiornare
        if connection_type == 'RESTAPI':
            operations = api_query('Updater', 'Cliente_OperazioniServer_API', 'find', search_params=[{'FlagEseguiOra': 1}])
        else:
            operations = QueryBuilder().select('Descrizione','ComandoPython','NomeFilePython','IdOperazione')\
                .from_table('Cliente_OperazioniServer').where('FlagEseguiOra', 1).execute()

        if operations:
            i = 0
            for operation in operations:

                # estraggo le info necessarie dell'operazione
                operation = str(operations[i]['Descrizione'])
                unzip_name = str(operations[i]['NomeFilePython'])
                file_id = str(operations[i]['IdOperazione'])

                print('Operazione trovata: ' + operation)

                # capisco la posizione del file da eseguire
                python_path = str(config['path_python'] + file_id + '/')
                program_to_execute = str(config['script'])

                # unzip il programma python
                unzip(unzip_name, python_path)

                ############################################
                # L'eseguibile dovrebbe essere presente ora
                ############################################

                # provo con il primo path possibile
                path_program = python_path + unzip_name.replace('.zip', '/') + 'run.py'
                path_program = path_program.replace('../','')
                path_program = path_program.replace(' ','\ ')

                # unisco i risultati
                command = get_python_command(path_program)

                # eseguo il comando
                result, err = execute_command(command)
                if err:
                    log_error(file_id,err)

                if 'No such file' in err:
                    # programma non trovato, provo con un altro path
                    path_program = python_path + 'run.py'
                    path_program = path_program.replace('../','')
                    path_program = path_program.replace(' ', '\ ') 

                    # capisco la piattaforma
                    command = get_python_command(path_program)

                    # eseguo il comando
                    result, err = execute_command(command)

                    if err:
                        log_error(file_id,err)

                    else:

                        # lancio il programma da eseguire
                        if program_to_execute:
                            result, err = run_fm_schedule(program_to_execute)

                            if err:
                                log_error(file_id,err)

                        # segno l'operazione come eseguita
                        if connection_type == 'RESTAPI':
                            api_query('Updater', 'Cliente_OperazioniServer_API', 'update', search_params=[{'IdOperazione': file_id}], update_params={'FlagEseguito': 1} )
                        else:
                            QueryBuilder().update('Cliente_OperazioniServer').set_field('FlagEseguito', 1)\
                                .where('IdOperazione', file_id).execute()


                elif err:
                    log_error(file_id, err)

                else:

                    # lancio il programma da eseguire
                    if program_to_execute:
                        result, err = run_fm_schedule(program_to_execute)

                        if err:
                            log_error(file_id,err)

                    # segno l'operazione come eseguito
                    if connection_type == 'RESTAPI':
                        api_query('Updater', 'Cliente_OperazioniServer_API', 'update', search_params=[{'IdOperazione': file_id}], update_params={'FlagEseguito': 1} )
                    else:
                        QueryBuilder().update('Cliente_OperazioniServer').set_field('FlagEseguito', 1)\
                            .where('IdOperazione', file_id).execute()

                # feedback
                print('Operazione terminata.')

                i += 1

        # pausa
        time.sleep(config['occurrence'])


# run the program
run()
