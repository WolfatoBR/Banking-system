from abc import ABC, abstractproperty, abstractclassmethod

class Transaction(ABC):
    @property
    @abstractproperty
    def value(self):
        pass
    
    @abstractclassmethod
    def register(self, account):
        pass