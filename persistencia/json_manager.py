"""Leitura e gravação de arquivos JSON."""
import json
import os


class JsonManager:
    def __init__(self, pasta):
        self.__pasta = pasta
        os.makedirs(self.__pasta, exist_ok=True)

    def __caminho(self, nome_arquivo):
        return os.path.join(self.__pasta, nome_arquivo)

    def carregar(self, nome_arquivo):
        """Retorna a lista salva no arquivo (lista vazia se não existir ou estiver inválido)."""
        caminho = self.__caminho(nome_arquivo)
        if not os.path.exists(caminho):
            return []
        try:
            with open(caminho, "r", encoding="utf-8") as arquivo:
                return json.load(arquivo)
        except (json.JSONDecodeError, OSError):
            print(f"Aviso: não foi possível ler {nome_arquivo}. Iniciando vazio.")
            return []

    def salvar(self, nome_arquivo, dados):
        with open(self.__caminho(nome_arquivo), "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, indent=4, ensure_ascii=False)
