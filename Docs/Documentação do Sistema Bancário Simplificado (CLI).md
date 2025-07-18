# Documentação do Sistema Bancário Simplificado (CLI)

Este documento detalha o funcionamento de um sistema bancário básico implementado em Python, que opera através de uma interface de linha de comando (CLI). O sistema permite aos usuários realizar depósitos, saques e visualizar um extrato simplificado.

## 1\. Visão Geral do Sistema

O sistema é uma aplicação console que simula operações financeiras essenciais. Ele gerencia o saldo, um limite de saque por transação, um contador de saques e um extrato textual, tudo isso em memória durante a execução do programa. Não há persistência de dados; ao encerrar o programa, todas as informações são perdidas.

## 2\. Estrutura do Código

O código é linear e sequencial, utilizando um loop principal para interagir com o usuário e uma série de condicionais (`if/elif/else`) para processar as diferentes opções do menu.

### 2.1. Variáveis Globais de Estado

No início do script, diversas variáveis são inicializadas. Elas servem para armazenar o estado atual da conta e as configurações operacionais:

  * **`menu` (str)**:

      * **Descrição**: Uma string de múltiplas linhas que define a interface de usuário do menu principal. Apresenta as opções disponíveis para o usuário ([d] Depositar, [s] Sacar, [e] Extrato, [q] Sair).
      * **Exemplo**:
        ```
        [d] Depositar
        [s] Sacar
        [e] Extrato
        [q] Sair
        ```

  * **`balance` (float)**:

      * **Descrição**: Armazena o valor atual do saldo disponível na conta.
      * **Valor Inicial**: `0` (zero).

  * **`limit` (int)**:

      * **Descrição**: Define o valor monetário máximo permitido para um *único* saque.
      * **Valor Inicial**: `500`.

  * **`statement` (str)**:

      * **Descrição**: Acumula um registro textual de todas as operações de depósito e saque realizadas. Cada transação é adicionada como uma nova linha.
      * **Valor Inicial**: `""` (string vazia).

  * **`number_of_withdrawals` (int)**:

      * **Descrição**: Um contador que registra a quantidade de saques já efetuados na sessão atual.
      * **Valor Inicial**: `0` (zero).

  * **`WITHDRAWAL_LIMIT` (int)**:

      * **Descrição**: Uma constante que especifica o número máximo de saques permitidos que podem ser realizados.
      * **Valor Inicial**: `3`.

## 3\. Fluxo de Execução do Programa

O programa é controlado por um loop `while True` que garante a execução contínua até que o usuário decida sair.

### 3.1. Loop Principal (`while True`)

O loop principal gerencia a interação com o usuário:

```python
while True:
    option = input(menu)
    # ... (lógica das operações)
```

1.  **Exibição do Menu**: A cada iteração do loop, o conteúdo da variável `menu` é exibido na tela.
2.  **Entrada do Usuário**: A função `input()` aguarda que o usuário digite uma das opções do menu e pressione Enter. A entrada do usuário é armazenada na variável `option`.
3.  **Processamento da Opção**: A `option` é avaliada por uma série de declarações condicionais (`if/elif/else`) para determinar qual operação deve ser executada.

### 3.2. Operações Suportadas

#### 3.2.1. Depósito (`option == "d"`)

Esta seção lida com a funcionalidade de depósito de dinheiro na conta.

```python
    if option == "d":
        value = float(input("Informe o valor do deposito: "))

        if value > 0:
            balance += value
            statement += f"Deposito: R$ {value:.2f}\n"
        else:
            print("Operacao falhou! O valor informado é invalido.")
```

1.  **Solicitação de Valor**: O usuário é solicitado a ` Informe o valor do deposito:  `. A entrada é convertida para `float`.
2.  **Validação do Valor**:
      * **Condição**: `if value > 0:`
      * **Comportamento (Sucesso)**: Se o valor for maior que zero:
          * O `value` é adicionado ao `balance` (`balance += value`).
          * Uma linha formatada (`Deposito: R$ XX.YY\n`) é anexada à string `statement` para registrar a transação.
      * **Comportamento (Falha)**: Se o valor não for maior que zero:
          * Uma mensagem de erro `Operacao falhou! O valor informado é invalido.` é exibida.

#### 3.2.2. Saque (`option == "s"`)

