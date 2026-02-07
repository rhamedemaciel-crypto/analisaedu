from fastapi import FastAPI, Depends, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import shutil
import os
import uuid
import traceback
import models
import database

# Importa os DOIS módulos de visão
import vision      # Seu código de contornos (Gabarito 89/90)
import vision_ocr  # O novo código de IA (Redação)

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/imagens", StaticFiles(directory="uploads"), name="imagens")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"status": "Online", "sistema": "AnalisaEdu Híbrido"}

# --- ROTA A: GABARITO (Usa seu vision.py estável) ---
@app.post("/enviar-gabarito/{aluno_id}")
def enviar_gabarito(aluno_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    print(f"\nQw [ROTA A] GABARITO para aluno {aluno_id}")
    
    try:
        extensao = file.filename.split(".")[-1]
        nome_arquivo = f"gabarito_{uuid.uuid4()}.{extensao}"
        caminho_arquivo = f"uploads/{nome_arquivo}"
        
        with open(caminho_arquivo, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Chama seu algoritmo de contornos
        resultado = vision.processar_imagem_para_leitura(caminho_arquivo)
        
        # O seu vision.py retorna (caminho_proc, mensagem_string)
        if not resultado:
             raise Exception("Erro no processamento da imagem")

        caminho_proc, msg_status = resultado

        nova_resposta = models.Resposta(
            aluno_id=aluno_id,
            url_foto_cartao=caminho_arquivo,
            respostas_identificadas={"tipo": "gabarito", "status": msg_status}
        )
        db.add(nova_resposta)
        db.commit()

        return {
            "mensagem": "Gabarito processado!",
            "arquivo_processado": os.path.basename(caminho_proc),
            "info": msg_status,
            "tipo": "gabarito"
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# --- ROTA B: REDAÇÃO (Usa a IA do Google) ---
@app.post("/enviar-redacao/{aluno_id}")
def enviar_redacao(aluno_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    print(f"\n📝 [ROTA B] REDAÇÃO para aluno {aluno_id}")
    
    try:
        extensao = file.filename.split(".")[-1]
        nome_arquivo = f"redacao_{uuid.uuid4()}.{extensao}"
        caminho_arquivo = f"uploads/{nome_arquivo}"
        
        with open(caminho_arquivo, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Chama a IA
        texto_transcrito = vision_ocr.processar_redacao(caminho_arquivo)

        nova_resposta = models.Resposta(
            aluno_id=aluno_id,
            url_foto_redacao=caminho_arquivo,
            respostas_identificadas={"tipo": "redacao", "texto": texto_transcrito}
        )
        db.add(nova_resposta)
        db.commit()

        return {
            "mensagem": "Redação transcrita!",
            "arquivo_original": nome_arquivo,
            "texto_transcrito": texto_transcrito,
            "tipo": "redacao"
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))