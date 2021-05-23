__author__ = Rafael Oliveira, 52848; Ariana Dias, 53687


import csv, functools, math, sys, re
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


def classes(dados, opcoes):
    """Chama as funções certas para o comando 'classes' consoante as opções

    Args:
        dados (list[dict]): lista com um dicionário para cada jogo contendo a sua informação
        opcoes (list): lista com todas as opções indicadas após o comando
    """

    if opcoes == []:
        classes_tratamento(dados)
    elif opcoes[0] == '-c' and (opcoes[1]).isdigit():
        classes_tratamento(dados, int(opcoes[1]))
    else:
        print("Erro: Insira opções válidas.")
        sys.exit(1)

        
def classes_tratamento(dados, bars = 5):
    """Faz o tratamento dos dados, preparando-os para serem plotados

    Args:
        dados (list[dict]): lista com um dicionário para cada jogo contendo a sua informação
        bars (int): nr de barras a aparecer no grafico de barras

    """

    dict_dados_c = limpa_converte(dados, ['time_control', 'time_class'],lambda cell: cell != None  ,[str,str])
    formatos = { 'blitz':[], 'bullet':[], 'daily':[] ,'rapid':[]}
    for dic in dict_dados_c:
        for form in formatos:
            if dic['time_class']==form:
                formatos[form].append(dic['time_control'])
    dict_classes = {form:sorted([(item, formatos[form].count(item)) for item in list(set(formatos[form]))], key=lambda x: x[1])[-bars:]
                    for form in list(formatos.keys())}
    Geral = [(item,len(formatos[item])) for item in list(formatos.keys())]
    tracar_classes(dict_classes,Geral)

    
def tracar_classes(L,Geral):
    """Traça a imagem com os subplots

    Args:
        L (dict): dicionário com tuplos (formato_jogo, #jogos) para as modalidades do xadrez
        Geral(list[tuples]): lista de tuplos(modalidade_jogo, #jogos_total)

    """

    ax1 = plt.subplot2grid((5,10), (0,0), colspan=2)
    list1, list2 = zip(*L['rapid'])
    ax1.bar(list1[::-1],list2[::-1])
    ax1.set_title('rapid')
    ax1.set(xlabel='Formato de Jogo', ylabel='#jogos')
    plt.xticks(range(len(list1)), list1, rotation='vertical')
    ax2 = plt.subplot2grid((5,10), (0,4), colspan=2)
    list1, list2 = zip(*L['daily'])
    ax2.set_title('daily')
    ax2.set(xlabel='Formato de Jogo', ylabel='#jogos')
    ax2.bar(list1[::-1],list2[::-1])
    plt.xticks(range(len(list1)), list1, rotation='vertical')
    ax3 = plt.subplot2grid((5,10), (0,8), colspan=2)
    list1, list2 = zip(*L['bullet'])
    ax3.set_title('bullet')
    ax3.bar(list1[::-1],list2[::-1])
    ax3.set(xlabel='Formato de Jogo', ylabel='#jogos')
    plt.xticks(range(len(list1)), list1, rotation='vertical')
    ax4 = plt.subplot2grid((5,10), (3,0), colspan=2)
    list1, list2 = zip(*L['blitz'])
    ax4.set_title('blitz')
    ax4.bar(list1[::-1],list2[::-1])
    ax4.set(xlabel='Formato de Jogo', ylabel='#jogos')
    plt.xticks(range(len(list1)), list1, rotation='vertical')
    ax5 = plt.subplot2grid((5,10), (3,4), colspan=2)
    list1, list2 = zip(*Geral)
    ax5.set_title('time_class')
    ax5.set(xlabel='Formato de Jogo', ylabel='#jogos')
    plt.xticks(range(len(list1)), list1, rotation='vertical')
    ax5.bar(list1,list2)
    plt.show()

    
def seguinte(dados,opcoes):
    """Chama as funções certas para o comando 'classes' consoante as opções

    Args:
        dados: lista com um dicionário para cada jogo contendo a sua informação
        opcoes: lista com todas as opções indicadas após o comando
    """

    firstplay = 'e4'
    top = 5

    if opcoes == []:
        seguinte_tratamento(dados)
    elif '-j' in opcoes or '-c' in opcoes :
        if '-o' in opcoes:
            firstplay = opcoes[(opcoes.index('-j') + 1)]
        if '-r' in opcoes:
            top = int(opcoes[(opcoes.index('-c') + 1)])
        seguinte_tratamento(dados, firstplay, top)
    else:
        print("Erro: Insira opções válidas.")
        sys.exit(1)


