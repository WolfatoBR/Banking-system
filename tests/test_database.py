import pytest
import os
from engine import database as db

# O pytest nos fornece o 'tmp_path', um diretório temporário para nossos testes.
# O 'monkeypatch' nos permite modificar o comportamento de outros módulos.

@pytest.fixture
def setup_test_database(tmp_path, monkeypatch):
    """
    Essa fixture prepara um banco de dados limpo e temporario para cada teste.
    """
    # 1. define o caminho para um banco de dados de teste em uma pasta temporaria
    test_db_file = tmp_path / "test_banking.db"

    # 2. A MÁGICA: Usamos o monkeypatch para substituir a variável global DB_PATH
    #    no seu módulo 'database' pelo nosso caminho de teste. Agora, todas as
    #    funções em db.* usarão este banco de dados temporário.
    monkeypatch.setattr(db, 'DB_PATH', str(test_db_file))

    # 3. Cria as tabelas no banco de dados de teste.
    db.create_project_tables()

    # 4. 'yield' passa o controle para a função de teste.
    #    Nenhum código é necessário aqui, pois o banco já está pronto.
    yield

    # 5. O código após o yield (nenhum neste caso) rodaria para limpeza,
    #    mas o tmp_path do pytest já cuida de apagar tudo automaticamente.

def test_add_and_get_client(setup_test_database):
    """
    Testa se podemos adicionar um cliente e depois buscá-lo com sucesso.
    """

    # arrange
    cpf = "12345678900"
    name = "Cliente de Teste"
    birth_date = "01-01-2000"
    address = "Rua dos Testes, 123"

    # act
    success = db.add_client(cpf, name, birth_date, address)

    # assert
    assert success is True, "A adição de um novo cliente deveria retornar True."

    # act 2: busca o cliente que acabamos de adicionar.
    client_from_db = db.get_client_by_cpf(cpf)

    # Assert 2: Verifica se o cliente foi encontrado e se os dados estão corretos.
    assert client_from_db is not None
    assert client_from_db['cpf'] == cpf
    assert client_from_db['name'] == name

def test_add_account_for_existing_client(setup_test_database):
    """
    Testa a criação de uma conta para um cliente que ja existe.
    """
    # arrange
    client_cpf = "11122233344"
    db.add_client(client_cpf, "Cliente com Conta", "02-02-2002", "Av. Principal")

    # act
    new_account_number = db.add_account(agency="0001", balance=100.0, client_cpf=client_cpf)

    # assert
    assert new_account_number is not None
    assert new_account_number > 0

    # act 2: buscando conta
    accounts = db.get_accounts_by_client(client_cpf)

    # assert 2: verifica se a conta foi encontrada e os dados estao corretos
    assert len(accounts) == 1
    assert accounts[0]['number'] == new_account_number
    assert accounts[0]['balance'] == 100.0

def test_add_account_for_nonexistent_client(setup_test_database):
    """
    Testa se o sistema impede a criação de uma conta para um CPF que não existe.
    """
    # arrange
    noneexistent_cpf = "00000000000"

    # act: Tenta adicionar uma conta para este CPF
    result = db.add_account(agency="0001", balance=0, client_cpf=noneexistent_cpf)

    # assert: a função deve retornar None, indicando que a operação falhou
    assert result is None

def test_update_account_balance(setup_test_database):
    """
    Teste a atualização do saldo de uma conta.
    """
    # arrange: Cria um cliente e uma conta com saldo inicial.
    client_cpf = "33344455566"
    db.add_client(client_cpf, "Cliente Saldo", "03-03-2003", "Rua Financeira")
    account_number = db.add_account(agency="0001", balance=500.0, client_cpf=client_cpf)

    # act 
    db.update_account_balance(account_number, 750.50)

    # assert: Busca a conta novamente e verifica se o saldo foi realmente atualizado.
    accounts = db.get_accounts_by_client(client_cpf)
    assert accounts[0]['balance'] == 750.50