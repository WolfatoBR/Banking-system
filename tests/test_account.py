import pytest
# importando as classes que iremos testar.
# Precisamos do 'Account' para testá-lo e do 'Individual' porque uma conta precisa de um cliente.
from engine.account import Account
from engine.individual import Individual

# O decorador '@pytest.fixture' transforma uma função em um "molde" 
# que prepara um cenário de teste reutilizável.
@pytest.fixture
def sample_accounnt():
    # aqui vamos fazer um "Arrange" -> organizar ; criar um cliente e uma conta 
    client = Individual(name="Dono Teste", birth_date="01-01-1990", cpf="123", address="Rua Teste")
    account = Account(number=1, client=client)
    # A palavra 'return' entrega o objeto 'account' pronto para qualquer 
    # teste que o solicitar.
    return account

def test_deposit_valid_amount(sample_accounnt):
    """Testa se um depósito com valor positivo funciona corretamente."""
    # Arrange (organizar)
    account = sample_accounnt

    # Act (agir) -> Executamos a única ação que queremos testar: 
    # o método deposit() com um valor válido.
    sucess = account.deposit(100.0)

    # Assert (Verificar) - Verificamos se o resultado foi o esperado.
    # Se qualquer uma dessas condições for falsa, o pytest irá parar e marcar o teste como FALHA.
    assert sucess is True, "O depósito deveria retornar True."
    assert account.balance == 100.0, "O saldo deveria ser 100.0 após o depósito."

# cenario de falha
def test_deposit_invalid_amount(sample_accounnt):
    """Testa se um deposito com valor negativo é rejeitado."""

    # arrange
    account = sample_accounnt

    # act
    sucess = account.deposit(-50.0)

    # assert
    assert sucess is False, "O deposito com valor negativo deveria retornar False."
    assert account.balance == 0, "O saldo não deveria mudar apos um deposito invalido."

def test_withdraw_sufficient_funds(sample_accounnt):
    """Testa se um saque bem-sucedido funciona."""

    # arrange: Primerio precisamos de um saldo na conta.
    account = sample_accounnt
    account.deposit(200.0) #saldo de 200

    # act: sacando um valor menor que o saldo.
    success = account.withdraw(150.0)

    # assert
    assert success is True
    assert account.balance == 50.0

def test_withdraw_insufficient_funds(sample_accounnt):
    """Testa a falha de saque por saldo insuficiente"""

    # arrange
    account = sample_accounnt
    account.deposit(100.0)

    # act
    success = account.withdraw(100.1)

    #assert
    assert success is False
    assert account.balance == 100.0, "O saldo não pode mudar se o saque falhou."