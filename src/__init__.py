def calcular_idade(df, nasc, idade = 'idade'):
    """
    Função para calcular a idade a partir de uma coluna de nascimento.
    Exemplo:
    calcular_idade(df, 'data_nascimento', 'idade')
    """
    import pandas as pd
    import numpy as np
    from datetime import date 
    def calculateAge(birthDate): 
        today = date.today() 
        age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day))
        return age
    if np.issubdtype(df[nasc], np.datetime64):
        df[idade] = df.apply(lambda x: calculateAge(x[nasc]),axis=1)
    else:
        df[idade] = df.apply(lambda x: calculateAge(pd.to_datetime(x[nasc])),axis=1)
    df[idade] = df[idade].astype('Int32')
    return None
    

def para_data(df, coluna, **kwargs):
    """
    Função para transformar coluna em data.
    Por padrão ignora hora, minutos e segundos.
    
    Argumentos:
    --------------------------------------------
    horario: True para manter horário ou False (default)
    fuso:    Transformar fuso horário no de São Paulo (implica horário True)
    
    Exemplo:
    df['data']
    2020-02-06T18:32:15.645Z
    dtype: object
    
    para_data(df,'data')
    
    df['data']
    2020-02-06
    dtype: datetime64[ns]
    """
    import pandas as pd
    horario = kwargs.get('horario', False)
    fuso = kwargs.get('fuso', False)
    if fuso == True:
        horario = True
    if horario == False:
        try:
            df[coluna] = pd.to_datetime(df[coluna].astype('str').str[:10])
            return None
        except:
            horario = True
    if horario == True:
        if fuso == True:
            df[coluna] = pd.to_datetime(df[coluna]).dt.tz_convert('America/Sao_Paulo').dt.tz_localize(None)
        else:
            df[coluna] = pd.to_datetime(df[coluna])
        return None
        
def manter_num(df, coluna):
    """
    Função para manter apenas os números de uma coluna.
    Exemplo:
    df['CPF']
    |  111.222.333-44   |
    | cpf = 99988877766 |
    |  555-444-333/11   |
    
    manter_num(df,'CPF')
    
    df['CPF']
    | 11122233344 |
    | 99988877766 |
    | 55544433311 |
    """
    import pandas as pd
    df[coluna] = df[coluna].astype('str').str.replace('[^0-9]', '', regex = True)
    return None

