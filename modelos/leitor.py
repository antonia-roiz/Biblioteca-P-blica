"""Leitor: usuário que pode pegar materiais emprestados."""
from datetime import date

from excecoes.erros import DadosInvalidosError
from modelos.pessoa import Pessoa


class Leitor(Pessoa):
    TIPO = "leitor"

    def __init__(self, id_usuario, nome, cpf, email, data_nascimento, limite_emprestimos=3):
        super().__init__(id_usuario, nome, cpf, email)
        self.__data_nascimento = None
        self.__limite_emprestimos = None
        self.data_nascimento = data_nascimento
        self.limite_emprestimos = limite_emprestimos

    @property
    def data_nascimento(self):
        return self.__data_nascimento

    @data_nascimento.setter
    def data_nascimento(self, valor):
        if not isinstance(valor, date) or valor > date.today():
            raise DadosInvalidosError("Data de nascimento inválida.")
        self.__data_nascimento = valor

    @property
    def limite_emprestimos(self):
        return self.__limite_emprestimos

    @limite_emprestimos.setter
    def limite_emprestimos(self, valor):
        if not isinstance(valor, int) or valor < 1:
            raise DadosInvalidosError("Limite de empréstimos deve ser um inteiro maior que zero.")
        self.__limite_emprestimos = valor

    def descricao(self):
        return (f"{super().descricao()} | Leitor | Nasc.: "
                f"{self.data_nascimento.strftime('%d/%m/%Y')} | Limite: {self.limite_emprestimos}")

    def to_dict(self):
        dados = super().to_dict()
        dados.update({
            "tipo": self.TIPO,
            "data_nascimento": self.data_nascimento.isoformat(),
            "limite_emprestimos": self.limite_emprestimos,
        })
        return dados

    @classmethod
    def from_dict(cls, d):
        return cls(d["id"], d["nome"], d["cpf"], d["email"],
                   date.fromisoformat(d["data_nascimento"]), d["limite_emprestimos"])
