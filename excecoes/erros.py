"""Exceções personalizadas do sistema de biblioteca."""


class BibliotecaError(Exception):
    """Classe base de todos os erros do sistema."""


class MaterialIndisponivelError(BibliotecaError):
    """Material sem exemplares disponíveis (ou reservado para outra pessoa)."""


class LimiteEmprestimosError(BibliotecaError):
    """Leitor atingiu o limite de empréstimos simultâneos."""


class AvaliacaoInvalidaError(BibliotecaError):
    """Nota fora do intervalo 1 a 5 ou avaliação não permitida."""


class DadosInvalidosError(BibliotecaError):
    """Dado de entrada inválido (CPF, e-mail, campo vazio etc.)."""


class NaoEncontradoError(BibliotecaError):
    """Usuário, material ou empréstimo não encontrado."""


class OperacaoInvalidaError(BibliotecaError):
    """Operação que viola uma regra do sistema."""
