"""Livro digital (a quantidade representa licenças de acesso simultâneo)."""
from excecoes.erros import DadosInvalidosError
from modelos.material import Material


class LivroDigital(Material):
    TIPO = "livro_digital"
    MULTA_POR_DIA = 0.50

    def __init__(self, isbn, titulo, autor, tamanho_mb, formato, quantidade=1):
        super().__init__(isbn, titulo, quantidade)
        self.__autor = None
        self.__tamanho_mb = None
        self.__formato = None
        self.autor = autor
        self.tamanho_mb = tamanho_mb
        self.formato = formato

    @property
    def autor(self):
        return self.__autor

    @autor.setter
    def autor(self, valor):
        if not str(valor).strip():
            raise DadosInvalidosError("Autor não pode ser vazio.")
        self.__autor = str(valor).strip()

    @property
    def tamanho_mb(self):
        return self.__tamanho_mb

    @tamanho_mb.setter
    def tamanho_mb(self, valor):
        if not isinstance(valor, (int, float)) or valor <= 0:
            raise DadosInvalidosError("Tamanho do arquivo deve ser maior que zero.")
        self.__tamanho_mb = float(valor)

    @property
    def formato(self):
        return self.__formato

    @formato.setter
    def formato(self, valor):
        if not str(valor).strip():
            raise DadosInvalidosError("Formato não pode ser vazio.")
        self.__formato = str(valor).strip().upper()

    def calcular_multa(self, dias_atraso):
        return round(max(0, dias_atraso) * self.MULTA_POR_DIA, 2)

    def resumo(self):
        return (f"{super().resumo()} | Autor: {self.autor} | "
                f"{self.formato} {self.tamanho_mb:.1f} MB")

    def to_dict(self):
        dados = super().to_dict()
        dados.update({"autor": self.autor, "tamanho_mb": self.tamanho_mb, "formato": self.formato})
        return dados

    @classmethod
    def from_dict(cls, d):
        obj = cls(d["codigo"], d["titulo"], d["autor"], d["tamanho_mb"],
                  d["formato"], d["quantidade_total"])
        obj.restaurar_estado(d["disponivel"], d["total_emprestimos"])
        return obj
