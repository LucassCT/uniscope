from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Instituicao(Base):
    __tablename__ = "instituicoes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)

    cursos = relationship("Curso", back_populates="instituicao")
    candidatos = relationship("Candidato", back_populates="instituicao")


class Curso(Base):
    __tablename__ = "cursos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo_dges = Column(Integer, nullable=False, index=True)
    name = Column(String, nullable=False)
    vagas = Column(Integer, nullable=False)
    type = Column(String, nullable=False)

    instituicao_id = Column(Integer, ForeignKey("instituicoes.id"), nullable=True)
    instituicao = relationship("Instituicao", back_populates="cursos")


class Candidato(Base):
    __tablename__ = "candidatos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False, index=True)

    instituicao_id = Column(Integer, ForeignKey("instituicoes.id"), nullable=False)
    curso_codigo_dges = Column(Integer, nullable=False, index=True)

    instituicao = relationship("Instituicao", back_populates="candidatos")
