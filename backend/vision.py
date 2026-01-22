import cv2
import numpy as np
import os

def processar_imagem_para_leitura(caminho_arquivo_original):
    print(f"👀 [Vision] Modo Grid Matemático: {caminho_arquivo_original}")
    
    img = cv2.imread(caminho_arquivo_original)
    if img is None: return None, "Erro leitura"

    # 1. Redimensionamento Seguro (1200px é suficiente e rápido)
    h_orig, w_orig = img.shape[:2]
    fator = 1
    if w_orig > 1200:
        fator = 1200 / w_orig
        img = cv2.resize(img, (0, 0), fx=fator, fy=fator)
    
    h, w = img.shape[:2]
    img_final = img.copy()

    # 2. Binarização Simples (Invertida: Tinta = Branco, Papel = Preto)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Threshold Adaptativo (Melhor que o global para iluminação irregular)
    img_bin = cv2.adaptiveThreshold(
        img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 4
    )

    # 3. PROJEÇÃO VERTICAL (Achar Colunas)
    # Somamos os pixels brancos de cada coluna
    proj_vert = np.sum(img_bin, axis=0)
    
    # Normalizamos para facilitar a detecção (0 a 1)
    proj_vert_norm = proj_vert / np.max(proj_vert)
    
    # Filtro: Onde tem "bastante" tinta verticalmente?
    # Colunas de gabarito são picos densos.
    colunas_mask = proj_vert_norm > 0.20 # 20% da densidade máxima
    
    # Achar intervalos (início e fim de cada coluna)
    colunas_intervals = []
    dentro = False
    start = 0
    for i, val in enumerate(colunas_mask):
        if val and not dentro:
            dentro = True
            start = i
        elif not val and dentro:
            dentro = False
            # Filtro de largura: Uma coluna deve ter entre 50px e 400px
            largura = i - start
            if 50 < largura < 400:
                colunas_intervals.append((start, i))

    print(f"📊 Colunas detectadas: {len(colunas_intervals)}")

    # 4. PROJEÇÃO HORIZONTAL (Achar Linhas DENTRO das Colunas)
    respostas_encontradas = 0
    
    for (x1, x2) in colunas_intervals:
        # Desenha a caixa da coluna (Azul)
        cv2.rectangle(img_final, (x1, 0), (x2, h), (255, 0, 0), 2)
        
        # Recorta a coluna para analisar as linhas
        fatia = img_bin[:, x1:x2]
        
        # Soma Horizontal (axis=1) para achar onde estão as questões
        proj_horiz = np.sum(fatia, axis=1)
        proj_horiz_norm = proj_horiz / np.max(proj_horiz)
        
        linhas_mask = proj_horiz_norm > 0.10 # Linhas tem menos tinta que colunas
        
        # Achar intervalos das linhas (Questões)
        linhas_intervals = []
        dentro_linha = False
        start_y = 0
        for j, val_y in enumerate(linhas_mask):
            if val_y and not dentro_linha:
                dentro_linha = True
                start_y = j
            elif not val_y and dentro_linha:
                dentro_linha = False
                altura = j - start_y
                # Filtro: Uma linha de questão tem altura específica (~15 a 60px)
                if 15 < altura < 80:
                    linhas_intervals.append((start_y, j))

        # AGORA TEMOS O GRID: Cruzamento de (x1, x2) com (y1, y2)
        # Mas dentro desse cruzamento tem 5 letras (A, B, C, D, E)
        # Vamos dividir esse retângulo em 5 pedaços iguais matematicamente.
        
        for (y1, y2) in linhas_intervals:
            # Largura total da linha
            largura_total = x2 - x1
            largura_opcao = largura_total / 5 # Divide em 5 (A, B, C, D, E)
            
            melhor_densidade = 0
            melhor_opcao_x = -1
            
            for k in range(5):
                # Coordenadas da "Caixinha" da letra
                box_x1 = int(x1 + (k * largura_opcao))
                box_x2 = int(x1 + ((k+1) * largura_opcao))
                
                # Margem de segurança (para não pegar a borda)
                margin = 4
                roi = img_bin[y1+margin:y2-margin, box_x1+margin:box_x2-margin]
                
                # Mede a tinta aqui
                if roi.size == 0: continue
                densidade = cv2.countNonZero(roi) / roi.size
                
                # Desenha o Grid (Amarelo fraquinho)
                cv2.rectangle(img_final, (box_x1, y1), (box_x2, y2), (0, 255, 255), 1)
                
                # VERIFICAÇÃO DE RESPOSTA
                # Se tiver mais de 45% de tinta, é uma marcação
                if densidade > 0.45:
                    cv2.rectangle(img_final, (box_x1, y1), (box_x2, y2), (0, 255, 0), 2)
                    # cv2.putText(img_final, f"{densidade:.2f}", (box_x1, y1-2), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0,255,0), 1)
                    respostas_encontradas += 1

    print(f"🟢 Total Grid: {respostas_encontradas}")

    pasta, nome_arquivo = os.path.split(caminho_arquivo_original)
    caminho_final = os.path.join(pasta, f"proc_{nome_arquivo}")
    cv2.imwrite(caminho_final, img_final)
    
    return caminho_final, f"Grid leu {respostas_encontradas}"