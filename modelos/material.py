"""Classe abstrata Material: base de livros físicos, digitais e revistas."""
from abc import abstractmethod

from excecoes.erros import AvaliacaoInvalidaError, DadosInvalidosError, MaterialIndisponivelError
from modelos.avaliavel import Avaliavel


class Material(Avaliavel):
    TIPO = "material"

    def __init__(self, codigo, titulo, quantidade):
        self.__codigo = None          # ISBN ou ISSN
        self.__titulo = None
        self.__quantidade_total = None
        self.__disponivel = None
        self.__total_emprestimos = 0
        self.__avaliacoes = []        # lista de dicts: cpf, nota, comentario

        if not str(codigo).strip():
            raise DadosInvalidosError("Código (ISBN/ISSN) não pode ser vazio.")
        if not str(titulo).strip():
            raise DadosInvalidosError("Título não pode ser vazio.")
        if not isinstance(quantidade, int) or quantidade < 1:
            raise DadosInvalidosError("Quantidade deve ser um inteiro maior que zero.")

        self.__codigo = str(codigo).strip()
        self.__titulo = str(titulo).strip()
        self.__quantidade_total = quantidade
        self.__disponivel = quantidade

    # ---------- propriedades ----------
    @property
    def codigo(self):
        return self.__codigo

    @property
    def titulo(self):
        return self.__titulo

    @titulo.setter
    def titulo(self, valor):
        if not str(valor).strip():
            raise DadosInvalidosError("Título não pode ser vazio.")
        self.__titulo = str(valor).strip()

    @property
    def quantidade_total(self):
        return self.__quantidade_total

    @property
    def disponivel(self):
        return self.__disponivel

    @property
    def total_emprestimos(self):
        return self.__total_emprestimos

    @property
    def avaliacoes(self):
        return list(self.__avaliacoes)  # cópia, preserva o encapsulamento

    @property
    def quantidade_avaliacoes(self):
        return len(self.__avaliacoes)

    @property
    def tipo(self):
        return self.TIPO

    # ---------- regras de negócio ----------
    def emprestar(self):
        """Reduz a quantidade disponível. Levanta erro se não houver exemplar."""
        if self.__disponivel <= 0:
            raise MaterialIndisponivelError(f"'{self.titulo}' não possui exemplares disponíveis.")
        self.__disponivel -= 1
        self.__total_emprestimos += 1

    def devolver(self):
        """Aumenta a quantidade disponível."""
        if self.__disponivel < self.__quantidade_total:
            self.__disponivel += 1

    @abstractmethod
    def calcular_multa(self, dias_atraso):
        """Cada tipo de material define sua regra de multa (polimorfismo)."""

    # ---------- interface Avaliavel ----------
    def avaliar(self, nota, comentario, cpf_usuario=""):
        if not isinstance(nota, int) or isinstance(nota, bool) or not 1 <= nota <= 5:
            raise AvaliacaoInvalidaError("A nota deve ser um inteiro de 1 a 5.")
        self.__avaliacoes.append({
            "cpf": cpf_usuario,
            "nota": nota,
            "comentario": str(comentario).strip(),
        })

    def calcular_media(self):
        if not self.__avaliacoes:
            return 0.0
        soma = sum(a["nota"] for a in self.__avaliacoes)
        return round(soma / len(self.__avaliacoes), 2)

    # ---------- apresentação / persistência ----------
    def resumo(self):
        return (f"[{self.TIPO}] {self.codigo} - {self.titulo} | "
                f"Disponível: {self.disponivel}/{self.quantidade_total} | "
                f"Média: {self.calcular_media():.2f} ({self.quantidade_avaliacoes} aval.) | "
                f"Empréstimos: {self.total_emprestimos}")

    def restaurar_estado(self, disponivel, total_emprestimos):
        """Usado ao carregar do JSON para restaurar contadores."""
        self.__disponivel = disponivel
        self.__total_emprestimos = total_emprestimos

    def to_dict(self):
        return {
            "tipo": self.TIPO,
            "codigo": self.codigo,
            "titulo": self.titulo,
            "quantidade_total": self.quantidade_total,
            "disponivel": self.disponivel,
            "total_emprestimos": self.total_emprestimos,
        }
