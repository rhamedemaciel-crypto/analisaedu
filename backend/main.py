from fastapi import FastAPI, Depends, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import shutil
import os
import uuid
import traceback
import json

# Seus módulos locais
import models
import database
import vision       # Seu código de contornos (OMR)
import vision_ocr   # Sua IA de Redação (Gemini/OCR)

# Garante que as tabelas existem (Criação automática se não existirem)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Configuração de CORS (Permite que o React acesse)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monta a pasta de uploads para ser acessível via URL (ex: http://localhost:8000/imagens/foto.jpg)
os.makedirs("uploads", exist_ok=True)
app.mount("/imagens", StaticFiles(directory="uploads"), name="imagens")

# Dependência de Banco de Dados
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"status": "Online", "sistema": "AnalisaEdu - Núcleo SAEV Municipal"}

# --- ROTA A: CORREÇÃO OBJETIVA (GABARITO) ---
# Mudança: Agora exigimos 'avaliacao_id' para saber de qual prova é esse cartão
@app.post("/enviar-gabarito/{aluno_id}")
def enviar_gabarito(
    aluno_id: int, 
    avaliacao_id: int = Form(...), # Novo campo obrigatório
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    print(f"\nQw [ROTA A] GABARITO | Aluno: {aluno_id} | Prova: {avaliacao_id}")
    
    # 1. Validação de Segurança (O aluno e a prova existem?)
    aluno = db.query(models.Aluno).filter(models.Aluno.id == aluno_id).first()
    avaliacao = db.query(models.Avaliacao).filter(models.Avaliacao.id == avaliacao_id).first()
    
    if not aluno:
        raise HTTPException(404, "Aluno não encontrado.")
    if not avaliacao:
        raise HTTPException(404, "Avaliação não encontrada.")

    try:
        # 2. Salvar Arquivo
        extensao = file.filename.split(".")[-1]
        nome_arquivo = f"gabarito_prova{avaliacao_id}_aluno{aluno_id}_{uuid.uuid4()}.{extensao}"
        caminho_arquivo = f"uploads/{nome_arquivo}"
        
        with open(caminho_arquivo, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 3. Processamento (Seu código 'vision.py')
        # vision.processar... retorna (caminho_imagem_processada, resultado_texto)
        resultado = vision.processar_imagem_para_leitura(caminho_arquivo)
        
        if not resultado:
             raise Exception("Erro no processamento da imagem (OpenCV falhou)")

        caminho_proc, msg_status = resultado

        # 4. Gravação no Banco (Modelo Novo)
        nova_resposta = models.Resposta(
            aluno_id=aluno_id,
            avaliacao_id=avaliacao_id, # Vinculo institucional
            url_foto_cartao=caminho_arquivo,
            status="corrigido_automatico",
            # Salvamos o resultado técnico no JSON para auditoria
            resultado_correcao={"tipo": "gabarito_omr", "dados_cv": msg_status} 
        )
        
        db.add(nova_resposta)
        db.commit()

        return {
            "mensagem": "Gabarito processado com sucesso!",
            "aluno": aluno.nome,
            "escola": aluno.turma.escola.nome, # Mostrando que o sistema conhece a escola
            "arquivo_debug": os.path.basename(caminho_proc),
            "resultado_bruto": msg_status
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# --- ROTA B: CORREÇÃO DISCURSIVA (REDAÇÃO/IA) ---
@app.post("/enviar-redacao/{aluno_id}")
def enviar_redacao(
    aluno_id: int, 
    avaliacao_id: int = Form(...), # Novo campo obrigatório
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    print(f"\n📝 [ROTA B] REDAÇÃO | Aluno: {aluno_id} | Prova: {avaliacao_id}")
    
    # 1. Validação
    aluno = db.query(models.Aluno).filter(models.Aluno.id == aluno_id).first()
    avaliacao = db.query(models.Avaliacao).filter(models.Avaliacao.id == avaliacao_id).first()
    
    if not aluno or not avaliacao:
        raise HTTPException(404, "Aluno ou Avaliação não encontrados.")

    try:
        # 2. Salvar Arquivo
        extensao = file.filename.split(".")[-1]
        nome_arquivo = f"redacao_prova{avaliacao_id}_aluno{aluno_id}_{uuid.uuid4()}.{extensao}"
        caminho_arquivo = f"uploads/{nome_arquivo}"
        
        with open(caminho_arquivo, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 3. Processamento IA (Seu código 'vision_ocr.py')
        texto_transcrito = vision_ocr.processar_redacao(caminho_arquivo)

        # 4. Gravação no Banco (Modelo Novo)
        nova_resposta = models.Resposta(
            aluno_id=aluno_id,
            avaliacao_id=avaliacao_id,
            url_foto_redacao=caminho_arquivo,
            texto_transcrito=texto_transcrito, # Campo específico para texto
            status="transcrito_aguardando_correcao"
        )
        
        db.add(nova_resposta)
        db.commit()

        return {
            "mensagem": "Redação recebida e transcrita!",
            "aluno": aluno.nome,
            "prova": avaliacao.nome,
            "texto_identificado": texto_transcrito
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))