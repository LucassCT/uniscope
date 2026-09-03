import time

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import Candidato, Curso, Instituicao

Base.metadata.create_all(bind=engine)

URL_COLOC = "https://dges.gov.pt/coloc/2026/col1listacol.asp"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

session = requests.Session()
session.headers.update(HEADERS)


def scrape_candidates_for_course(
    db: Session, cod_estab: int, cod_curso: int, cod_r: int
) -> int:
    payload = {
        "CodCurso": f"{cod_curso:04d}",
        "CodR": str(cod_r),
        "CodEstab": f"{cod_estab:04d}",
        "search": "Continuar",
    }

    try:
        response = session.post(URL_COLOC, data=payload, timeout=10)
        if response.status_code != 200:
            print(f"  ❌ Erro no pedido HTTP ({response.status_code})")
            return 0

        soup = BeautifulSoup(response.text, "html.parser")
        elements = soup.find_all("td", width="550")

        if not elements or len(elements) <= 1:
            return 0

        candidates_added = 0
        for n in elements[1:]:
            student_name = n.getText().strip()
            if student_name:
                candidato_obj = Candidato(
                    nome=student_name,
                    instituicao_id=cod_estab,
                    curso_codigo_dges=cod_curso,
                )
                db.add(candidato_obj)
                candidates_added += 1

        db.commit()
        return candidates_added

    except Exception as e:
        db.rollback()
        print(f"  ❌ Erro ao processar o curso {cod_curso}: {e}")
        return 0


def scrape_all_candidates() -> None:
    db = SessionLocal()

    try:
        cursos_com_inst = (
            db.query(Curso, Instituicao)
            .join(Instituicao, Curso.instituicao_id == Instituicao.id)
            .all()
        )

        total_courses = len(cursos_com_inst)
        print(
            f"🚀 A iniciar raspagem de {total_courses} cursos com zeros à esquerda (zfill)... \n"
        )

        total_candidates_saved = 0

        for index, (curso, instituicao) in enumerate(cursos_com_inst, start=1):
            estab_id = getattr(curso, "instituicao_id", None)
            curso_id = getattr(curso, "codigo_dges", None)
            inst_type = getattr(instituicao, "type", "").lower()

            if not estab_id or not curso_id:
                continue

            cod_r = 11 if "universidade" in inst_type else 12

            estab_id_str = f"{int(estab_id):04d}"
            curso_id_str = f"{int(curso_id):04d}"

            print(
                f"[{index}/{total_courses}] Curso {curso_id_str} ({curso.name}) "
                f"| Inst: {estab_id_str} -> CodR={cod_r}..."
            )

            count = scrape_candidates_for_course(
                db=db,
                cod_estab=int(estab_id),
                cod_curso=int(curso_id),
                cod_r=cod_r,
            )

            total_candidates_saved += count
            print(f"  └ Guardados {count} candidatos.")

            time.sleep(0.5)

        print(
            f"\n🎉 CONCLUÍDO! Guardados {total_candidates_saved} candidatos "
            f"no total ao longo de {total_courses} cursos."
        )

    finally:
        db.close()


if __name__ == "__main__":
    scrape_all_candidates()
