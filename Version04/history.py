from datetime import datetime
from abc import ABC, abstractmethod

class History:
    def __init__(self):
        self._transactions = []

    @property
    def transactions(self):
        return self._transactions

    def add_transaction(self, transaction):
        self._transactions.append(
            {
                "type": transaction.__class__.__name__,
                "value": transaction.value,
                "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )
    
    def generate_report(self, type_transaction=None):
        for transaction in self._transactions:
            if type_transaction is None or transaction["type"].lower() == type_transaction.lower():
                yield transaction