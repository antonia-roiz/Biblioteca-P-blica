"""Sistema Inteligente de Biblioteca Digital Comunitária - menu principal."""
import os
from collections import deque
from datetime import date, datetime, timedelta

from excecoes.erros import (
    BibliotecaError, DadosInvalidosError, LimiteEmprestimosError,
    MaterialIndisponivelError, NaoEncontradoError, OperacaoInvalidaError,
)
from modelos.bibliotecario import Bibliotecario
from modelos.emprestimo import Emprestimo
from modelos.leitor import Leitor
from modelos.livro_digital import LivroDigital
from modelos.livro_fisico import LivroFisico
from modelos.pessoa import Pessoa
from modelos.revista import Revista
from persistencia.json_manager import JsonManager

PRAZO_DIAS = 14
PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados")

# ---------- estruturas de dados exigidas ----------
usuarios = []                 # lista de Leitor / Bibliotecario
materiais = []                # lista de LivroFisico / LivroDigital / Revista
emprestimos = []              # lista de Emprestimo
fila_reservas = deque()       # fila de espera: dicts {"cpf": ..., "codigo": ...}
historico_emprestimos = {}    # cpf -> lista de Emprestimo

gerenciador = JsonManager(PASTA_DADOS)

TIPOS_USUARIO = {"leitor": Leitor, "bibliotecario": Bibliotecario}
TIPOS_MATERIAL = {"livro_fisico": LivroFisico, "livro_digital": LivroDigital, "revista": Revista}


# =====================================================================
# Entrada de dados com validação
# =====================================================================
def ler_texto(mensagem):
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print("Campo obrigatório.")


def ler_inteiro(mensagem, minimo=None, maximo=None):
    while True:
        try:
            valor = int(input(mensagem).strip())
        except ValueError:
            print("Digite um número inteiro.")
            continue
        if (minimo is not None and valor < minimo) or (maximo is not None and valor > maximo):
            print(f"Valor deve estar entre {minimo} e {maximo}." if maximo is not None
                  else f"Valor deve ser no mínimo {minimo}.")
            continue
        return valor


def ler_decimal(mensagem):
    while True:
        try:
            valor = float(input(mensagem).strip().replace(",", "."))
        except ValueError:
            print("Digite um número válido.")
            continue
        if valor <= 0:
            print("O valor deve ser maior que zero.")
            continue
        return valor


def ler_data(mensagem, opcional=False):
    """Lê data no formato DD/MM/AAAA. Se opcional, Enter retorna None."""
    while True:
        texto = input(mensagem).strip()
        if not texto and opcional:
            return None
        try:
            return datetime.strptime(texto, "%d/%m/%Y").date()
        except ValueError:
            print("Data inválida. Use o formato DD/MM/AAAA.")


def ler_validado(mensagem, validador):
    """Repete a pergunta até o validador aceitar o valor."""
    while True:
        try:
            return validador(input(mensagem))
        except DadosInvalidosError as erro:
            print(f"Erro: {erro}")


# =====================================================================
# Buscas
# =====================================================================
def buscar_usuario(cpf):
    for usuario in usuarios:
        if usuario.cpf == cpf:
            return usuario
    raise NaoEncontradoError("Usuário não encontrado.")


def buscar_material(codigo):
    for material in materiais:
        if material.codigo == codigo:
            return material
    raise NaoEncontradoError("Material não encontrado.")


def emprestimos_ativos(cpf):
    return [e for e in historico_emprestimos.get(cpf, []) if not e.devolvido]


def reconstruir_historico():
    historico_emprestimos.clear()
    for emp in emprestimos:
        historico_emprestimos.setdefault(emp.cpf_usuario, []).append(emp)


# =====================================================================
# Persistência
# =====================================================================
def salvar_tudo():
    gerenciador.salvar("usuarios.json", [u.to_dict() for u in usuarios])
    gerenciador.salvar("materiais.json", [m.to_dict() for m in materiais])
    gerenciador.salvar("emprestimos.json", [e.to_dict() for e in emprestimos])
    avaliacoes = []
    for material in materiais:
        for aval in material.avaliacoes:
            avaliacoes.append({"codigo_material": material.codigo, **aval})
    gerenciador.salvar("avaliacoes.json", avaliacoes)
    gerenciador.salvar("reservas.json", list(fila_reservas))


