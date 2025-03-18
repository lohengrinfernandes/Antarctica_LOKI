# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 18:48:10 2024

@author: Zbook
"""

import os
import csv

# Define o diretório base, incluindo "LOKI"
base_directory = r"D:\Projects\Antartica_Ecopelagos\Operantar_XLI_Dados\LOKI_para_fazer"
csv_path = os.path.join(base_directory, "..", "OPERANTAR_XLI.csv")  # Caminho ajustado para acessar o arquivo CSV na pasta pai

# Ler o arquivo CSV para extrair latitude, longitude e profundidade (das colunas 5, 6 e 3)
lat_lon_depth_data = {}
with open(csv_path, 'r') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Pular cabeçalho
    for row in reader:
        directory = row[0]
        lat = row[4]  # Extrair da 5ª coluna
        lon = row[5]  # Extrair da 6ª coluna
        bottom_depth = row[2]  # Extrair da 3ª coluna
        lat_lon_depth_data[directory] = (lat, lon, bottom_depth)

# Função para calcular a média da 20ª coluna dos cinco primeiros arquivos .dat
def calculate_average_depth(telemetrie_directory):
    depths = []
    
    try:
        files = [f for f in os.listdir(telemetrie_directory) if f.endswith('.dat')]
        files.sort()  # Ordenar para garantir a consistência na seleção dos arquivos
        
        # Processar apenas os cinco primeiros arquivos .dat
        for dat_file in files[:5]:
            dat_file_path = os.path.join(telemetrie_directory, dat_file)
            with open(dat_file_path, 'r') as datfile:
                lines = datfile.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    columns = last_line.split('\t')
                    if len(columns) >= 20:
                        depths.append(float(columns[19]))  # Armazenar o valor da 20ª coluna
        
        # Calcular a média
        if depths:
            return sum(depths) / len(depths)
        else:
            return None
    except Exception as e:
        print(f"Erro ao calcular a média dos arquivos .dat: {e}")
        return None

# Função para recuperar dados do arquivo .dat
def get_data_from_dat_file(dat_file_path, average_depth):
    if not os.path.isfile(dat_file_path):
        print(f"Arquivo não encontrado: {dat_file_path}")
        return ('', '', '', '', '', '', '', '', '', '')

    try:
        with open(dat_file_path, 'r') as datfile:
            lines = datfile.readlines()
            if lines:
                last_line = lines[-1].strip()  # Ler a última linha e remover espaços em branco extras
                columns = last_line.split('\t')  # Usar tabulação como delimitador
                if len(columns) >= 20:  # Garantir que há colunas suficientes
                    # Obter o valor da 20ª coluna
                    dat_depth = float(columns[19])
                    
                    # Calcular object_depth_min e object_depth_max
                    if average_depth is not None:
                        depth_difference = (dat_depth - average_depth) / 10
                        object_depth_min = round(depth_difference)  # Arredondar para número inteiro
                        object_depth_max = object_depth_min + 2  # Somar 2 ao valor arredondado
                    else:
                        object_depth_min = object_depth_max = ''

                    # Retornar os outros dados
                    return (
                        object_depth_min, object_depth_max,
                        columns[1] if columns[1] else '',    # object_sound_velocity
                        columns[2] if columns[2] else '',    # object_water_density
                        columns[4] if columns[4] else '',    # object_conductivity
                        columns[5] if columns[5] else '',    # object_salinity
                        columns[6] if columns[6] else '',    # object_dissol_oxygen
                        columns[7] if columns[7] else '',    # object_oxygen_saturation
                        columns[8] if columns[8] else '',    # object_water_temperature
                        columns[15] if columns[15] else ''   # object_Chla_fluor
                    )
                else:
                    print(f"Colunas insuficientes no arquivo: {dat_file_path}")
                    return ('', '', '', '', '', '', '', '', '', '')
            else:
                print(f"Arquivo vazio: {dat_file_path}")
                return ('', '', '', '', '', '', '', '', '', '')
    except Exception as e:
        print(f"Erro ao ler o arquivo {dat_file_path}: {e}")
        return ('', '', '', '', '', '', '', '', '', '')

# Percorrer cada diretório dentro do diretório "LOKI_para_fazer"
for dir_name in os.listdir(base_directory):
    dir_path = os.path.join(base_directory, dir_name)
    
    if os.path.isdir(dir_path):  # Processar apenas diretórios
        telemetrie_directory = os.path.join(dir_path, "Telemetrie")  # Substituir "Telemetry" por "Telemetrie"
        vinhetes_directory = os.path.join(dir_path, "Vinhetes")  # Subdiretório "Vinhetes"
        output_tsv = os.path.join(dir_path, f"ecotaxa_{dir_name}_data.tsv")  # Prefixar o nome do arquivo de saída com 'ecotaxa_'

        # Calcular a média dos cinco primeiros arquivos .dat
        average_depth = calculate_average_depth(telemetrie_directory)

        # Percorrer o subdiretório "Vinhetes" e coletar os nomes dos arquivos de imagem
        image_data = []
        if os.path.exists(vinhetes_directory):
            for file in os.listdir(vinhetes_directory):
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif')):
                    img_file_name = os.path.basename(file)  # Extrair apenas o nome do arquivo
                    object_id = os.path.splitext(file)[0]

                    # Extrair data e hora do nome do arquivo
                    date_time_str = object_id[:15]
                    object_date = date_time_str[:8]  # Primeiros 8 caracteres para data (yyyymmdd)
                    object_time = date_time_str[9:15]  # Últimos 6 caracteres para hora (hhmmss)

                    # Construir o caminho correspondente ao arquivo .dat
                    dat_file_name = f"{object_date} {object_time}.dat"
                    dat_file_path = os.path.join(telemetrie_directory, dat_file_name)

                    # Extrair profundidade e informações adicionais do arquivo .dat
                    (object_depth_min, object_depth_max, object_sound_velocity, object_water_density,
                     object_conductivity, object_salinity, object_dissol_oxygen, object_oxygen_saturation,
                     object_water_temperature, object_Chla_fluor) = get_data_from_dat_file(dat_file_path, average_depth)

                    # Extrair lat, lon e profundidade da amostra com base no nome do diretório
                    object_lat, object_lon, sample_bottomdepth = lat_lon_depth_data.get(dir_name, ('', '', ''))

                    # Preencher os campos de amostra com os valores requeridos
                    sample_id = sample_idLOKI = sample_idIEAPM = sample_idBNDO = dir_name
                    sample_tow_type = "vertical"
                    sample_net_type = "WP2"
                    sample_net_mesh = "200 µm"

                    # Adicionar 'Loki' como o campo acq_instrument
                    acq_id = "OAXLII_" + str(dir_name) # Atualizar o nome da Operantar
                    acq_instrument = "LOKI"

                    # Preparar os dados da linha
                    row_data = [
                        img_file_name, object_id, object_lat, object_lon, 
                        object_date, object_time, 
                        object_depth_min, object_depth_max, object_sound_velocity, 
                        object_water_density, object_conductivity, object_salinity, 
                        object_dissol_oxygen, object_oxygen_saturation, object_water_temperature, 
                        object_Chla_fluor, acq_id, acq_instrument, 
                        sample_id, sample_idLOKI, sample_idIEAPM, 
                        sample_idBNDO, sample_bottomdepth, 
                        sample_tow_type, sample_net_type, sample_net_mesh
                    ]

                    # Adicionar a linha de dados
                    image_data.append(row_data)

        # Escrever os dados no arquivo TSV para o diretório atual
        if image_data:
            with open(output_tsv, 'w', newline='') as tsvfile:
                writer = csv.writer(tsvfile, delimiter='\t')
                
                # Escrever o cabeçalho
                headers = [
                    "img_file_name", "object_id", "object_lat", "object_lon", "object_date", "object_time", 
                    "object_depth_min", "object_depth_max", "object_sound_velocity", "object_water_density", 
                    "object_conductivity", "object_salinity", "object_dissol_oxygen", "object_oxygen_saturation",
                    "object_water_temperature", "object_Chla_fluor", "acq_id",  
                    "acq_instrument", "sample_id", "sample_idLOKI", 
                    "sample_idIEAPM", "sample_idBNDO", "sample_bottomdepth", "sample_tow_type", 
                    "sample_net_type", "sample_net_mesh"
                ]
                writer.writerow(headers)
                
                # Escrever a segunda linha com metadados atualizados
                metadata = [
                    "[t]", "[t]", "[f]", "[f]", "[t]", "[t]", 
                    "[f]", "[f]", "[f]", "[f]", "[f]", "[f]", "[f]", "[f]", 
                    "[f]", "[f]", "[t]", "[t]", "[t]", "[t]", "[t]",
                    "[t]", "[t]", "[t]", "[t]", "[t]"
                ]
                writer.writerow(metadata)
                
                # Escrever os dados das imagens
                for data in image_data:
                    writer.writerow(data)

            print(f"Arquivo TSV foi criado em: {output_tsv}")
