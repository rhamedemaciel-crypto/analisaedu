from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# CONFIGURAÇÃO DA CONEXÃO
# Substitua 'postgres' pela sua senha real do PostgreSQL se não for essa.
# Sintaxe: postgresql://USUARIO:SENHA@localhost/NOME_DO_BANCO
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:admin123@localhost/analisaedu"

# Cria o motor de conexão
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Cria a sessão (o túnel por onde passam os dados)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base para criar as tabelas depois
Base = declarative_base()

# Função para pegar o banco de dados (Dependency Injection)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()