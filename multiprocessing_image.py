import numpy as np
from PIL import Image
from time import perf_counter
import multiprocessing

# matriz = imagem para operação; alpha = contraste ;  beta= brilho ;
def define_brilho(matriz, alpha, beta, id, shared_array):
    # Cria-se uma imagem temporária, "vazia", com as dimensões e tipo da original (passada por parâmetro)
    imagem_result = np.zeros(matriz.shape, matriz.dtype)

    # Obtem-se as dimensões e quantidade de canais da imagem original (passada por parâmetro)
    # No nosso caso, vamos obter as dimensões em pixels (y, x) e a quantidade de canais (RGB = 3)
    y, x, c = matriz.shape

    # Percorre todos os pares x,y da imagem em todos os canais
    for ypos in range(y):
        for xpos in range(x):
            for canal in range(c):
                # Realiza-se os cálculos necessários para cada ponto e canal, mantendo o valor resultante dentro
                # do limite de 0 a 255
                imagem_result[ypos, xpos, canal] = np.clip((alpha * matriz[ypos, xpos, canal]) + beta, 0, 255)

    # Salva a matriz na lista compartilhada
    shared_array[id] = imagem_result

if __name__ == '__main__':
   
    brilho = 100
    contraste = 3
    processos = int(input("Quantidade de processos: ")) # Maximo: 508 - 25/09/2023
    
    start_time = perf_counter()
    
    # Carrega uma imagem de um arquivo
    img = Image.open('img001.jpeg')

    # Converte a imagem em uma matriz RGB
    imagem_original = np.asarray(img)

    # Dividindo a matriz + imagem[i-1].shape[1]
    imagem = []
    
    for i in range(processos):
        if i != 0:
            imagem.append(imagem_original[:,round(imagem[i-1].shape[1] * i):round(imagem[i-1].shape[1] * (i+1)),:])
        else:
            imagem.append(imagem_original[:,0:round(imagem_original.shape[1]/processos),:])

    # Crie uma lista compartilhada para armazenar as imagens resultantes
    manager = multiprocessing.Manager()
    shared_array = manager.list([None] * processos)

    # Paralelismo por Multiprocessamento
    P_imagem = []
    
    for j in range(processos):
        P_imagem.append(multiprocessing.Process(target=define_brilho, args=(imagem[j], contraste, brilho, j, shared_array)))

    # Inicializando os processos
    for i in range(processos):    
        P_imagem[i].start()
    
    # Encerrando os processos
    for j in range(processos):    
        P_imagem[j].join()
        
    # Unindo matrizes  
    matriz_final = np.concatenate(shared_array, axis=1)
            
    # Salva a nova imagem (matriz) em um novo arquivo
    imagem_final = Image.fromarray(matriz_final)
    imagem_final.save('img002.jpg')

    end_time = perf_counter()
    print(f'As tarefas levaram {end_time - start_time:0.2f} segundo(s) para executar.')
    