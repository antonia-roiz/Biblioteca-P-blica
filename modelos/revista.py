"""Revista (identificada pelo ISSN)."""
from excecoes.erros import DadosInvalidosError
from modelos.material import Material


class Revista(Material):
    TIPO = "revista"
    MULTA_POR_DIA = 0.75

    def __init__(self, issn, titulo, edicao, quantidade=1):
        super().__init__(issn, titulo, quantidade)
        self.__edicao = None
        self.edicao = edicao

    @property
    def edicao(self):
        return self.__edicao

    @edicao.setter
    def edicao(self, valor):
        if not str(valor).strip():
            raise DadosInvalidosError("Edição não pode ser vazia.")
        self.__edicao = str(valor).strip()

    def calcular_multa(self, dias_atraso):
        return round(max(0, dias_atraso) * self.MULTA_POR_DIA, 2)

    def resumo(self):
        return f"{super().resumo()} | Edição: {self.edicao}"

    def to_dict(self):
        dados = super().to_dict()
        dados["edicao"] = self.edicao
        return dados

    @classmethod
    def from_dict(cls, d):
        obj = cls(d["codigo"], d["titulo"], d["edicao"], d["quantidade_total"])
        obj.restaurar_estado(d["disponivel"], d["total_emprestimos"])
        return obj
