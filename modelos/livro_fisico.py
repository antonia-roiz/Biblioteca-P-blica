"""Livro físico."""
from excecoes.erros import DadosInvalidosError
from modelos.material import Material


class LivroFisico(Material):
    TIPO = "livro_fisico"
    MULTA_POR_DIA = 1.00

    def __init__(self, isbn, titulo, autor, quantidade):
        super().__init__(isbn, titulo, quantidade)
        self.__autor = None
        self.autor = autor

    @property
    def autor(self):
        return self.__autor

    @autor.setter
    def autor(self, valor):
        if not str(valor).strip():
            raise DadosInvalidosError("Autor não pode ser vazio.")
        self.__autor = str(valor).strip()

    def calcular_multa(self, dias_atraso):
        return round(max(0, dias_atraso) * self.MULTA_POR_DIA, 2)

    def resumo(self):
        return f"{super().resumo()} | Autor: {self.autor}"

    def to_dict(self):
        dados = super().to_dict()
        dados["autor"] = self.autor
        return dados

    @classmethod
    def from_dict(cls, d):
        obj = cls(d["codigo"], d["titulo"], d["autor"], d["quantidade_total"])
        obj.restaurar_estado(d["disponivel"], d["total_emprestimos"])
        return obj
