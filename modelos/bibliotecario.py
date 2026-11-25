"""Bibliotecário: funcionário responsável pelo acervo."""
from excecoes.erros import DadosInvalidosError
from modelos.pessoa import Pessoa


class Bibliotecario(Pessoa):
    TIPO = "bibliotecario"

    def __init__(self, id_usuario, nome, cpf, email, matricula, setor):
        super().__init__(id_usuario, nome, cpf, email)
        self.__matricula = None
        self.__setor = None
        self.matricula = matricula
        self.setor = setor

    @property
    def matricula(self):
        return self.__matricula

    @matricula.setter
    def matricula(self, valor):
        if not str(valor).strip():
            raise DadosInvalidosError("Matrícula não pode ser vazia.")
        self.__matricula = str(valor).strip()

    @property
    def setor(self):
        return self.__setor

    @setor.setter
    def setor(self, valor):
        if not str(valor).strip():
            raise DadosInvalidosError("Setor não pode ser vazio.")
        self.__setor = str(valor).strip()

    def descricao(self):
        return f"{super().descricao()} | Bibliotecário | Matrícula: {self.matricula} | Setor: {self.setor}"

    def to_dict(self):
        dados = super().to_dict()
        dados.update({"tipo": self.TIPO, "matricula": self.matricula, "setor": self.setor})
        return dados

    @classmethod
    def from_dict(cls, d):
        return cls(d["id"], d["nome"], d["cpf"], d["email"], d["matricula"], d["setor"])
