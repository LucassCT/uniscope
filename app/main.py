from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Candidato, Curso, Instituicao
from .schemas import (
    CursoBase,
    InstituicaoBase,
    InstituicaoWithCursos,
)

Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="DGES Higher Education Admissions API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return "API WORKING!"


@app.get("/api/v1/instituicoes", response_model=list[InstituicaoBase])
def get_instituicoes(
    type: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Instituicao)
    if type:
        query = query.filter(Instituicao.type.ilike(f"%{type}%"))
    return query.all()


@app.get("/api/v1/instituicoes/{inst_id}", response_model=InstituicaoWithCursos)
def get_instituicao(inst_id: int, db: Session = Depends(get_db)):
    inst = db.query(Instituicao).filter(Instituicao.id == inst_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Instituição não encontrada")
    return inst


@app.get("/api/v1/cursos", response_model=list[CursoBase])
def get_cursos(
    search: str | None = Query(None, description="Procurar por nome do curso"),
    min_vagas: int = Query(0, description="Filtrar por vagas mínimas"),
    type: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Curso)

    if search:
        query = query.filter(Curso.name.ilike(f"%{search}%"))
    if min_vagas > 0:
        query = query.filter(Curso.vagas >= min_vagas)
    if type:
        query = query.filter(Curso.type.ilike(f"%{type}%"))

    return query.all()


@app.get("/api/v1/cursos/{curso_id}", response_model=CursoBase)
def get_curso(curso_id: int, db: Session = Depends(get_db)):
    curso = db.query(Curso).filter(Curso.id == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    return curso


@app.get("/api/v1/candidatos/search")
def search_candidatos(
    nome: str = Query(..., min_length=2, description="Nome do candidato a pesquisar"),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    query = (
        db.query(
            Candidato.id,
            Candidato.nome,
            Candidato.instituicao_id,
            Instituicao.name.label("instituicao_nome"),
            Candidato.curso_codigo_dges,
            Curso.name.label("curso_nome"),
        )
        .distinct()
        .outerjoin(Instituicao, Candidato.instituicao_id == Instituicao.id)
        .outerjoin(
            Curso,
            (Candidato.curso_codigo_dges == Curso.codigo_dges)
            & (Candidato.instituicao_id == Curso.instituicao_id),
        )
    )

    keywords = [word.strip() for word in nome.split() if word.strip()]
    for keyword in keywords:
        query = query.filter(Candidato.nome.ilike(f"%{keyword}%"))

    results = query.limit(limit).all()

    return [
        {
            "id": r.id,
            "nome": r.nome,
            "instituicao_id": r.instituicao_id,
            "instituicao_nome": r.instituicao_nome or "Desconhecida",
            "curso_codigo_dges": r.curso_codigo_dges,
            "curso_nome": r.curso_nome or "Desconhecido",
        }
        for r in results
    ]
