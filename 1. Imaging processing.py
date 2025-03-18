# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 18:06:39 2024

@author: Zbook
"""


#%% Importa bibliotecas de manipulação de arquivos

import os
from os import listdir
from os.path import isfile, join
import numpy as np
import shutil
from PIL import Image, ImageChops

lista_telem = []
lista_vinhetes = []
lista_telemetrie = []
# Diretório contendo as imagens
station = 'B01'
raw_directory = "D:/Projects/Antartica_Ecopelagos/Operantar_XLII_Dados/" + station + "/LOKI_12023.01/"
directory_read = "D:/Projects/Antartica_Ecopelagos/Operantar_XLII_Dados/" + station + "/LOKI_12023.01/"
#directory_read = "E:/Operantar_XLI_2023_NP_Alte_Maximiano/LOKI/" + station + "/"
directory = raw_directory + "Imagens_Subida/"
directory_vinhetes = directory_read + "Pictures/"
directory_data = directory_read + "Telemetrie/"



if not os.path.exists(raw_directory):
    os.makedirs(raw_directory)

if not os.path.exists(directory):
    os.makedirs(directory)



#%% Cria duas listas de arquivos, uma de imagens e outra de dados da telemetria
lista_diretorios = [h for h in listdir(directory_vinhetes)]
for subdir in lista_diretorios:
    g = listdir(directory_vinhetes + subdir)
    for im in g:
        if not im.startswith('.'):
            dup = (im,subdir)
            lista_vinhetes.append(dup)
    
lista_telem = [g for g in listdir(directory_data) if isfile(join(directory_data, g))]
for elem in lista_telem:
    if elem[-3:] == "dat":
        lista_telemetrie.append(elem)
  
#%% Empilha os arquivos dat e extrai a pressão para um array
def read_dat_file(file_path):
    with open(file_path, 'r') as file:
        content = file.readline() # Read the first line of the file
        values = content.strip().split('\t')
        return values

def stack_values_from_dat_files(directory_data):
    dat_files = [file for file in os.listdir(directory_data) if file.endswith('.dat')]
    stacked_values = []

    for file_name in dat_files:
        file_path = os.path.join(directory_data, file_name)
        values = read_dat_file(file_path)
        if values:
            stacked_values.append(values)

    return stacked_values

if __name__ == '__main__':
    stacked_values = stack_values_from_dat_files(directory_data)
        

press = []

for linha in stacked_values:
    press.append(float(linha[19]))  # COLUNA QUE REPRESENTA A PRESSAO


#%% METODO PARA EXTRACAO DOS DADOS (ABIOTICOS) DE SUBIDA ------------------------            
i_pmax    = press.index(max(press)) #indice da pressao maxima
max_press = max(press) # valor da pressao maxima

                 
#dens_new  = dens[i_pmax::]   
press_new = press[i_pmax::]

#i_dens1020 = np.where(np.asarray(dens_new)<1020)[0] #indice da densidade maxima, transformada em array 
i_subida = np.where(np.asarray(press)<=max_press)[0] 

ini = i_pmax   # INDICE DO INICIO, definido como início na pressao máxima
f_subida = np.where(np.asarray(press_new)>=85)[0] 
fim = len(f_subida)+ini


      
#%% METODO PARA EXTRACAO DOS DADOS (IMAGENS) DE SUBIDA --------------------------

TL_ini = lista_telemetrie[ini]  # inicio na lista de telemetrie, a partir do indice ´ini´
TL_fim = lista_telemetrie[fim]  # final na lista de telemetrie, a partir do índice ´fim´

TL_ini = TL_ini[0:15:]    # formatando o nome do arquivo, pegando apenas os 15 primeiros números
TL_fim = TL_fim[0:15:]    # formatando o nome do arquivo, pegando apenas os 15 primeiros números

tempo_ini = float(TL_ini[9:15])
tempo_fim = float(TL_fim[9:15])

#%% Mover arquivos das imagens para uma nova pasta
#os.makedirs(directory, exist_ok=True)

for elem in lista_vinhetes:
    arq,diret = elem
    if arq != 'Thumbs.db':
        hora = float(arq[9:15])
        if hora >= tempo_ini and hora <= tempo_fim:
            shutil.copy(os.path.join(directory_vinhetes, diret, arq), directory)


#%% Novo Script para criar a pasta output 1


# Número de imagens para criar o background
num_images_for_background = 10

# Função para processar as imagens
def process_images(directory, num_images_for_background=10, images_per_background=1000):
    # Obtém a lista de arquivos no diretório
    files = os.listdir(directory)

    # Ordena a lista de arquivos em ordem alfabética
    files.sort()

    # Dicionário para armazenar os tamanhos das imagens e os diretórios de saída
    sizes = {}

    for filename in files:
        if filename.lower().endswith((".jpg", ".png", ".bmp")):
            filepath = os.path.join(directory, filename)

            # Abre a imagem
            image = Image.open(filepath)

            # Verifica se a imagem possui um tamanho válido
            size = image.size
            if size not in sizes and is_image_size_valid(image, size):
                sizes[size] = []

            if size in sizes:
                sizes[size].append(filepath)

    # Cria diretórios de saída para cada tamanho e processa as imagens
    for size, image_list in sizes.items():
        output_directory = os.path.join(raw_directory, f"output_{size[0]}x{size[1]}")
        os.makedirs(output_directory, exist_ok=True)

        if len(image_list) < num_images_for_background:
            # Copia as imagens para o diretório de saída se o número de imagens for menor que 10
            for image_path in image_list:
                shutil.copy(image_path, output_directory)
        else:
            for i in range(0, len(image_list), images_per_background):
                # Seleciona o bloco de imagens para criar a imagem de fundo
                block_images = [Image.open(image_list[j]) for j in range(i, min(i + num_images_for_background, len(image_list)))]

                # Cria a imagem de fundo
                background_image = create_background_image(block_images, size)

                # Salva a imagem de fundo para verificação
                #background_image.save(os.path.join(output_directory, f"background_image_{i // images_per_background}.png"))

                # Processa as imagens do bloco atual
                for image_path in image_list[i:i + images_per_background]:
                    process_image(image_path, background_image, output_directory, size)

    print("Processamento concluído.")

# Função para verificar se a imagem possui o tamanho desejado
def is_image_size_valid(image, size):
    return image.size == size

# Função para processar uma imagem específica
def process_image(image_path, background_image, output_directory, size):
    image = Image.open(image_path).resize(size)

    # Calcula a diferença entre a imagem original e a imagem de fundo
    difference_image = difference_images(image, background_image)

    # Salva a imagem resultante
    #result_filename = os.path.basename(image_path).replace(".", "_difference.")
    result_filename = os.path.basename(image_path)
    result_filepath = os.path.join(output_directory, result_filename)
    difference_image.save(result_filepath)

# Nova função para criar a imagem de background
def create_background_image(images, size):
    if len(images) < 10:
        raise ValueError("Pelo menos dez imagens são necessárias para criar o background.")

    # Redimensiona todas as imagens para o mesmo tamanho
    resized_images = [image.resize(size) for image in images]

    # Cria array numpy para os pixels
    pixels = np.array([np.array(image) for image in resized_images])

    # Inicializa a imagem de fundo com zeros
    background_pixels = np.zeros(pixels[0].shape, dtype=np.uint8)

    # Define um limiar para a coincidência (pelo menos 5 das 10 imagens)
    threshold = 5

    # Percorre cada pixel e verifica se ao menos 5 das 10 imagens têm o mesmo valor para esse pixel
    for i in range(size[1]):
        for j in range(size[0]):
            pixel_values, counts = np.unique(pixels[:, i, j], axis=0, return_counts=True)
            background_pixels[i, j] = pixel_values[np.argmax(counts >= threshold)]

    # Cria a imagem de background a partir dos pixels calculados
    background_image = Image.fromarray(background_pixels)

    return background_image

# Função para calcular a diferença entre duas imagens em tons de cinza pixel a pixel
def difference_images(image1, image2):
    # Verifica se as imagens têm o mesmo tamanho
    if image1.size != image2.size:
        raise ValueError("As imagens devem ter o mesmo tamanho.")

    # Converte as imagens para escala de cinza
    image1_gray = image1.convert("L")
    image2_gray = image2.convert("L")

    # Calcula a diferença entre as imagens
    difference_image = ImageChops.difference(image1_gray, image2_gray)

    return difference_image

# Processa as imagens do diretório
process_images(directory, num_images_for_background)


#%% Script para melhorar ainda mais as imagens
# Criação da pasta output 2

# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 15:10:59 2023

@author: Zbook
"""

