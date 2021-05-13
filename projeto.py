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
    """Converte uma string com o tempo no formato "Ano-Mês-Dia Horas:Minutos:Segundos" num dicionário
    com essa informação

    Args:
        tempo (str): string onde se encontra a data e hora

    Returns:
        dict: Dicionário com o tempo

    Pre:
        A string tempo seja no formato indicado a cima
    """

    li = tempo.split(" ")
    data = li[0].split("-")
    horas = li[1].split(":")
    return {"segundos": horas[2], "minutos": horas[1], "horas": horas[0],
        "dia": data[2], "mes": data[1], "ano": data[0]}

def get_jogos_user(dados):
    """Obtem um dicionário com o número de jogos que casa utilizador jogou

    Args:
        dados (list[dict]): lista com os dicionários da informação de cada jogo

    Returns:
        dict: dicionário em que as chaves são os nomes dos jogadores e os valores
    o número de jogos jogado
    """

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
    """Traça o gráfico necessário para o comando 'anos'

    Args:
        abcissas (list): lista de anos
        jogos (list): lista de totais jogos jogados em cada ano
        jogadoras (list): lista dos números de jogadoras diferentes que jogaram
    em cada ano

    Pre:
        len(abcissas) == len(jogos) == len(jogadoras)
    """

    fig, ax1 = plt.subplots()
    ax1.plot(abcissas, jogadoras, color="blue")
    ax1.set_ylabel("#Jogadoras diferentes")
    ax1.set_xlabel("Ano")
    ax2 = ax1.twinx()
    ax2.bar(abcissas, jogos, color="green")
    ax2.set_ylabel("#Jogos")
    fig.tight_layout()
    plt.title("Jogos e jogadoras por ano")
    plt.show()

def anos(dados):
    """Trata do comando anos

    Args:
        dados (list[dict]): lista com um dicionário para cada jogo contendo a sua informação
    """

    dados_c = limpa_converte(dados, ["end_time", "black_username", "white_username"], lambda jogo: True, [lambda tempo: int(converte_tempo(tempo)["ano"]), str, str])
    conjunto_anos = list(map(lambda jogo: jogo["end_time"], dados_c))
    abcissas = range(min(conjunto_anos), max(conjunto_anos) + 1)
    filtrar_ano = lambda ano: list(filter(lambda jogo: jogo["end_time"] == ano,dados_c))
    jogos = list(map(lambda ano: len(list(filtrar_ano(ano))), abcissas))
    jogadoras = list(map(lambda ano: len(list(get_jogos_user(filtrar_ano(ano)).keys())), abcissas))
    tracar_anos(abcissas, jogos, jogadoras)

def tracar_vitorias(abcissas, white_wins, black_wins, width):
    """Traça o gráfico necessário para o comando 'vitorias'

    Args:
        abcissas (list): lista de utilizadores
        white_wins (list): lista das percentagens de vitorias jogando com as
    brancas de cada jogador
        black_wins (list): lista das percentagens de vitorias jogando com as
    pretas de cada jogador
        width (float): largura das barras

    Pre:
        len(abcissas) == len(white_wins) == len(black_wins)
    """

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
    """Trata do caso em que o comando 'vitorias' é chamado com a opção -u

    Args:
        dados (list[dict]): lista com um dicionário para cada jogo contendo a sua informação
        users (list): lista com os nomes dos utilizadores que aparecerão no gráfico
    """

    is_win = lambda result: result == "win"
    users_c = list(map(lambda user: user.lower(), users))
    dados_c = limpa_converte(dados, ["black_username", "black_result", "white_username", "white_result"], lambda jogo: jogo["white_username"].lower() in users_c or jogo["black_username"].lower() in users_c, [str, is_win, str, is_win])
    white_wins = list(map(lambda user: len(list(filter(lambda jogo: jogo["white_username"].lower() == user and jogo["white_result"], dados_c)))/len(list(filter(lambda jogo: jogo["white_username"].lower() == user, dados_c))), users_c))
    black_wins = list(map(lambda user: len(list(filter(lambda jogo: jogo["black_username"].lower() == user and jogo["black_result"], dados_c)))/len(list(filter(lambda jogo: jogo["black_username"].lower() == user, dados_c))), users_c))
    tracar_vitorias(users, white_wins, black_wins, 0.3)

def vitorias_C(dados, count=5):
    """Trata do caso em que o comando 'vitorias' é chamado com a opção -c ou sem opção.
    Escolhe os utilizadores que jogaram um maior número de jogos.

    Args:
        dados (list[dict]): lista com um dicionário para cada jogo contendo a sua informação
        count (int): número total de utilizadores a incluir no gráfico
    """

    is_win = lambda result: result == "win"
    dados_c = limpa_converte(dados, ["black_username", "black_result", "white_username", "white_result"], lambda jogo: True, [str, is_win, str, is_win])
    jogos = get_jogos_user(dados_c)
    abcissas = list(reversed(sorted(jogos, key = jogos.get)))[:count]
    white_wins = list(map(lambda user: len(list(filter(lambda jogo: jogo["white_username"].lower() == user and jogo["white_result"], dados_c)))/len(list(filter(lambda jogo: jogo["white_username"].lower() == user, dados_c))), abcissas))
    black_wins = list(map(lambda user: len(list(filter(lambda jogo: jogo["black_username"].lower() == user and jogo["black_result"], dados_c)))/len(list(filter(lambda jogo: jogo["black_username"].lower() == user, dados_c))), abcissas))
    tracar_vitorias(abcissas, white_wins, black_wins, 0.3)

