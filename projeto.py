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

def get_jogos_user(dados):
    info = {}
    for dado in dados:
        if dado["black_username"].lower() in info.keys():
            info[dado["black_username"].lower()] += 1
        else:
            info[dado["black_username"].lower()] = 1
        if dado["white_username"].lower() in info.keys():
            info[dado["white_username"].lower()] += 1
        else:
            info[dado["white_username"].lower()] = 1
    return info

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
    jogadoras = list(map(lambda ano: len(list(get_jogos_user(filtrar_ano(ano)).keys())), abcissas))
    tracar_anos(abcissas, jogos, jogadoras)

def tracar_vitorias(abcissas, white_wins, black_wins, width):
    fig, ax1 = plt.subplots()
    X1 = range(len(abcissas))
    X2 = list(map(lambda x: x+width, X1))
    ax1.bar(X1, white_wins, width, color="grey")
    ax1.set_ylabel("Percentagem de vitórias")
    ax1.bar(X2, black_wins, width,  color="black")
    ax1.set_xticks(X1)
    ax1.set_xticklabels(abcissas)
    plt.title("Percentagem de vitórias jogando com peças brancas / pretas")
    plt.show()

def vitorias_U(dados, users):
    is_win = lambda result: result == "win"
    users_c = list(map(lambda user: user.lower(), users))
    dados_c = limpa_converte(dados, ["black_username", "black_result", "white_username", "white_result"], lambda jogo: jogo["white_username"].lower() in users_c or jogo["black_username"].lower() in users_c, [str, is_win, str, is_win])
    white_wins = list(map(lambda user: len(list(filter(lambda jogo: jogo["white_username"].lower() == user and jogo["white_result"], dados_c)))/len(list(filter(lambda jogo: jogo["white_username"].lower() == user, dados_c))), users_c))
    black_wins = list(map(lambda user: len(list(filter(lambda jogo: jogo["black_username"].lower() == user and jogo["black_result"], dados_c)))/len(list(filter(lambda jogo: jogo["black_username"].lower() == user, dados_c))), users_c))
    tracar_vitorias(users, white_wins, black_wins, 0.3)

def vitorias_C(dados, count=5):
    is_win = lambda result: result == "win"
    dados_c = limpa_converte(dados, ["black_username", "black_result", "white_username", "white_result"], lambda jogo: True, [str, is_win, str, is_win])
    jogos = get_jogos_user(dados_c)
    abcissas = list(reversed(sorted(jogos, key = jogos.get)))[:count]
    white_wins = list(map(lambda user: len(list(filter(lambda jogo: jogo["white_username"].lower() == user and jogo["white_result"], dados_c)))/len(list(filter(lambda jogo: jogo["white_username"].lower() == user, dados_c))), abcissas))
    black_wins = list(map(lambda user: len(list(filter(lambda jogo: jogo["black_username"].lower() == user and jogo["black_result"], dados_c)))/len(list(filter(lambda jogo: jogo["black_username"].lower() == user, dados_c))), abcissas))
    tracar_vitorias(abcissas, white_wins, black_wins, 0.3)

def vitorias(dados, opcoes):
    if opcoes == []:
        vitorias_C(dados)
    elif opcoes[0] == "-c":
        vitorias_C(dados, int(opcoes[1]))
    elif opcoes[0] == "-u":
        vitorias_U(dados, opcoes[1:])
    else:
        print("Erro: Insira opções válidas.")
        sys.exit(1)







ficheiro = sys.argv[1]
comando = sys.argv[2]
opcoes = sys.argv[3:]

dados = ler_csv_dicionario_cabecalho(ficheiro)

if comando == "anos":
    anos(dados)
elif comando == "vitorias":
    vitorias(dados, opcoes)
'''elif comando == "classes":
    classes(dados)
elif comando == "seguinte":
    seguinte(dados)
elif comando == "mate":
    mate(dados)
elif comando == "extrair":
    extrair(dados)
else:
    print("Erro: Insira um comando válido.")
    sys.exit(1)'''