def carregar_tudo():
    for dados in gerenciador.carregar("usuarios.json"):
        usuarios.append(TIPOS_USUARIO[dados["tipo"]].from_dict(dados))
    for dados in gerenciador.carregar("materiais.json"):
        materiais.append(TIPOS_MATERIAL[dados["tipo"]].from_dict(dados))
    for dados in gerenciador.carregar("emprestimos.json"):
        emprestimos.append(Emprestimo.from_dict(dados))
    for aval in gerenciador.carregar("avaliacoes.json"):
        buscar_material(aval["codigo_material"]).avaliar(aval["nota"], aval["comentario"], aval["cpf"])
    for reserva in gerenciador.carregar("reservas.json"):
        fila_reservas.append(reserva)
    reconstruir_historico()


# =====================================================================
# Operações do menu
# =====================================================================
def cadastrar_usuario():
    print("\n--- Cadastrar usuário ---")
    print("1 - Leitor\n2 - Bibliotecário")
    tipo = ler_inteiro("Tipo: ", 1, 2)

    nome = ler_texto("Nome: ")
    cpf = ler_validado("CPF (11 dígitos): ", Pessoa.validar_cpf)
    if any(u.cpf == cpf for u in usuarios):
        raise OperacaoInvalidaError("Já existe usuário com esse CPF.")
    email = ler_validado("E-mail: ", Pessoa.validar_email)
    novo_id = max((u.id for u in usuarios), default=0) + 1

    if tipo == 1:
        while True:
            nascimento = ler_data("Data de nascimento (DD/MM/AAAA): ")
            if nascimento <= date.today():
                break
            print("A data não pode estar no futuro.")
        limite = ler_inteiro("Máximo de empréstimos simultâneos: ", 1)
        usuario = Leitor(novo_id, nome, cpf, email, nascimento, limite)
    else:
        matricula = ler_texto("Matrícula funcional: ")
        setor = ler_texto("Setor: ")
        usuario = Bibliotecario(novo_id, nome, cpf, email, matricula, setor)

    usuarios.append(usuario)
    salvar_tudo()
    print("Usuário cadastrado com sucesso!")


def cadastrar_material():
    print("\n--- Cadastrar material ---")
    print("1 - Livro físico\n2 - Livro digital\n3 - Revista")
    tipo = ler_inteiro("Tipo: ", 1, 3)

    codigo = ler_texto("ISBN: " if tipo != 3 else "ISSN: ")
    if any(m.codigo == codigo for m in materiais):
        raise OperacaoInvalidaError("Já existe material com esse código.")
    titulo = ler_texto("Título: ")

    if tipo == 1:
        autor = ler_texto("Autor: ")
        quantidade = ler_inteiro("Quantidade de exemplares: ", 1)
        material = LivroFisico(codigo, titulo, autor, quantidade)
    elif tipo == 2:
        autor = ler_texto("Autor: ")
        tamanho = ler_decimal("Tamanho do arquivo (MB): ")
        formato = ler_texto("Formato (PDF, EPUB, MOBI...): ")
        quantidade = ler_inteiro("Quantidade de licenças simultâneas: ", 1)
        material = LivroDigital(codigo, titulo, autor, tamanho, formato, quantidade)
    else:
        edicao = ler_texto("Edição: ")
        quantidade = ler_inteiro("Quantidade de exemplares: ", 1)
        material = Revista(codigo, titulo, edicao, quantidade)

    materiais.append(material)
    salvar_tudo()
    print("Material cadastrado com sucesso!")


