"""Interface Avaliavel: contrato para qualquer item que possa ser avaliado."""
from abc import ABC, abstractmethod


class Avaliavel(ABC):
    @abstractmethod
    def avaliar(self, nota, comentario):
        """Registra uma avaliação (nota de 1 a 5 e comentário)."""

    @abstractmethod
    def calcular_media(self):
        """Retorna a média das avaliações."""