def vitorias(dados, opcoes):
    """Chama as funções certas para o comando 'vitorias' consoante as opções

    Args:
        dados (list[dict]): lista com um dicionário para cada jogo contendo a sua informação
        opcoes (list): lista com todas as opções indicadas após o comando
    """
    if opcoes == []:
        vitorias_C(dados)
    elif opcoes[0] == "-c":
        vitorias_C(dados, int(opcoes[1]))
    elif opcoes[0] == "-u":
        vitorias_U(dados, opcoes[1:])
    else:
        print("Erro: Insira opções válidas.")
        sys.exit(1)


def tracar_eixos_mate(abcissas, jogos_ganhos, jogos_ganhos_mate, percentagens, width, X1, X2, ax1):
    """Trata dos dois eixos para o gráfico do comando mate

    Args:
        abcissas (list): lista de utilizadores
        jogos_ganhos (list): lista de número de jogos ganhos por utilizador
        jogos_ganhos_mate (list): lista de número de jogos ganhos por xeque-mate por utilizador
        percentagens (list): lista percentagens de jogos ganhos por xeque-mate por utilizador
        width (float): largura das barras
        X1 (list): lista das abcissas das primeiras barras
        X2 (list): lista das abcissas das segundas barras

    Pre:
        len(abcissas) == len(percentagens) == len(jogos_ganhos) == len(jogos_ganhos_mate)
    """

    ax1.bar(X1, jogos_ganhos, width, color="blue", label="jogos ganhos")
    ax1.bar(X2, jogos_ganhos_mate, width,  color="grey", label="jogos ganhos por xeque-mate")
    ax1.set_xticks(X1)
    ax1.set_xticklabels(abcissas)
    ax1.set_ylabel("#Jogos")
    ax1.legend(loc="lower left")
    ax2 = ax1.twinx()
    ax2.plot(X1, percentagens, color="red", label="percentagem de xeque-mate")
    ax2.set_ylabel("Percentagem de xeque-mates", color="red")
    ax2.legend(loc="upper right")

def tracar_mate(abcissas, jogos_ganhos, jogos_ganhos_mate, percentagens, width, X1, X2):
    """Traça o gráfico necessário para o comando 'mate'

    Args:
        abcissas (list): lista de utilizadores
        jogos_ganhos (list): lista de número de jogos ganhos por utilizador
        jogos_ganhos_mate (list): lista de número de jogos ganhos por xeque-mate por utilizador
        percentagens (list): lista percentagens de jogos ganhos por xeque-mate por utilizador
        width (float): largura das barras
        X1 (list): lista das abcissas das primeiras barras
        X2 (list): lista das abcissas das segundas barras

    Pre:
        len(abcissas) == len(percentagens) == len(jogos_ganhos) == len(jogos_ganhos_mate)
    """

    fig, ax1 = plt.subplots()
    tracar_eixos_mate(abcissas, jogos_ganhos, jogos_ganhos_mate, percentagens, width, X1, X2, ax1)
    plt.title("Percentagem de xeque-mates, jogos ganhos e jogos ganhos por xeque-mate")
    plt.show()


def mate(dados, opcoes):
    """Trata do comando mate

    Args:
        dados (list[dict]): lista com um dicionário para cada jogo contendo a sua informação
        opcoes (list): lista com todas as opções indicadas após o comando
    """

    is_mate = lambda result: (result == "win", result == "checkmated")
    dados_c = limpa_converte(dados, ["black_username", "black_result", "white_username", "white_result"], lambda jogo: True, [str, is_mate, str, is_mate])
    count = 5 if opcoes == [] else int(opcoes[1])
    jogos = get_jogos_user(dados_c)
    abcissas = list(reversed(sorted(jogos, key = jogos.get)))[:count]
    jogos_ganhos = list(map(lambda user: len(list(filter(lambda jogo: (jogo["white_username"].lower() == user and jogo["white_result"][0]) or (jogo["black_username"].lower() == user and jogo["black_result"][0]) , dados_c))), abcissas))
    jogos_ganhos_mate = list(map(lambda user: len(list(filter(lambda jogo: (jogo["white_username"].lower() == user and jogo["black_result"][1]) or (jogo["black_username"].lower() == user and jogo["white_result"][1]) , dados_c))), abcissas))
    percentagens = list(map(lambda index: jogos_ganhos_mate[index]/jogos_ganhos[index],range(len(abcissas))))
    tracar_mate(abcissas, jogos_ganhos, jogos_ganhos_mate, percentagens, 0.3, range(len(abcissas)), list(map(lambda x: x+0.3, range(len(abcissas)))))



#Argumentos
ficheiro = sys.argv[1]
comando = sys.argv[2]
opcoes = sys.argv[3:]

#Obter dicionário a partir do csv
dados = ler_csv_dicionario_cabecalho(ficheiro)

#Escolher o comando
if comando == "anos":
    anos(dados)
elif comando == "vitorias":
    vitorias(dados, opcoes)
elif comando == "mate":
    mate(dados, opcoes)
'''elif comando == "classes":
    classes(dados)
elif comando == "seguinte":
    seguinte(dados)

elif comando == "extrair":
    extrair(dados)
else:
    print("Erro: Insira um comando válido.")
    sys.exit(1)'''