def realizar_emprestimo():
    print("\n--- Realizar empréstimo ---")
    usuario = buscar_usuario(ler_validado("CPF do leitor: ", Pessoa.validar_cpf))
    if not isinstance(usuario, Leitor):
        raise OperacaoInvalidaError("Somente leitores podem fazer empréstimos.")
    material = buscar_material(ler_texto("ISBN/ISSN do material: "))

    ativos = emprestimos_ativos(usuario.cpf)
    if len(ativos) >= usuario.limite_emprestimos:
        raise LimiteEmprestimosError(
            f"Limite de {usuario.limite_emprestimos} empréstimos simultâneos atingido.")
    if any(e.codigo_material == material.codigo for e in ativos):
        raise OperacaoInvalidaError("O leitor já está com este material emprestado.")

    # Se há fila, só quem está entre os primeiros (conforme exemplares livres) pode retirar
    fila_material = [r for r in fila_reservas if r["codigo"] == material.codigo]
    if fila_material:
        primeiros = [r["cpf"] for r in fila_material[:material.disponivel]]
        if usuario.cpf not in primeiros:
            raise MaterialIndisponivelError(
                "Existem reservas na frente deste leitor na fila de espera.")

    material.emprestar()  # levanta MaterialIndisponivelError se não houver exemplar

    reserva = {"cpf": usuario.cpf, "codigo": material.codigo}
    if reserva in fila_reservas:
        fila_reservas.remove(reserva)

    hoje = date.today()
    emprestimo = Emprestimo(
        max((e.id for e in emprestimos), default=0) + 1,
        usuario.cpf, material.codigo, hoje, hoje + timedelta(days=PRAZO_DIAS))
    emprestimos.append(emprestimo)
    historico_emprestimos.setdefault(usuario.cpf, []).append(emprestimo)
    salvar_tudo()
    print(f"Empréstimo realizado! Devolução prevista para "
          f"{emprestimo.data_prevista.strftime('%d/%m/%Y')}.")


def realizar_devolucao():
    print("\n--- Realizar devolução ---")
    usuario = buscar_usuario(ler_validado("CPF do leitor: ", Pessoa.validar_cpf))
    material = buscar_material(ler_texto("ISBN/ISSN do material: "))

    emprestimo = next((e for e in emprestimos_ativos(usuario.cpf)
                       if e.codigo_material == material.codigo), None)
    if emprestimo is None:
        raise NaoEncontradoError("Não há empréstimo ativo deste material para este leitor.")

    data = ler_data("Data da devolução (DD/MM/AAAA, Enter = hoje): ", opcional=True) or date.today()
    if data < emprestimo.data_emprestimo:
        raise OperacaoInvalidaError("A devolução não pode ser anterior ao empréstimo.")

    atraso = emprestimo.dias_atraso(data)
    multa = material.calcular_multa(atraso)  # polimorfismo
    emprestimo.registrar_devolucao(data, multa)
    material.devolver()
    salvar_tudo()

    print("Devolução registrada!")
    if atraso > 0:
        print(f"Atraso de {atraso} dia(s). Multa: R$ {multa:.2f}")
    proximo = next((r for r in fila_reservas if r["codigo"] == material.codigo), None)
    if proximo:
        print(f"Aviso: o próximo da fila de espera é {buscar_usuario(proximo['cpf']).nome}.")


def reservar_material():
    print("\n--- Reservar material ---")
    usuario = buscar_usuario(ler_validado("CPF do leitor: ", Pessoa.validar_cpf))
    if not isinstance(usuario, Leitor):
        raise OperacaoInvalidaError("Somente leitores podem reservar materiais.")
    material = buscar_material(ler_texto("ISBN/ISSN do material: "))

    if material.disponivel > 0:
        raise OperacaoInvalidaError("Há exemplares disponíveis; faça o empréstimo diretamente.")
    if any(e.codigo_material == material.codigo for e in emprestimos_ativos(usuario.cpf)):
        raise OperacaoInvalidaError("O leitor já está com este material emprestado.")
    reserva = {"cpf": usuario.cpf, "codigo": material.codigo}
    if reserva in fila_reservas:
        raise OperacaoInvalidaError("O leitor já está na fila de espera deste material.")

    fila_reservas.append(reserva)
    salvar_tudo()
    posicao = len([r for r in fila_reservas if r["codigo"] == material.codigo])
    print(f"Reserva registrada! Posição na fila: {posicao}.")


