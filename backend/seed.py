print("🚀 Iniciando script de reset do banco...") # PROVA DE VIDA
from database import SessionLocal, engine, Base
from models import Instituicao, Escola, Turma, Aluno, Avaliacao
import json
import sys

# Garante que as tabelas sejam recriadas
try:
    print("🗑️  Apagando tabelas antigas...")
    Base.metadata.drop_all(bind=engine)
    print("✨ Criando novas tabelas...")
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"❌ Erro ao manipular banco: {e}")
    sys.exit(1)

db = SessionLocal()

def criar_dados():
    try:
        print("🌱 Inserindo dados fictícios...")

        # 1. Prefeitura
        pref = Instituicao(nome="Secretaria Mun. de Educação", cnpj="00.000.000/0001-00")
        db.add(pref)
        db.commit()

        # 2. Escola
        escola = Escola(nome="Escola Modelo", instituicao_id=pref.id)
        db.add(escola)
        db.commit()

        # 3. Turma
        turma = Turma(nome="9º Ano A", ano_letivo=2026, escola_id=escola.id)
        db.add(turma)
        db.commit()

        # 4. Aluno
        aluno = Aluno(nome="João da Silva", matricula="2026001", turma_id=turma.id)
        db.add(aluno)
        db.commit()

        # 5. Prova
        rubrica = [{"criterio": "Geral", "peso": 10.0}]
        prova = Avaliacao(
            nome="Redação Teste", 
            materia="Português", 
            turma_id=turma.id,
            configuracao_rubrica=json.dumps(rubrica)
        )
        db.add(prova)
        db.commit()

        print("✅ SUCESSO! Banco resetado.")
        print(f"👉 ID Aluno: {aluno.id}")
        print(f"👉 ID Avaliação: {prova.id}")
        
    except Exception as e:
        print(f"❌ Erro ao inserir dados: {e}")
        db.rollback()
    finally:
        db.close()

# ESTA LINHA É A MAIS IMPORTANTE:
if __name__ == "__main__":
    criar_dados()