def seguinte_tratamento(dados, firstplay = 'e4', top = 5):
    """Faz o tratamento dos dados, preparando-os para depois serem plotados

    Args:
        dados: lista com um dicionário para cada jogo contendo a sua informação
        top: # de top jogadas a apresentar
        firstplay: jogada de abertura
    """

    dados_convertidos = limpa_converte(dados, ['pgn'], lambda cell: cell['pgn'] != '' , [str])
    L = [[dic['pgn']] for dic in dados_convertidos]
    newL = list(map(lambda x: [x[0].replace('{', '').replace('}', '')], L))
    newLL = list(map(lambda x: [re.sub("[\(\[].*?[\)\]]", "", x[0] )], newL))
    newLLL = list(map(lambda x: x[0].split(), newLL))
    flt = list(filter(lambda x: x[0] == '1.', newLLL))
    final = list(map(lambda a: a[1::2], flt))
    filtrada = (list(filter(lambda x: x[0] == firstplay and len(x)> top, final)))
    tracar_seguinte(filtrada, top,firstplay)

    
def tracar_seguinte(filtrada,top,firstplay):
    """Calcula as probabilidades e traca o respetivo gráfico de barras

    Args:
        filtrada: matriz com os dados filtrados prontos para serem usados nos calculos de probabilidades
        top: # de top jogadas a apresentar
        firstplay: jogada de abertura
    """
    seguinte = []
    for item in filtrada:
        seguinte.append(item[1])
    aux = list(set(seguinte))
    probabilidades = [(item,(seguinte.count(item)/len(seguinte)) )for item in aux]
    probabilidades.sort(key=lambda x:x[1])


    list1, list2 = zip(*probabilidades[-top:])
    plt.bar(list1[::-1], list2[::-1])
    plt.title('jogadas mais provaveis depois de {}'.format(firstplay))
    plt.xlabel('jogadas')
    plt.ylabel('probabilidade')
    plt.show()
    
    
def extrair(dados, opcoes):
    """Chama as funções certas para o comando 'classes' consoante as opções

    Args:
        dados: lista com um dicionário para cada jogo contendo a sua informação
        opcoes: lista com todas as opções indicadas após o comando
    """
    nome_ficheiro = 'out.csv'
    linhas_de_interesse = '.*'
    coluna_testada = 'wgm_username'

    if opcoes == []:
        extrair_tratamento(dados)
    elif '-o' in opcoes or '-r' in opcoes or '-d' in opcoes:
        if '-o' in opcoes:
            nome_ficheiro = opcoes[(opcoes.index('-o') + 1)]
        if '-r' in opcoes:
            linhas_de_interesse = opcoes[(opcoes.index('-r') + 1)]
        if '-d' in opcoes:
            coluna_testada = opcoes[(opcoes.index('-d'))]
        extrair_tratamento(dados, nome_ficheiro, linhas_de_interesse, coluna_testada)
    else:
        print("Erro: Insira opções válidas.")
        sys.exit(1)


def extrair_tratamento(dados, nome_ficheiro, pattern, coluna_testada):
    """Extrai informacao do ficheiro original para um outro ficheiro csv

    Args:
        dados: lista com um dicionário para cada jogo contendo a sua informação
        nome_ficheiro: nome do ficheiro final
        pattern: expressao regular que identifica as linhas de interesse
        coluna_testada: nome da coluna onde a expressão regular é testada
    """
    
    header = list(dados[0].keys())
    dados_2 = limpa_converte(dados, header, lambda x: x[coluna_testada], [str] * len(header))
    rows = []
    for dic in dados_2:
        if re.match(pattern, dic[coluna_testada]):
            rows.append(dic)

    with open(nome_ficheiro, 'w', newline='') as f:
        write = csv.DictWriter(f, fieldnames = header)
        write.writeheader()
        for data in rows:
            write.writerow(data)    
       
    
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
elif comando == "classes":
    classes(dados,opcoes)
elif comando == "seguinte":
    seguinte(dados, opcoes)
elif comando == "extrair":
    extrair(dados, opcoes)
else:
    print("Erro: Insira um comando válido.")
    sys.exit(1)
