import database as db
import os

TEST_DB_FILE = "test_banking.db"

db.DATABASE_FILE = TEST_DB_FILE

def test_db():
    """Testando todas as funções do arquivo DB"""

    print("--- INICIANDO TESTES NO BANCO DE DADOS ---")

    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
        print(f"Arquivo de teste anterior {TEST_DB_FILE} removido!")
    
    print("\n[TESTE 1] Criação de tabelas")
    db.create_tables()
    print("Tabelas criadas!")

    print("\n[TESTE 2] Inserção de clientes")
    db.add_client("05341968530", "Arthur", "02-03-2005", "Rua B")
    db.add_client("11122233344", "João da Silva", "01-01-1990", "Rua A, 123")
    db.add_client("55566677788", "Maria Oliveira", "05-05-1985", "Avenida B, 456")
    print("-> Tentando inserir cliente com CPF duplicado (esperado falhar):")
    db.add_client("11122233344", "João Duplicado", "02-02-1992", "Rua C, 789")

    acc_num_1 = db.add_account("0001", 1500.00, "11122233344")
    acc_num_2 = db.add_account("0001", 3500.00, "05341968530")
    print(f"Contas criadas com numeros: {acc_num_1} e {acc_num_2}")

    print("\n[TESTE 3] Leitura de dados...")
    print("Buscando client João...")
    joao = db.get_client_by_cpf("11122233344")
    print(dict(joao)) #transformando em dict pra melhor visu

    print("\n-> Listando todos os clientes:")
    all_clients = db.get_all_clients()
    for client in all_clients:
        print(dict(client))

    print(f"\n-> Listando contas do cliente João :")
    joao_accounts = db.get_accounts_by_client("11122233344")
    for account in joao_accounts:
        print(dict(account))

    print("\n[Teste 4] Atualizando saldo...")
    new_balance = 5002.50
    print(f"-> Atualizando saldo da conta {acc_num_2} para R$ {new_balance}")
    db.update_account_balance(acc_num_2, new_balance)
    print("-> Buscando conta novamente para verificar a atualização:")

    accounts_list = db.get_accounts_by_client("05341968530")
    if accounts_list:
        updated_account = accounts_list[0] 
        print(dict(updated_account))
        if updated_account['balance'] == new_balance:
            print("Saldo atualizado com SUCESSO.")
        else:
            print("FALHA na atualização do saldo.")
    else:
        print("FALHA: Nenhuma conta encontrada para o cliente após a atualização.") 

    print("\n[TESTE 5] Excluindo dados...")
    print("-> Deletando cliente João (CPF 111...). Isso também deve deletar sua conta.")
    deleted = db.delete_client("11122233344")
    if deleted:
        print("Cliente deletado com SUCESSO.")
    else:
        print("FALHA ao deletar o cliente.")
    

    print("Listando os clientes dnv... (joao não deve aparecer)")
    all_clients_after_delete = db.get_all_clients()

    if not all_clients_after_delete:
        print("Nenhum cliente na lista")
    else:
        for client in all_clients_after_delete:
            print(dict(client))
    
    print("Testes finalixados")

if __name__ == "__main__":
    test_db()