from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Float, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# --- Nível 1: Gestão Municipal ---
class Instituicao(Base):
    __tablename__ = "instituicoes"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False) # Ex: "Secretaria de Educação"
    cnpj = Column(String, unique=True, nullable=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

# --- Nível 2: Unidade Escolar ---
class Escola(Base):
    __tablename__ = "escolas"
    id = Column(Integer, primary_key=True, index=True)
    instituicao_id = Column(Integer, ForeignKey("instituicoes.id"))
    nome = Column(String, index=True) # Ex: "Escola Municipal X"
    codigo_inep = Column(String, nullable=True)
    instituicao = relationship("Instituicao", backref="escolas")

# --- Nível 3: Sala de Aula ---
class Turma(Base):
    __tablename__ = "turmas"
    id = Column(Integer, primary_key=True, index=True)
    escola_id = Column(Integer, ForeignKey("escolas.id"))
    nome = Column(String) # Ex: "9º Ano A"
    ano_letivo = Column(Integer)
    escola = relationship("Escola", backref="turmas")

# --- Nível 4: O Aluno ---
class Aluno(Base):
    __tablename__ = "alunos"
    id = Column(Integer, primary_key=True, index=True)
    turma_id = Column(Integer, ForeignKey("turmas.id"))
    nome = Column(String, index=True)
    matricula = Column(String, unique=True)
    turma = relationship("Turma", backref="alunos")

# --- Nível 5: A Prova (Configuração) ---
class Avaliacao(Base):
    __tablename__ = "avaliacoes"
    id = Column(Integer, primary_key=True, index=True)
    turma_id = Column(Integer, ForeignKey("turmas.id"))
    nome = Column(String, index=True) # Ex: "Prova Bimestral"
    materia = Column(String)
    # Configuração da IA (Rubrica)
    configuracao_rubrica = Column(JSON, nullable=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    turma = relationship("Turma")

# --- Nível 6: As Respostas (Execução) ---
class Resposta(Base):
    __tablename__ = "respostas"
    id = Column(Integer, primary_key=True, index=True)
    avaliacao_id = Column(Integer, ForeignKey("avaliacoes.id"))
    aluno_id = Column(Integer, ForeignKey("alunos.id"))
    
    url_foto_redacao = Column(String, nullable=True)
    texto_transcrito = Column(Text, nullable=True) # O que a IA leu
    status = Column(String, default="pendente")
    
    nota_final = Column(Float, default=0.0)
    resultado_correcao = Column(JSON, nullable=True) # O detalhe da nota
    
    aluno = relationship("Aluno")
    avaliacao = relationship("Avaliacao")