def exportar_excel(df, local = None):
    """
    Função para exportar o excel já formatado.
    Pode ser passado o csv caso queira realizar uma conversao rapida.
    Se omitido o local de exportacao, ele ira usar o mesmo de entrada.
    (Ele apenas faz um auto-ajuste da largura das colunas)
    Exemplo:
    1 - exportar_excel(df, 'Dados/df.xslx')
    2 - exportar_excel('Dados/df.csv', 'Dados/df.xlsx')
    3 - exportar_excel('Dados/df.csv')
    """
    #local = kwargs.get(local, None)
    import pandas as pd 
    if local == None:
        try:
            local = df.split('.')[0] + '.xlsx'
        except:
            print('Cuidado: Omitido local [ exportar_excel(df, "Dados/df.xlsx") ].\n')
            from datetime import datetime
            local = (datetime.today().strftime('%Y%m%d_%H%M%S') + '.xlsx')
    elif '.' not in local:
        print('Cuidado: Omitido extensao do arquivo xlsx.\n Adicionado .xslx automaticamente.\n')
        local += '.xlsx'
    if type(df) is str:
        df = pd.read_csv(df)
    writer = pd.ExcelWriter(local, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet', index = False)  # send df to writer
    worksheet = writer.sheets['Sheet']  # pull worksheet object
    for idx, col in enumerate(df):  # loop through all columns
        series = df[col]
        max_len = max((
            series.astype(str).map(len).max(),  # len of largest item
            len(str(series.name))  # len of column name/header
            )) + 3  # adding a little extra space
        worksheet.set_column(idx, idx, max_len)  # set column width
    writer.save()
    print('Gerado: ' + local)
    
def to_sftp_csv(DataFrame, Destino, sftp, compactar = True):
    """
	Funcao para exportar CSV no SFTP.
    Por padrão irá compactar o arquivo.
    
    Argumentos:
    --------------------------------------------
    compactar: True compactar com padrao bzip2 (default)
	
	Exemplo:
		to_sftp_csv(df, 'pasta_rede/out/arquivo.csv', sftp, Compactar = False)
	
    PS: Eh possivel passar um dicionario no DataFrame para exportar varios arquivos dentro do mesmo .ZIP
        Formato {'nome arquivo1' : DataFrame1,
                 'nome arquivo2' : DataFrame2}
	IMPORTANTE: Necessario estar com conexao aberta ao sftp
		Exemplo:
			from connectsftp import sftp
			sftp = sftp()
			
			to_sftp_csv([...])
    """
    import pandas as pd
    if type(DataFrame) == type(pd.DataFrame()):
        # Renomeando colunas para views que tenham o nome da tabela
        if DataFrame.columns.str.contains('\.').sum() >= 1:
            DataFrame.columns = DataFrame.columns.str.split('.').str[1]

        if compactar == False:
            # Escrita de arquivo
            with sftp.open(Destino.rsplit('.',1)[0] + '.csv', "w") as f:
                f.write(DataFrame.to_csv(index=False))
            # Printando arquivo gerado
            print('Gerado com sucesso: ' + Destino.rsplit('.',1)[0] + '.csv')
        else:
            # Iportando Buffer
            import io
            # Importando compactador
            from zipfile import ZipFile, ZIP_BZIP2
            # Criando buffer
            zip_buffer = io.BytesIO()
            # Gerando arquivo zipado em buffer
            with ZipFile(zip_buffer, 'a', ZIP_BZIP2) as zip: 
                # Zipando
                zip.writestr(Destino.rsplit('/',1)[1].rsplit('.',1)[0] + '.csv', DataFrame.to_csv(index = False))

            # Gerando arquivo
            with sftp.open(Destino.rsplit('.',1)[0] + '.zip', "wb") as f:
                f.write(zip_buffer.getvalue())
            print('Gerado com sucesso: ' + Destino.rsplit('.',1)[0] + '.zip')
    elif type(DataFrame) == dict:
        # Iportando Buffer
        import io
        # Importando compactador
        from zipfile import ZipFile, ZIP_BZIP2
        # Criando buffer
        zip_buffer = io.BytesIO()
        # Gerando arquivo zipado em buffer
        with ZipFile(zip_buffer, 'a', ZIP_BZIP2) as zip: 
            # Iterando em cima das bases para criar um zip soh
            for arq, df in DataFrame.items():
                # Renomeando colunas para views que tenham o nome da tabela
                if df.columns.str.contains('\.').sum() >= 1:
                    df.columns = df.columns.str.split('.').str[1]
                # Zipando
                zip.writestr(arq + '.csv', df.to_csv(index = False))
                print('Zipado '+ arq + '.csv;')
        
        # Gerando arquivo
        with sftp.open(Destino.rsplit('.',1)[0] + '.zip', "wb") as f:
            f.write(zip_buffer.getvalue())
        print('Gerado com sucesso: ' + Destino.rsplit('.',1)[0] + '.zip')
    else:
        print('Entrada de DataFrame invalida')
		
def to_sftp_excel(DataFrame, Destino, sftp):
    import pandas as pd 
    # Iportando Buffer
    import io
    # Criando buffer
    excel = io.BytesIO()
    """
    Função para exportar para um sftp o excel já formatado.
    (Ele apenas faz um auto-ajuste da largura das colunas)
    Exemplo:
        to_sftp_excel(df, 'Dados/df.xslx')
    """
    writer = pd.ExcelWriter(excel, engine='xlsxwriter')
    DataFrame.to_excel(writer, sheet_name='Planilha', index = False)
    worksheet = writer.sheets['Planilha']
    for idx, col in enumerate(DataFrame):
        series = DataFrame[col]
        max_len = max((
            series.astype(str).map(len).max(),  # len of largest item
            len(str(series.name))  # len of column name/header
            )) + 5  # adding a little extra space
        worksheet.set_column(idx, idx, max_len)  # set column width
    writer.save()
    # Gerando arquivo
    with sftp.open(Destino.rsplit('.',1)[0] + '.xlsx', "wb") as f:
        f.write(excel.getvalue())
    print('Gerado com sucesso: ' + Destino.rsplit('.',1)[0] + '.xlsx')
    
def zipar_bases(Bases, Destino):
    """
    Função para exportar o excel já formatado e csv puro.
    Deve ser passado dicionário das bases
    (Ele apenas faz um auto-ajuste da largura das colunas)
    Exemplo:
        bases = {'base.csv'  : df,
                 'base.xlsx' : df}
        zipar_bases(bases, 'Dados/bases.zip')
    """
    # Checagem básica
    if type(Bases) != dict:
        return(print('A entrada de bases precisa ser um dicionário. Exemplo: {df : "df.csv"}'))
    # Importando pandas
    import pandas as pd 
    # Iportando Buffer
    import io
    # Importando compactador
    from zipfile import ZIP_DEFLATED, ZipFile
    # Criando buffer
    zip_buffer = io.BytesIO()
    # Gerando arquivo zipado em buffer
    with ZipFile(zip_buffer, 'a', ZIP_DEFLATED) as zip: 
        # Iterando em cima das bases para criar um zip soh
        for arq, df in Bases.items():
            if 'xlsx' in arq:
                excel = io.BytesIO()
                writer = pd.ExcelWriter(excel, engine='xlsxwriter')
                df.to_excel(writer, sheet_name='Planilha', index = False)
                worksheet = writer.sheets['Planilha']
                for idx, col in enumerate(df):
                    series = df[col]
                    max_len = max((
                        series.astype(str).map(len).max(),  # len of largest item
                        len(str(series.name))  # len of column name/header
                        )) + 5  # adding a little extra space
                    worksheet.set_column(idx, idx, max_len)  # set column width
                writer.save()
                # Zipando
                zip.writestr(arq, excel.getvalue())
                print('Zipado '+ arq)
            else:
                # Zipando
                zip.writestr(arq, df.to_csv(index = False))
                print('Zipado '+ arq)
    with open(Destino, 'wb') as f:
        f.write(zip_buffer.getvalue())
    print('Gerado: ' + Destino)