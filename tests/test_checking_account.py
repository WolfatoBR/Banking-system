import pytest

# 'CheckingAccount' é a classe que estamos testando.
# 'Individual' é necessária para criar um cliente para a conta.
from engine.checkingAccount import CheckingAccount
from engine.individual import Individual

@pytest.fixture
def sample_checking_account():
    """
    Cria uma instância de CheckingAccount com valores padrão para ser usada nos testes.
    Limite de saque por operação: R$ 500.
    """

    # arrange (organizar)
    client = Individual(name="Dona Conta Corrente", birth_date="01-01-1990", cpf="123", address="Rua Teste")
    account = CheckingAccount(number=1, client=client, limit=500)

    return account

def test_withdraw_within_limit_and_balance(sample_checking_account):
    """
    Testa um saque valido, que está dentro do limite por operação e do saldo disponivel.
    """
    # arrange
    account = sample_checking_account
    account.deposit(1000.0)

    # act
    success = account.withdraw(400.0)

    # asssert
    assert success is True
    assert account.balance == 600.0

def test_withdraw_exceeding_operation_limit(sample_checking_account):
    """
    Testa a falha de um saque onde o valor excede o limite por operação (R$ 500),
    mesmo que o saldo seja suficiente.
    """
    # arrange
    account = sample_checking_account
    account.deposit(2000.0)

    # act
    success = account.withdraw(500.1)

    # assert
    assert success is False
    assert account.balance == 2000.0, "O saldo não pode mudar se o saque excedeu o limite."

def test_withdraw_with_insufficient_funds_but_within_limit(sample_checking_account):
    """
    Testa a falha de um saque onde o valor esta dentro do limite de operação,
    mas é maior que o saldo disponivel.
    """
    # arrange
    account = sample_checking_account
    account.deposit(300.0)

    # act
    success = account.withdraw(400.0)

    # assert
    assert success is False
    assert account.balance == 300.0, "O saldo não deve mudar se for insuficiente."
    