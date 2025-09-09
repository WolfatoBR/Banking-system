import sqlite3
from datetime import datetime

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
        cursor = self.execute_query(query, tuple(data.values()))
        print(f"Registro inserido em '{table_name}'.")
        return cursor.lastrowid    ## A propriedade cursor.lastrowid guarda o valor da coluna PRIMARY KEY gerado automaticamente pelo banco na última inserção.

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
        if not condition or len(condition) == 0:
            raise ValueError("Para evitar desastres, é necessario uma condição.") ## raise lança a exceção e interrompe o programa.
        
        condition_clause = ' AND '.join([f"{key} = ?" for key in condition.keys()])
        query = f"DELETE FROM {table_name} WHERE {condition_clause}"
        self.execute_query(query, tuple(condition.values()))
        print(f"Registro em '{table_name}' deletado.")

    def select(self, table_name, columns="*", condition=None, fetch_one=False, order_by=None):
        """
        Seleciona dados de uma tabela.
        :param table_name: Nome da tabela.
        :param columns: String das colunas a selecionar (padrão '*').
        :param condition: Dicionário para a cláusula WHERE (opcional).
        :param fetch_one: Se True, retorna apenas um registro, senão, todos.
        """
        query = f"SELECT {columns} FROM {table_name}"
        params = ()
        if condition:
            condition_clause = ' AND '.join([f"{key} = ?" for key in condition.keys()])
            query += f" WHERE {condition_clause}"
            params = tuple(condition.values())
        
        # adição feita para o extrato
        if order_by:
            query += f" ORDER BY {order_by}"
        
        cursor = self.execute_query(query, params)

        if fetch_one:
            return cursor.fetchone()
        return cursor.fetchall()

DB_PATH = "banking.db"

def create_project_tables():
    """Cria as tabelas 'clients' e 'accounts' para o projeto"""
    with DataBaseManager(DB_PATH) as db:
        client_columns = {
            'cpf' : 'TEXT PRIMARY KEY',
            'name' : 'TEXT NOT NULL',
            'birth_date' : 'TEXT NOT NULL',
            'address' : 'text not null'
        }
        db.create_table('clients', client_columns)

        account_columns = {
            'number' : 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'agency' : 'TEXT NOT NULL',
            'balance' : 'REAL NOT NULL',
            'client_cpf' : 'TEXT NOT NULL',
            'limit_value' : 'REAL DEFAULT 500',
            'withdraw_limit' : 'INTEGER DEFAULT 3',
            'FOREIGN KEY (client_cpf)' : 'REFERENCES clients (cpf)'
        }
        db.create_table('accounts', account_columns)

        transaction_columns = {
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'account_number': 'INTEGER NOT NULL',
            'transaction_type': 'TEXT NOT NULL',
            'value': 'REAL NOT NULL',
            'date': 'TEXT NOT NULL',
            'FOREIGN KEY (account_number)': 'REFERENCES accounts (number)'
        }
        db.create_table('transactions', transaction_columns)

    print("Tabelas prontas.")

def add_client(cpf, name, birth_date, address):
    """Adiciona um novo client no banco"""
    with DataBaseManager(DB_PATH) as db:
        try:
            db.insert('clients', {
                'cpf': cpf, 'name': name, 'birth_date': birth_date, 'address': address
            })
            return True
        except sqlite3.IntegrityError:
            #Erro se o cpf (primary key) ja estiver em uso
            return False

def add_account(agency, balance, client_cpf):
    """Adiciona uma conta para um cliente exixstente"""
    with DataBaseManager(DB_PATH) as db:
        #verificação
        client = db.select('clients', condition={'cpf': client_cpf}, fetch_one=True)
        if client:
            new_account_number = db.insert('accounts', {
                'agency': agency, 'balance': balance, 'client_cpf': client_cpf
            })
            return new_account_number
        return None #se o client não for encontrado vai retornar None

def get_client_by_cpf(cpf):
    """Busca e retorna os dados do cliente pelo CPF."""
    with DataBaseManager(DB_PATH) as db:
        return db.select('clients', condition={'cpf': cpf}, fetch_one=True)

def get_accounts_by_client(cpf):
    """Busca e retorna todas as contas associadas a um CPF."""
    with DataBaseManager(DB_PATH) as db:
        return db.select('accounts', condition={'client_cpf': cpf})

def get_all_clients():
    """Busca e retorna todos os clientes cadastrados."""
    with DataBaseManager(DB_PATH) as db:
        return db.select('clients')

def update_account_balance(account_number, new_balance):
    """Atualiza o saldo de uma conta especifica."""
    with DataBaseManager(DB_PATH) as db:
        return db.update('accounts', {'balance': new_balance}, {'number': account_number})

def add_transaction(account_number, transaction_type, value):
    """Adiciona um registro de transação no banco de dados"""
    with DataBaseManager(DB_PATH) as db:
        date_now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        db.insert('transactions', {
            'account_number': account_number,
            'transaction_type': transaction_type,
            'value': value,
            'date': date_now
        })

def get_transactions_by_account(account_number):
    """Busca todas as transações da conta especifica, ordenado por data"""
    with DataBaseManager(DB_PATH) as db:
        return db.select('transactions', condition={'account_number': account_number}, order_by='id ASC')

def delete_client(cpf):
    """Exclui um cliente e todas as suas contas associadas."""
    with DataBaseManager(DB_PATH) as db:
     # Primeiro deleta as contas, depois o cliente (devido à FOREIGN KEY)   
     db.delete('accounts', {'client_cpf': cpf})
     db.delete('clients', {'cpf': cpf})

def delete_account(account_number):
    """Exclui um conta especifica pelo seu numero."""
    with DataBaseManager(DB_PATH) as db:
        db.delete('accounts', {'number': account_number})

#Bloco para iniciar e testar rapido
# if __name__ == '__main__':
#     create_project_tables()
#     print("\nTeste rapido")
#     print("Cliente de teste inserido com sucesso.")
#     # Adicionando uma conta para o cliente
#     acc_id = add_account("0001", 1000.0, "12345678900")
#     print(f"Conta de teste criada com o número: {acc_id}")
# else:
#     print("Cliente de teste já existe.")

# print("\nTeste de leitura:")
# fulano = get_client_by_cpf("12345678900")
# if fulano:
#     print(dict(fulano))