from pydantic import BaseModel


class CursoBase(BaseModel):
    id: int
    name: str
    vagas: int
    type: str
    instituicao_id: int | None = None

    class Config:
        from_attributes = True


class InstituicaoBase(BaseModel):
    id: int
    name: str
    type: str

    class Config:
        from_attributes = True


class InstituicaoWithCursos(InstituicaoBase):
    cursos: list[CursoBase] = []


class CandidatoBase(BaseModel):
    id: int
    nome: str
    instituicao_id: int
    curso_codigo_dges: int

    class Config:
        from_attributes = True
