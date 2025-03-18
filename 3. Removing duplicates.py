# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 15:44:35 2024

@author: Zbook
"""

import os
import shutil
import openpyxl
from datetime import datetime, timedelta

# Diretório contendo as imagens
station = 'B01'
raw_directory = "D:/Projects/Antartica_Ecopelagos/Operantar_XLII_Dados/" + station + "/"
directory = raw_directory + "Vinhetes/"


def extract_info(filename):
    # Remover a extensão do arquivo
    name, _ = os.path.splitext(filename)
    
    # Substituir espaços duplos por um caractere único (ex.: espaço simples ou "_")
    name = name.replace('  ', ' ').replace('_', ' ')
    
    # Dividir a string em partes
    parts = name.split(' ')
    
    if len(parts) == 9:
        try:
            return [int(part) for part in parts]
        except ValueError:
            print(f"Não foi possível converter os componentes para inteiros: {parts}")
            return None
    else:
        print(f"O nome do arquivo não corresponde ao formato esperado: {filename}")
        return None

def find_duplicates(directory):
    if not os.path.exists(directory):
        print(f"O diretório {directory} não existe.")
        return
    
    # Criar o diretório "Duplicadas"
    duplicated_dir = os.path.join(directory, 'Duplicadas')
    if not os.path.exists(duplicated_dir):
        os.makedirs(duplicated_dir)

    files_info = []

    # Listar e processar os arquivos no diretório
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            info = extract_info(filename)
            if info:
                files_info.append((filename, info))
            else:
                print(f"Não foi possível extrair informações do arquivo: {filename}")

    # Verificação se há arquivos processados
    if not files_info:
        print("Nenhuma informação de arquivo foi extraída.")
        return

    # Ordenar os arquivos pelo tempo
    files_info.sort(key=lambda x: (x[1][0], x[1][1]))

    # Criar a planilha
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Informações das Imagens"
    headers = ["Data", "Hora", "Número da Imagem", "Número de Sequência 1", "Número de Sequência 2", 
               "Número de Sequência 3", "Posição do Recorte", "Largura do Recorte", "Altura do Recorte", "Arquivo"]
    sheet.append(headers)

    for filename, info in files_info:
        sheet.append(info + [filename])
    
    planilha_path = os.path.join(directory, "informacoes_imagens.xlsx")
    workbook.save(planilha_path)
    print(f"Planilha criada em: {planilha_path}")

    # Encontrar e mover as duplicatas
    tolerance = 5
    moved_files = set()
    
    def time_within_two_seconds(time1, time2):
        datetime1 = datetime.strptime(f"{time1[0]} {time1[1]}", "%Y%m%d %H%M%S")
        datetime2 = datetime.strptime(f"{time2[0]} {time2[1]}", "%Y%m%d %H%M%S")
        return abs((datetime1 - datetime2).total_seconds()) <= 2

    for i, (filename1, info1) in enumerate(files_info):
        if filename1 in moved_files:
            continue
        for j in range(i+1, len(files_info)):
            filename2, info2 = files_info[j]
            if filename2 in moved_files:
                continue
            if not time_within_two_seconds(info1, info2):
                break
            if (abs(info1[6] - info2[6]) <= tolerance and
                abs(info1[7] - info2[7]) <= tolerance and
                abs(info1[8] - info2[8]) <= tolerance):
                src_path = os.path.join(directory, filename2)
                dst_path = os.path.join(duplicated_dir, filename2)
                if not os.path.exists(dst_path):
                    shutil.move(src_path, dst_path)
                    moved_files.add(filename2)
                    #print(f"Movendo duplicata: {filename2} para {duplicated_dir}")


# Chamar a função find_duplicates com o caminho do diretório
find_duplicates(directory)
