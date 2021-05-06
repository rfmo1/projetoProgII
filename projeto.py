import csv, functools, math, sys
import matplotlib.pyplot as plt

def ler_csv_dicionario_cabecalho (nome_ficheiro, deli = None):
    """Ler um ficheiro CSV com cabeçalho.

    Args:
        nome_ficheiro (str): O nome do ficheiro
        deli (bool): Verdadeiro se o delimitador do ficheiro for ;

    Returns:
        list[dict]: Uma lista de dicionarios com o conteúdo do ficheiro;
            as chaves do dicionário são lidas da primeira linha do ficheiro.
    """
    with open(nome_ficheiro) as ficheiro_csv:
        delimit = deli if deli else ","
        leitor = csv.DictReader(ficheiro_csv, delimiter = delimit)
        return list(leitor)


def limpa_converte(dados, lista_colunas, pred_filtragem, funs_converter):
    '''Limpar e converter uma lista de dicionários

    Args:
        dados (list[dict]): Dados a serem convertidos
        lista_colunas (list[str]): Lista de colunas a manter
        pred_filtragem (funct): Predicado para a filtragem de elementos da lista
        funs_converter (list[funct]): Lista de funções usadas para converter os dados

    Returns:
        list[dict]: Conjunto final de dados convertidos usando o predicado de filtragem e as funs_converter

    Pre:
        len(funs_converter) == len(lista_colunas)
    '''
    fltr = list(filter(pred_filtragem, dados))
    for d in fltr:
        for coluna in list(d.keys()):
            if coluna not in lista_colunas:
                del d[coluna]
    convert = map(lambda d: dict(map(lambda item: (item[0], funs_converter[lista_colunas.index(item[0])](item[1])), d.items())), fltr)

    return list(convert)

def converte_tempo(tempo):
    li = tempo.split(" ")
    data = li[0].split("-")
    horas = li[1].split(":")
    return {"segundos": horas[2], "minutos": horas[1], "horas": horas[0],
        "dia": data[2], "mes": data[1], "ano": data[0]}


def users_totais(lista_ano):
    users = []
    for jogo in lista_ano:
        if jogo["black_username"] not in users:
            users.append(jogo["black_username"])
        if jogo["white_username"] not in users:
            users.append(jogo["white_username"])
    return users


def tracar_anos(abcissas, jogos, jogadoras):
    fig, ax1 = plt.subplots()
    ax1.plot(abcissas, jogadoras, color="blue")
    ax1.set_ylabel("#Jogadoras diferentes")
    ax1.set_xlabel("Ano")
    ax2 = ax1.twinx()
    ax2.bar(abcissas, jogos, color="green")
    ax1.set_ylabel("#Jogos")
    fig.tight_layout()
    plt.title("Jogos e jogadoras por ano")
    plt.show()


def anos(dados):
    dados_c = limpa_converte(dados, ["end_time", "black_username", "white_username"], lambda jogo: True, [lambda tempo: int(converte_tempo(tempo)["ano"]), str, str])
    conjunto_anos = list(map(lambda jogo: jogo["end_time"], dados_c))
    abcissas = range(min(conjunto_anos), max(conjunto_anos) + 1)
    filtrar_ano = lambda ano: list(filter(lambda jogo: jogo["end_time"] == ano,dados_c))
    jogos = list(map(lambda ano: len(list(filtrar_ano(ano))), abcissas))
    jogadoras = list(map(lambda ano: len(users_totais(filtrar_ano(ano))), abcissas))
    tracar_anos(abcissas, jogos, jogadoras)






ficheiro = sys.argv[1]
comando = sys.argv[2]
opcoes = sys.argv[3:]

dados = ler_csv_dicionario_cabecalho(ficheiro)

if comando == "anos":
    anos(dados)
'''elif comando == "classes":
    classes(dados)
elif comando == "vitorias":
    vitorias(dados)
elif comando == "seguinte":
    seguinte(dados)
elif comando == "mate":
    mate(dados)
elif comando == "extrair":
    extrair(dados)
else:
    print("Erro: Insira um comando válido.")
    sys.exit(1)'''
