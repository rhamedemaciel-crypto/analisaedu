import cv2
import numpy as np
import os

def processar_imagem_para_leitura(caminho_arquivo_original):
    print(f"👀 [Vision] Modo Seguro + Filtro Geométrico: {caminho_arquivo_original}")
    
    img = cv2.imread(caminho_arquivo_original)
    if img is None: return None, "Erro leitura"

    # 1. Redimensionamento Seguro
    altura, largura = img.shape[:2]
    fator = 1
    if largura > 1200:
        fator = 1200 / largura
        img = cv2.resize(img, (0, 0), fx=fator, fy=fator)
    
    area_imagem_total = img.shape[0] * img.shape[1]

    # 2. Tratamento (O Clássico que funciona)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
    
    img_binaria = cv2.adaptiveThreshold(
        img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 19, 5
    )

    # Limpeza (Mantida pois estabiliza a imagem)
    kernel = np.ones((3,3), np.uint8)
    img_binaria = cv2.erode(img_binaria, kernel, iterations=1)
    img_binaria = cv2.dilate(img_binaria, kernel, iterations=2)

    # 3. Detectar (RETR_TREE)
    contornos, hierarchy = cv2.findContours(img_binaria, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    img_final = img.copy()
    contador_bolinhas = 0

    # --- AJUSTES FINAIS ---
    # Baixamos a densidade para salvar a 105
    MIN_DENSIDADE = 0.70
    # Mantemos circularidade média
    MIN_CIRCULARIDADE = 0.60
    
    for cnt in contornos:
        area = cv2.contourArea(cnt)
        perimetro = cv2.arcLength(cnt, True)
        
        # Proteção contra divisão por zero (Isso evita travar o servidor)
        if perimetro == 0 or area == 0: continue

        # Filtro de tamanho
        if area < 100 or area > 5000: continue

        (x, y, w, h) = cv2.boundingRect(cnt)
        
        # --- PROTEÇÃO CONTRA FANTASMAS: ASPECT RATIO ---
        # Bolinhas devem caber num quadrado (largura ~= altura)
        # Se a largura for muito diferente da altura (> 20% de diferença), é lixo.
        aspect_ratio = float(w) / h
        if aspect_ratio < 0.8 or aspect_ratio > 1.2:
            continue # Pula para o próximo (ignora letras compridas)

        # Cálculos normais
        porcentagem_area = (area / area_imagem_total) * 100
        circularidade = (4 * np.pi * area) / (perimetro ** 2)
        
        roi = img_binaria[y:y+h, x:x+w]
        pixels_brancos = cv2.countNonZero(roi)
        densidade = pixels_brancos / (w * h)

        # Regras
        passou_tamanho = 0.05 < porcentagem_area < 2.0
        passou_forma = circularidade > MIN_CIRCULARIDADE
        passou_densidade = densidade > MIN_DENSIDADE

        if passou_tamanho and passou_forma and passou_densidade:
            # SUCESSO (Verde)
            cv2.rectangle(img_final, (x, y), (x + w, y + h), (0, 255, 0), 2)
            contador_bolinhas += 1
            
            # Debug: Mostra o valor pra gente ter certeza
            # cv2.putText(img_final, f"{densidade:.2f}", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,255,0), 1)

    print(f"🟢 Resultado Seguro: {contador_bolinhas} detectadas.")

    pasta, nome_arquivo = os.path.split(caminho_arquivo_original)
    caminho_final = os.path.join(pasta, f"proc_{nome_arquivo}")
    cv2.imwrite(caminho_final, img_final)
    
    return caminho_final, f"Leu {contador_bolinhas} gabaritos"