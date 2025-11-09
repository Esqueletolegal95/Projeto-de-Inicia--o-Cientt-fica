import cv2
import numpy as np
import os

def cortar_e_saturar(img_path, largura_padrao=256, altura_padrao=256, fator_saturacao=2.0):
    img = cv2.imread(img_path)
    if img is None:
        print(f"Erro: arquivo '{img_path}' não encontrado ou não pôde ser aberto.")
        return None

    h, w = img.shape[:2]

    # Corte (pular 10% do topo até 55% da altura)
    start_y = int(h * 0.10)
    end_y = int(h * 0.55)
    crop = img[start_y:end_y, 0:w]

    # Redimensiona para o tamanho desejado
    crop_resized = cv2.resize(crop, (largura_padrao, altura_padrao))
    hsv = cv2.cvtColor(crop_resized, cv2.COLOR_BGR2HSV)

    # Máscaras para vermelho
    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([15, 255, 255])
    lower_red2 = np.array([160, 70, 50])
    upper_red2 = np.array([180, 255, 255])
    mask_red = cv2.bitwise_or(
        cv2.inRange(hsv, lower_red1, upper_red1),
        cv2.inRange(hsv, lower_red2, upper_red2)
    )

    # Máscara para verde
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([90, 255, 255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    # Aumenta saturação só nas áreas vermelhas e verdes
    hsv = hsv.astype(np.float32)
    hsv[..., 1] = np.where(
        (mask_red > 0) | (mask_green > 0),
        np.clip(hsv[..., 1] * fator_saturacao, 0, 255),
        hsv[..., 1]
    )
    hsv = hsv.astype(np.uint8)

    # Converte de volta para BGR
    img_final = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    return img_final

def processar_pasta(entrada_dir, saida_dir):
    if not os.path.exists(saida_dir):
        os.makedirs(saida_dir)

    for filename in os.listdir(entrada_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            caminho_img = os.path.join(entrada_dir, filename)
            img_processada = cortar_e_saturar(caminho_img)

            if img_processada is not None:
                nome_saida = os.path.splitext(filename)[0] + '_cortada_saturada.png'
                caminho_saida = os.path.join(saida_dir, nome_saida)
                cv2.imwrite(caminho_saida, img_processada)
                print(f"Salvo: {caminho_saida}")
            else:
                print(f"Pulando arquivo: {caminho_img}")

# Exemplo de uso
entrada = 'pasta_imagens'
saida = 'pasta_cortadas_saturadas'

processar_pasta(entrada, saida)
