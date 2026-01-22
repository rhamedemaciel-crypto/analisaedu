from fastapi import FastAPI, Depends, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import shutil
import os
import uuid
import traceback # Para ver os detalhes do erro
import models
import database
import vision

# Cria as tabelas
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# --- CORS LIBERADO GERAL ---
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
    return {"status": "Online"}

# --- ROTA DE EMERGÊNCIA: CRIAR ALUNO ---
@app.get("/criar-aluno")
def criar_aluno_teste(db: Session = Depends(get_db)):
    # Verifica se o aluno 1 já existe
    aluno = db.query(models.Aluno).filter(models.Aluno.id == 1).first()
    if aluno:
        return {"mensagem": "O Aluno 1 já existe! Pode enviar a prova."}
    
    # Se não existe, cria ele
    novo_aluno = models.Aluno(id=1, nome="João da Silva", matricula="2026001")
    db.add(novo_aluno)
    db.commit()
    return {"mensagem": "✅ Aluno 1 criado com sucesso! Agora tente enviar a prova."}

@app.post("/enviar-prova/{aluno_id}")
def enviar_prova(aluno_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    print(f"\n📢 [PASSO 1] Recebido pedido para aluno {aluno_id}")
    
    try:
        # 1. Salvar arquivo
        extensao = file.filename.split(".")[-1]
        nome_arquivo = f"{uuid.uuid4()}.{extensao}"
        caminho_arquivo = f"uploads/{nome_arquivo}"
        
        # Caminho absoluto para evitar erros de pasta
        caminho_absoluto = os.path.abspath(caminho_arquivo)

        print(f"📂 [PASSO 2] Salvando arquivo em: {caminho_absoluto}")

        with open(caminho_arquivo, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Visão Computacional
        print("👀 [PASSO 3] Chamando o robô de visão...")
        
        # --- AQUI É ONDE GERALMENTE DÁ ERRO ---
        resultado = vision.processar_imagem_para_leitura(caminho_arquivo)
        
        # Verificação de segurança: O robô devolveu o que a gente espera?
        if not resultado or len(resultado) != 2:
             print("❌ [ERRO] O vision.py retornou algo estranho:", resultado)
             raise Exception("Erro interno no módulo de visão")

        caminho_proc, status_visao = resultado
        print(f"✅ [PASSO 4] Visão concluiu: {status_visao}")

        # 3. Banco de Dados
        nova_resposta = models.Resposta(
            aluno_id=aluno_id,
            url_foto_cartao=caminho_arquivo
        )
        db.add(nova_resposta)
        db.commit()
        db.refresh(nova_resposta)
        print("💾 [PASSO 5] Salvo no banco de dados!")

        return {
            "mensagem": "Sucesso total!",
            "arquivo_processado": os.path.basename(caminho_proc),
            "status_visao": status_visao
        }
    

    except Exception as e:
        # Se der erro, ele vai imprimir o motivo exato no terminal
        print("\n❌❌❌ ERRO GRAVE NO SERVIDOR ❌❌❌")
        traceback.print_exc() # Imprime o erro vermelho detalhado
        # Devolve o erro pro site em vez de explodir
        raise HTTPException(status_code=500, detail=str(e))