import pytest
# importando classes necessarias para o teste 
from engine.individual import Individual
from engine.checkingAccount import CheckingAccount
from engine.deposit import Deposit
from engine.withdraw import Withdraw

@pytest.fixture
def sample_client():
    """Cria uma instancia de um client para os testes"""
    return Individual(name="Cliente Teste", birth_date="01-01-1990", cpf="123", address="Rua teste")

@pytest.fixture
def sample_account(sample_client):
    """Cria uma instancia de uma conta, associada ao cliente da outra fixture"""
    return CheckingAccount(number=1, client=sample_client)

def test_perform_valid_deposit(sample_client, sample_account):
    """
    Testa se o metodo perfm_transaction do cliente executa um deposito
    bem sucedido e atualiza o saldo da conta"""
    # arrange
    client = sample_client
    account = sample_account
    deposit_transaction = Deposit(100.0)

    # verificação inicial: o saldo da conta deve ser 0
    assert account.balance == 0

    # act : executando a ação
    success = client.perform_transaction(account, deposit_transaction)

    # assert
    assert success is True, "A transação de deposito deveria retornar True."
    assert account.balance == 100.0, "O saldo da conta deveria ser 100.0 apos o deposito"

def test_perform_failed_withdraw(sample_client, sample_account):
    """
    Testa se o metodo perform_transaction lida corretamente com uma transação
    que falha (saque sem saldo) e não altera o estado da conta."""
    # arrange
    client = sample_client
    account = sample_account
    withdraw_transaction = Withdraw(50.0)

    # verificação inicial
    assert account.balance == 0

    # act
    success = client.perform_transaction(account, withdraw_transaction)

    # assert
    assert success is False, "A transação de saque sen fundos deveria retornar False."
    assert account.balance == 0, "O saldo não pode mudar se a transação de saque falhou."