def avaliar_material():
    print("\n--- Avaliar material ---")
    usuario = buscar_usuario(ler_validado("CPF do leitor: ", Pessoa.validar_cpf))
    material = buscar_material(ler_texto("ISBN/ISSN do material: "))

    emprestimo = next((e for e in historico_emprestimos.get(usuario.cpf, [])
                       if e.codigo_material == material.codigo and e.devolvido and not e.avaliado), None)
    if emprestimo is None:
        raise OperacaoInvalidaError(
            "Só é possível avaliar um material já devolvido e ainda não avaliado por você.")

    nota = ler_inteiro("Nota (1 a 5): ")
    comentario = input("Comentário (opcional): ").strip()
    material.avaliar(nota, comentario, usuario.cpf)  # levanta AvaliacaoInvalidaError se inválida
    emprestimo.marcar_avaliado()
    salvar_tudo()
    print(f"Avaliação registrada! Média atual: {material.calcular_media():.2f} "
          f"({material.quantidade_avaliacoes} avaliações).")


def consultar_materiais():
    print("\n--- Materiais cadastrados ---")
    if not materiais:
        print("Nenhum material cadastrado.")
    for material in materiais:
        print(material.resumo())


def consultar_usuarios():
    print("\n--- Usuários cadastrados ---")
    if not usuarios:
        print("Nenhum usuário cadastrado.")
    for usuario in usuarios:
        print(usuario.descricao())


def relatorio_emprestimos():
    print("\n--- Relatório de empréstimos ---")
    if not historico_emprestimos:
        print("Nenhum empréstimo registrado.")
    for cpf, lista in historico_emprestimos.items():
        print(f"\n{buscar_usuario(cpf).nome} (CPF {cpf}) - {len(lista)} empréstimo(s)")
        for emp in lista:
            titulo = buscar_material(emp.codigo_material).titulo
            if emp.devolvido:
                situacao = (f"devolvido em {emp.data_devolucao.strftime('%d/%m/%Y')} "
                            f"| multa R$ {emp.multa:.2f}")
            else:
                situacao = f"em aberto | previsto {emp.data_prevista.strftime('%d/%m/%Y')}"
            print(f"  #{emp.id} {titulo} | emprestado em "
                  f"{emp.data_emprestimo.strftime('%d/%m/%Y')} | {situacao}")


def recomendacoes():
    print("\n--- Recomendações ---")
    if not materiais:
        print("Nenhum material cadastrado.")
        return

    avaliados = [m for m in materiais if m.quantidade_avaliacoes > 0]
    por_media = sorted(avaliados, key=lambda m: (m.calcular_media(), m.quantidade_avaliacoes),
                       reverse=True)[:5]
    print("Mais bem avaliados:")
    if not por_media:
        print("  (ainda não há avaliações)")
    for posicao, m in enumerate(por_media, 1):
        print(f"  {posicao}. {m.titulo} - média {m.calcular_media():.2f} "
              f"({m.quantidade_avaliacoes} aval.)")

    emprestados = [m for m in materiais if m.total_emprestimos > 0]
    por_emprestimos = sorted(emprestados, key=lambda m: m.total_emprestimos, reverse=True)[:5]
    print("Mais emprestados:")
    if not por_emprestimos:
        print("  (ainda não há empréstimos)")
    for posicao, m in enumerate(por_emprestimos, 1):
        print(f"  {posicao}. {m.titulo} - {m.total_emprestimos} empréstimo(s)")


# =====================================================================
# Menu principal
# =====================================================================
MENU = """
===== BIBLIOTECA DIGITAL COMUNITÁRIA =====
1  - Cadastrar usuário
2  - Cadastrar material
3  - Realizar empréstimo
4  - Realizar devolução
5  - Reservar material
6  - Avaliar material
7  - Consultar materiais
8  - Consultar usuários
9  - Relatório de empréstimos
10 - Recomendações
0  - Sair"""

ACOES = {
    1: cadastrar_usuario,
    2: cadastrar_material,
    3: realizar_emprestimo,
    4: realizar_devolucao,
    5: reservar_material,
    6: avaliar_material,
    7: consultar_materiais,
    8: consultar_usuarios,
    9: relatorio_emprestimos,
    10: recomendacoes,
}


def main():
    carregar_tudo()
    while True:
        print(MENU)
        try:
            opcao = ler_inteiro("Escolha uma opção: ", 0, 10)
        except EOFError:
            break
        if opcao == 0:
            salvar_tudo()
            print("Dados salvos. Até logo!")
            break
        try:
            ACOES[opcao]()
        except BibliotecaError as erro:
            print(f"Erro: {erro}")


if __name__ == "__main__":
    main()
