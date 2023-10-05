from utils.connector import do_query, do_select_query


# Classe per costruire delle query
class QueryBuilder:

    def __init__(self):
        self.query = ''
        self.query_select = 0

    # Metodo per select query
    def select(self, *args):
        self.query = 'SELECT '
        for field in args:
            self.query += field + ','

        # rimuovi ultima virgola
        self.query = self.query[:-1]
        self.query_select = 1

        return self

    # Metodo per aggiungere from
    def from_table(self, table_name):
        self.query += ' FROM ' + table_name
        return self

    # Metodo per aggiungere where
    def where(self, field_name, value):
        if type(value) is int:
            self.query += ' WHERE ' + field_name + '=' + str(value)
        else:
            self.query += ' WHERE ' + field_name + '=\'' + str(value) + '\''
        return self

    # Metodo per update query
    def update(self, table_name):
        self.query = 'UPDATE ' + table_name
        return self

    # Metodo per il set in un update
    def set_field(self, field_name, value):
        if type(value) is int:
            self.query += ' SET ' + field_name + '=' + str(value)
        else:
            self.query += ' SET ' + field_name + '=\'' + str(value) + '\''
        return self

    # Metodo per un insert
    def insert(self, table_name, *args):
        s = 'INSERT INTO ' + table_name + ' ('
        for field in args:
            s += field + ','
        s = s[:-1] + ')'
        self.query = s
        return self

    # Metodo per values di un insert
    def values(self, *args):
        self.query += ' VALUES ('
        for value in args:
            if type(value) is int:
                self.query += str(value) + ','
            else:
                self.query += '\'' + str(value) + '\','
        self.query = self.query[:-1] + ')'
        return self

    # Metodo per eseguire la query
    def execute(self):
        if self.query_select:
            params = ()
            # query di tipo select
            result = do_select_query(self.query,params)
        else:
            # altra tipo di query
            result = do_query(self.query)
        return result
