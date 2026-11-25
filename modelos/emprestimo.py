"""Registro de um empréstimo de material a um leitor."""
from datetime import date


class Emprestimo:
    def __init__(self, id_emprestimo, cpf_usuario, codigo_material, data_emprestimo,
                 data_prevista, data_devolucao=None, multa=0.0, avaliado=False):
        self.__id = id_emprestimo
        self.__cpf_usuario = cpf_usuario
        self.__codigo_material = codigo_material
        self.__data_emprestimo = data_emprestimo
        self.__data_prevista = data_prevista
        self.__data_devolucao = data_devolucao
        self.__multa = multa
        self.__avaliado = avaliado

    @property
    def id(self):
        return self.__id

    @property
    def cpf_usuario(self):
        return self.__cpf_usuario

    @property
    def codigo_material(self):
        return self.__codigo_material

    @property
    def data_emprestimo(self):
        return self.__data_emprestimo

    @property
    def data_prevista(self):
        return self.__data_prevista

    @property
    def data_devolucao(self):
        return self.__data_devolucao

    @property
    def multa(self):
        return self.__multa

    @property
    def avaliado(self):
        return self.__avaliado

    @property
    def devolvido(self):
        return self.__data_devolucao is not None

    def dias_atraso(self, data_referencia):
        """Dias de atraso em relação à data prevista (nunca negativo)."""
        return max(0, (data_referencia - self.__data_prevista).days)

    def registrar_devolucao(self, data_devolucao, multa):
        self.__data_devolucao = data_devolucao
        self.__multa = multa

    def marcar_avaliado(self):
        self.__avaliado = True

    def to_dict(self):
        return {
            "id": self.__id,
            "cpf_usuario": self.__cpf_usuario,
            "codigo_material": self.__codigo_material,
            "data_emprestimo": self.__data_emprestimo.isoformat(),
            "data_prevista": self.__data_prevista.isoformat(),
            "data_devolucao": self.__data_devolucao.isoformat() if self.__data_devolucao else None,
            "multa": self.__multa,
            "avaliado": self.__avaliado,
        }

    @classmethod
    def from_dict(cls, d):
        devolucao = d["data_devolucao"]
        return cls(
            d["id"], d["cpf_usuario"], d["codigo_material"],
            date.fromisoformat(d["data_emprestimo"]),
            date.fromisoformat(d["data_prevista"]),
            date.fromisoformat(devolucao) if devolucao else None,
            d["multa"], d["avaliado"],
        )