Esta seção gerencia a funcionalidade de saque, aplicando diversas regras de negócio.

```python
    elif option == "s":
        value = float(input("Informe o valor do saque: "))

        exceeded_balance = value > balance
        exceeded_limit = value > limit
        exceeded_withdrawals = number_of_withdrawals >= WITHDRAWAL_LIMIT

        if exceeded_balance:
            print("Operação falhou! Você não tem saldo suficiente.")
        elif exceeded_limit:
            print("Operação falhou! O valor do saque ultrapassou o limite.")
        elif exceeded_withdrawals:
            print("Operação falhou! Número maximo de saques excedidos.")
        elif value > 0:
            balance -= value
            statement += f"Saque: R$ {value:.2f}\n"
            number_of_withdrawals += 1
        else:
            print("Operação falhou! O valor informado é invalido.")
```

1.  **Solicitação de Valor**: O usuário é solicitado a ` Informe o valor do saque:  `. A entrada é convertida para `float`.
2.  **Verificação de Condições de Falha**: Três variáveis booleanas são calculadas para verificar se o saque excede algum limite:
      * `exceeded_balance`: Verdadeiro se o `value` do saque for maior que o `balance` disponível.
      * `exceeded_limit`: Verdadeiro se o `value` do saque for maior que o `limit` por transação (500).
      * `exceeded_withdrawals`: Verdadeiro se o `number_of_withdrawals` atual for igual ou maior que o `WITHDRAWAL_LIMIT` (3).
3.  **Avaliação das Condições (Prioridade)**: As condições são verificadas em uma sequência específica para fornecer a mensagem de erro mais relevante:
      * **`if exceeded_balance:`**: Se o saldo for insuficiente, imprime `Operação falhou! Você não tem saldo suficiente.`.
      * **`elif exceeded_limit:`**: Caso contrário, se o valor exceder o limite por saque, imprime `Operação falhou! O valor do saque ultrapassou o limite.`.
      * **`elif exceeded_withdrawals:`**: Caso contrário, se o número de saques já excedeu o limite diário/sessão, imprime `Operação falhou! Número maximo de saques excedidos.`.
      * **`elif value > 0:`**: Se nenhuma das condições de falha anteriores for verdadeira E o `value` for positivo:
          * O `value` é subtraído do `balance` (`balance -= value`).
          * Uma linha formatada (`Saque: R$ XX.YY\n`) é anexada à string `statement`.
          * O `number_of_withdrawals` é incrementado (`number_of_withdrawals += 1`).
      * **`else:`**: Se o valor informado não for positivo, imprime `Operação falhou! O valor informado é invalido.`.

#### 3.2.3. Extrato (`option == "e"`)

Esta seção exibe o histórico de transações e o saldo atual da conta.

```python
    elif option == "e":
        print("\n================== Extrato =================")
        print("Não foram realizadas movimentações." if not statement else statement)
        print(f"\n Saldo: R$ {balance:.2f}")
        print("=============================================")
```

1.  **Cabeçalho**: Imprime `================== Extrato =================`.
2.  **Exibição do Histórico**:
      * **Condição**: `if not statement else statement`
      * **Comportamento**: Se a string `statement` estiver vazia (indicando que nenhuma transação foi registrada), a mensagem `Não foram realizadas movimentações.` é impressa. Caso contrário, o conteúdo completo da string `statement` (o histórico de depósitos e saques) é impresso.
3.  **Exibição do Saldo**: Imprime o `balance` atual, formatado para duas casas decimais (`Saldo: R$ XX.YY`).
4.  **Rodapé**: Imprime `=============================================`.

#### 3.2.4. Sair (`option == "q"`)

Esta opção permite que o usuário encerre o programa.

```python
    elif option == "q":
        break
```

1.  **`break`**: A instrução `break` é executada, o que termina imediatamente o loop `while True`. Isso faz com que o programa encerre sua execução.

#### 3.2.5. Opção Inválida (`else`)

Esta seção trata de qualquer entrada do usuário que não corresponda a uma opção válida do menu.

```python
    else:
        print("Operação invalida, porfavor selecione novamente a operação desejada.")
```

1.  **Mensagem de Erro**: Imprime `Operação invalida, porfavor selecione novamente a operação desejada.` para informar o usuário sobre a entrada incorreta.

-----