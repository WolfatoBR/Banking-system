import sqlite3

DATABASE_FILE = "banking.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    # Retorna as linhas como dicionários para facilitar o acesso por nome de coluna
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
CREATE TABLE IF NOT EXISTS clients (
                   cpf TEXT PRIMARY KEY,
                   name TEXT NOT NULL,
                   birth_date TEXT NOT NULL,
                   address TEXT NOT NULL
                   );
""")
    
    cursor.execute("""
CREATE TABLE IF NOT EXISTS accounts(
                   number INTEGER PRIMARY KEY AUTOINCREMENT,
                   agency TEXT NOT NULL,
                   balance REAL NOT NULL,
                   client_cpf TEXT NOT NULL,
                   limit_value REAL DEFAULT 500,
                   withdraw_limit INTEGER DEFAULT 3,
                   FOREIGN KEY (client_cpf) REFERENCES clients (cpf)
                   );
""")
    conn.commit()
    conn.close()

def add_client(cpf, name, birth_date, address):
    """Adiciona um cliente no BD"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO clients (cpf, name, birth_date, address) VALUES (?, ?, ?, ?)",
            (cpf, name, birth_date, address)
        )
        conn.commit()
        print(f"Cliente {name} adicionado com sucesso.")
        return True
    except sqlite3.IntegrityError:
         #se tentarmos inserir um CPF que já existe (PRIMARY KEY duplicada)
        print(f"Erro: CPF {cpf} ja cadastrado.")
        return False
    finally:
        conn.close()

def add_account(agency, balance, client_cpf):
    """Adiciona uma nova conta no BD, de acordo coom o cliente"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT cpf FROM clients WHERE cpf = ?", (client_cpf,))
    if cursor.fetchone() is None:
        print(f"Erro: Cliente com CPF {client_cpf} não encontrado.")
        conn.close()
        return None
    
    try:
        cursor.execute(
            "INSERT INTO accounts (agency, balance, client_cpf) VALUES (?, ?, ?)",
            (agency, balance, client_cpf)
            )
        new_account_number = cursor.lastrowid #  retorna o ID da última linha inserida.
        conn.commit()
        print(f"Conta número {new_account_number} criada para o cliente {client_cpf}.")
        return new_account_number
    finally:
        conn.close()

def get_client_by_cpf(cpf):
    """Busca e retorna os dados de um cliente pelo CPF."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM clients WHERE cpf = ?", (cpf,))
    client = cursor.fetchone() #pega apenas a primeira linha que a consulta encontrou. Como o CPF é único, haverá no máximo uma linha, então fetchone() é perfeito aqui. Se nenhum cliente for encontrado, ele retornará None.
    
    conn.close()
    return client

def get_accounts_by_client(cpf):
    """Busca e retorna todas as contas associadas a um CPF."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM accounts WHERE client_cpf = ?", (cpf,))
    accounts = cursor.fetchall()#  (buscar todos) pega todas as linhas que a consulta SQL encontrou e as retorna como uma lista.

    conn.close()
    return accounts

def get_all_clients():
    """Busca e retorna todos os clientes cadastrados."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clients")
    all_clients = cursor.fetchall()

    conn.close()
    return all_clients

def update_account_balance(account_number, new_balance):
    """Atualiza o saldo de alguma conta"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE accounts SET balance = ? WHERE number = ?",
        (new_balance, account_number)
    )
    conn.commit()
    conn.close()

def delete_client(cpf):
    """Deleta o clientes e todas as suas contas"""
    conn = get_db_connection()
    cursor = conn.cursor()

    """Deletar todas as contas de acordo com o CPF"""
    cursor.execute(
        "DELETE FROM accounts WHERE client_cpf = ?",
        (cpf,)
    )  ### No Python, quando você passa um único item para a função cursor.execute(), ele precisa estar dentro de uma tupla. A forma de criar uma tupla de um elemento só é colocando uma vírgula depois dele.
    """Deleta o cliente"""
    cursor.execute(
        "DELETE FROM clients WHERE cpf = ?", (cpf,)
    )
    conn.commit()
    change = conn.total_changes # diz quantas linhas foram modificadas
    conn.close()

    #aqui vai retornar True se algo foi deletado, se não vai retornar false
    return change > 0 

def delete_account(number_account):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM accounts WHERE number = ?", (number_account))
    conn.commit()
    change = conn.total_changes
    conn.close()

    return change > 0


if __name__ == "__main__":
    print("Inicializando o banco de dados e criando as tabelas...")
    create_tables()
    print("Banco de dados pronto.")