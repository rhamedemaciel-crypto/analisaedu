from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base

# Tabela de Avaliações (O Gabarito Oficial)
class Avaliacao(Base):
    __tablename__ = "avaliacoes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True) # Ex: "Simulado ENEM 2026"
    materia = Column(String) # Ex: "Matemática"
    
    # Aqui guardamos o gabarito oficial. Ex: {"1": "A", "2": "C"}
    gabarito = Column(JSON) 

# Tabela de Alunos
class Aluno(Base):
    __tablename__ = "alunos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    matricula = Column(String, unique=True)

# Tabela de Respostas (O que o aluno marcou/escreveu)
class Resposta(Base):
    __tablename__ = "respostas"

    id = Column(Integer, primary_key=True, index=True)
    avaliacao_id = Column(Integer, ForeignKey("avaliacoes.id"))
    aluno_id = Column(Integer, ForeignKey("alunos.id"))
    
    # O link da foto que o aluno tirou (guardaremos o caminho do arquivo)
    url_foto_cartao = Column(String, nullable=True)
    url_foto_redacao = Column(String, nullable=True)
    
    # O que o sistema entendeu da leitura (OCR)
    respostas_identificadas = Column(JSON, nullable=True)
    
    nota_final = Column(Float, default=0.0)
    
    # Cria a relação para facilitar consultas depois
    aluno = relationship("Aluno")
    avaliacao = relationship("Avaliacao")