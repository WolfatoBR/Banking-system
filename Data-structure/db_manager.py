import sqlite3

class DataBaseManager():
    """Classe pra gerenciar"""

    def __init__(self, db_path):
        """Caminho do arquivo do banco de dados"""
        self.db_path = db_path
        self.conn = None

    def __enter__(self):
        """faz conexao com o banco ao entrar no bloco 'with'."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row #não me devolve tuplas. Em vez disso, me devolve objetos especiais do tipo sqlite3.Row para cada linha. (dict)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """fecha a conexao ao sair do bloco 'with'."""
        if self.conn:
            self.conn.commit()
            self.conn.close()
    
    def execute_query(self, query, params=()):
        """uma query pra uso interno"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor
    
    def create_table(self, table_name, columns):
        """
        Cria uma tabela de forma genérica.
        :param table_name: Nome da tabela a ser criada.
        :param columns: Um dicionário com {nome_coluna: tipo_e_constraints}.
        Ex: {'id': 'INTEGER PRIMARY KEY', 'name': 'TEXT NOT NULL'}
        """
        columns_with_types = [f"{name} {definition}" for name, definition in columns.items()]
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns_with_types)})"
        self.execute_query(query)
        print(f"Tabela '{table_name}' criada ou já existente.")

    def insert(self, table_name, data):
        """
        Insere um novo registro na tabela.
        :param table_name: Nome da tabela.
        :param data: Um dicionario com {nome_coluna: valor}.
        """

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.execute_query(query, tuple(data.values()))
        print(f"Registro inserido em '{table_name}'.")

    def update(self, table_name, data, condition):
        """
        Atualiza registros em uma tabela.
        :param table_name: Nome da tabela.
        :param data: Um dicionário com {nome_coluna: novo_valor}.
        :param condition: Um dicionário para a cláusula WHERE, ex: {'id': 1}.
        """
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        condition_clause = ' AND '.join([f"{key} = ?" for key in condition.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition_clause}"
        paramns = tuple(data.values()) + tuple(condition.values())
        self.execute_query(query, paramns)
        print(f"Registro em '{table_name}' atualizado.")

    def delete(self, table_name, condition):
        """
        Deleta registros de uma tabela.
        :param table_name: nome da tabela.
        :param condition: um dicionario pra clausula WHERE, ex: {'id': 1}.
        """
        condition_clause = ' AND '.join([f"{key} = ?" for key in condition.keys()])
        query = f"DELETE FROM {table_name} WHERE {condition_clause}"
        self.execute_query(query, tuple(condition.values()))
        print(f"Registro em '{table_name}' deletado.")

    def select(self, table_name, columns="*", condition=None, fetch_one=False):
        """
        Seleciona dados de uma tabela.
        :param table_name: Nome da tabela.
        :param columns: String das colunas a selecionar (padrão '*').
        :param condition: Dicionário para a cláusula WHERE (opcional).
        :param fetch_one: Se True, retorna apenas um registro, senão, todos.
        """
        query = f"SELECT {columns} FROM {table_name}"
        paramns = ()
        if condition:
            condition_clause = ' AND '.join([f"{key} = ?" for key in condition.keys()])
            query += f" WHERE {condition_clause}"
            paramns = tuple(condition.values())
        
        cursor = self.execute_query(query, paramns)

        if fetch_one:
            return cursor.fetchone()
        return cursor.fetchall()
    

### TESTE DE CLASSE 
if __name__ == '__main__':
    with DataBaseManager("generic_test.db") as db:
        
        #criando tabela
        user_columns = {
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'name': 'TEXT NOT NULL',
            'email': 'TEXT UNIQUE'
        }
        db.create_table('users', user_columns)

        #inserindo dados
        db.insert('users', {'name': 'Arthur', 'email': 'arthur@moreira.com'})
        db.insert('users', {'name': 'Fabiane', 'email': 'fabi@biane.com'})

        #selecionando todos os dados
        print("\n--- Todos os usuarios ---")
        all_users = db.select('users')
        for user in all_users:
            print(dict(user))

        #selecionando um dado especifico
        print("\n--- Usuario Especifico (ID=2) ---")
        fabiane = db.select('users', condition={'id':2}, fetch_one=True)
        if fabiane:
            print(dict(fabiane))
        
        #atualiza um dado
        db.update('users', {'email': 'fabiane@gail.com'}, {'id': 2})

        print("\n--- usuario Fabiane apos atualização ---")
        fabiane_update = db.select('users', condition={'id': 2}, fetch_one=True)
        if fabiane_update:
            print(dict(fabiane_update))

        #deletar um dado
        db.delete('users', {'id': 1})

        print("\n--- Todos os usuarios apos deletear Arthur ---")
        remaining_users = db.select('users')
        for user in remaining_users:
            print(dict(user))