directory = raw_directory + "output_1360x1024/"

# Função para processar as imagens
def process_images2(directory):
    # Obtém a lista de arquivos no diretório
    files = os.listdir(directory)

    # Ordena a lista de arquivos em ordem alfabética
    files.sort()

    # Dicionário para armazenar os tamanhos das imagens e os diretórios de saída
    sizes = {}

    for filename in files:
        if filename.lower().endswith((".jpg", ".png", ".bmp")):
            filepath = os.path.join(directory, filename)

            # Abre a imagem
            image = Image.open(filepath)

            # Verifica se a imagem possui um tamanho válido
            size = image.size
            if size not in sizes and is_image_size_valid2(image, size):
                sizes[size] = []

            if size in sizes:
                sizes[size].append(filepath)

    # Cria diretórios de saída para cada tamanho e processa as imagens
    for size, image_list in sizes.items():
        output_directory = os.path.join(raw_directory, f"output2_{size[0]}x{size[1]}")
        os.makedirs(output_directory, exist_ok=True)
        process_images_of_size(size, image_list, output_directory)

    #print("Processamento concluído.")

# Função para verificar se a imagem possui o tamanho desejado
def is_image_size_valid2(image, size):
    return image.size == size

# Função para processar as imagens de um tamanho específico
def process_images_of_size(size, image_list, output_directory):
    # Variável para armazenar a imagem anterior
    previous_image = None

    for filepath in image_list:
        filename = os.path.basename(filepath)
        # Abre a imagem original
        original_image = Image.open(filepath)

        if previous_image is None:
            previous_image = original_image.copy()
        else:
            # Subtrai a imagem de fundo (anterior) da imagem atual
            subtracted_image = subtract_images(original_image, previous_image)

            # Salva a imagem resultante no diretório de saída
            result_filename = filename
            result_filepath = os.path.join(output_directory, result_filename)
            subtracted_image.save(result_filepath)

            # Define a imagem atual como a imagem anterior para o próximo loop
            previous_image = original_image.copy()

# Função para subtrair duas imagens em tons de cinza pixel a pixel
def subtract_images(image1, image2):
    # Verifica se as imagens têm o mesmo tamanho
    if image1.size != image2.size:
        raise ValueError("As imagens devem ter o mesmo tamanho.")

    # Converte as imagens para escala de cinza
    image1_gray = image1.convert("L")
    image2_gray = image2.convert("L")

    # Subtrai uma imagem da outra
    subtracted_image = ImageChops.subtract(image1_gray, image2_gray)

    # Converte os valores negativos para zero
    subtracted_image = np.maximum(np.array(subtracted_image), 0)
    subtracted_image = Image.fromarray(subtracted_image.astype(np.uint8))

    return subtracted_image

# Processa as imagens do diretório
process_images2(directory)
