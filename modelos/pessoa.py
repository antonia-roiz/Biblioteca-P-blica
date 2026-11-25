"""Classe base para os usuários do sistema."""
from excecoes.erros import DadosInvalidosError


class Pessoa:
    def __init__(self, id_usuario, nome, cpf, email):
        self.__id = id_usuario
        self.__nome = None
        self.__cpf = None
        self.__email = None
        # Os setters validam os dados
        self.nome = nome
        self.cpf = cpf
        self.email = email

    # ---------- validações (reutilizáveis na entrada de dados) ----------
    @staticmethod
    def validar_cpf(cpf):
        """Retorna o CPF somente com dígitos ou levanta DadosInvalidosError."""
        digitos = "".join(c for c in str(cpf) if c.isdigit())
        if len(digitos) != 11:
            raise DadosInvalidosError("CPF deve conter 11 dígitos.")
        return digitos

    @staticmethod
    def validar_email(email):
        email = str(email).strip()
        if "@" not in email or "." not in email.split("@")[-1] or " " in email:
            raise DadosInvalidosError("E-mail inválido.")
        return email

    # ---------- propriedades ----------
    @property
    def id(self):
        return self.__id

    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, valor):
        if not str(valor).strip():
            raise DadosInvalidosError("Nome não pode ser vazio.")
        self.__nome = str(valor).strip()

    @property
    def cpf(self):
        return self.__cpf

    @cpf.setter
    def cpf(self, valor):
        self.__cpf = self.validar_cpf(valor)

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, valor):
        self.__email = self.validar_email(valor)

    # ---------- apresentação / persistência ----------
    def descricao(self):
        return f"[{self.id}] {self.nome} | CPF: {self.cpf} | {self.email}"

    def to_dict(self):
        return {"id": self.id, "nome": self.nome, "cpf": self.cpf, "email": self.email}
