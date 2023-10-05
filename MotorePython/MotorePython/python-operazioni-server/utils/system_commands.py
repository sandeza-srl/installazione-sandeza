import os, subprocess

from zipfile import ZipFile

from utils.config import config, special_characters


# funzione per capire il tipo di sistema
def check_platform():
    if os.name == 'nt':
        # windows
        return 'windows'
    elif os.name == 'mac' or os.name == 'posix':
        # mac
        return 'mac'


# Funzione che ritorna True se Win
def isWin():
    if os.name == 'nt':
        # windows
        return True
    else:
        return False


# Funzione che ritorna True se Mac
def isMac():
    if os.name == 'mac' or os.name == 'posix':
        # mac
        return True
    else:
        return False


# Funzione che ritrova il giusto comando python in base alla piattaforma
def get_python_command(path_program):
    if isWin():
        #per windows devo rielaborare il path
        path_program = path_program.replace('\\','')
        path_program = path_program.replace('/','\\')
        path_program = "\"" + path_program + "\""
        command = 'python ' + path_program
    else:
        command = 'python3 ' + path_program
    return command


# funzione per aprire un file zip
def unzip(file_name, path):
    # create a reference to the file
    zip_ref = ZipFile(path + file_name)
    # estraggo
    zip_ref.extractall(path)
    zip_ref.close()
    return


# Funzione per analizzare la stringa di feedback dal terminale
def parse_response(response):
    # trasformo in stringa
    response = str(response)

    # rimuovo caratteri non supportati da SQL
    for char in special_characters:
        response = response.replace(char, "")

    # rimuovo la 'b' iniziale data da Popen
    if response[0] == 'b':
        response = response[1:]

    return response


# funzione che trova il path assoluto della cartella con i database
def find_location(file_name):
    dir_path = os.path.dirname(os.path.realpath(file_name))
    string_start = dir_path.find('python-operazioni-server')
    result = dir_path[:string_start]
    result = result.replace(' ','\ ')
    return result


# Funzione per eseguire comandi in terminale
def execute_command(command):
    # feedback comando da eseguire
    print('Comando da eseguire ' + str(command))

    # eseguo il comando
    result = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = result.communicate()

    out = parse_response(out)
    err = parse_response(err)

    if ('Error' in out or 'error' in out) and 'evaluation error' not in out:
        err += out
        out = ''

    return out, err


# funzione per eseguire un programma dalla consolle di FileMaker
def run_fm_schedule(program_id):
    # prendo le credenziali dal file di configurazione
    console_username = config['username_console']
    console_password = config['pwd_console']

    command = 'fmsadmin run schedule ' + program_id + ' -u ' + console_username + ' -p ' + console_password
    result, err = execute_command(command)

    return result, err
