import requests
from bs4 import BeautifulSoup

from . import models
from .database import Base, SessionLocal, engine

Base.metadata.create_all(bind=engine)

URL_DGES = [
    "https://www.dges.gov.pt/guias/indest.asp?reg=11",
    "https://www.dges.gov.pt/guias/indest.asp?reg=12",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

session = requests.Session()
session.headers.update(HEADERS)


def scraping() -> None:
    db = SessionLocal()
    TIPOS = {
        "[Lic-1º cic]": "Licenciatura",
        "[Mest Integ]": "Mestrado Integrado",
        "[Prep. MI]": "Preparatórios de Mestrado Integrado",
        "[Prep lic 1 c]": "Preparatórios de Licenciatura",
    }

    inst_count = 0
    curso_count = 0

    try:
        for url in URL_DGES:
            print(f"A aceder a: {url}")
            resposta = session.get(url)

            if resposta.status_code != 200:
                print(f"Erro ao aceder ao site da DGES ({resposta.status_code})")
                continue

            soup = BeautifulSoup(resposta.text, "html.parser")
            print("A extrair dados...")

            # 1. Extrair Instituições
            inst_boxes = soup.select(".box9, .box9a")
            for box in inst_boxes:
                cod = box.find(class_="lin-area-c1")
                nom = box.find(class_="lin-area-d2")
                if cod and nom:
                    codigo = cod.getText().strip()
                    nome = nom.getText().strip()

                    if codigo.isdigit():
                        inst_type = (
                            "universidade pública"
                            if url == URL_DGES[0]
                            else "politécnico público"
                        )

                        inst_obj = models.Instituicao(
                            id=int(codigo), name=nome, type=inst_type
                        )
                        db.merge(inst_obj)
                        inst_count += 1
                        print(f"Guardada instituição: {codigo} - {nome}")

            cursos_rows = soup.select(".lin-ce")
            for elem in cursos_rows:
                cod = elem.find(class_="lin-ce-c2")
                nom = elem.find("a")
                tipo = elem.find_all(class_="lin-ce-c3")
                vag = elem.find(class_="lin-ce-c5")

                if cod and nom and len(tipo) > 1 and vag:
                    codigo = cod.getText().strip()
                    nome = nom.getText().strip()
                    vagas = vag.getText().strip()
                    tipo_key = tipo[1].getText().strip()
                    tipo_str = TIPOS.get(tipo_key, "Outro")

                    # Extrair ID da Instituição do atributo title="INST_ID/CURSO_ID"
                    inst_id: int | None = None
                    title_attr = nom.get("title")

                    # Type-guard para evitar erros de verificação do Pylance/Pyright
                    if isinstance(title_attr, str) and "/" in title_attr:
                        parts = title_attr.split("/")
                        if parts[0].isdigit():
                            inst_id = int(parts[0])

                    if codigo.isdigit() and vagas.isdigit():
                        curso_obj = models.Curso(
                            codigo_dges=int(codigo),
                            name=nome,
                            vagas=int(vagas),
                            type=tipo_str,
                            instituicao_id=inst_id,  # Associa a instituição ao curso
                        )
                        db.add(curso_obj)
                        curso_count += 1
                        print(f"Guardado curso: {codigo} - {nome} (Inst ID: {inst_id})")

        # Commit final na base de dados SQLite
        db.commit()
        print(
            f"\nSucesso! Guardadas {inst_count} instituições e "
            f"{curso_count} cursos na base de dados SQLite."
        )

    except Exception as e:
        db.rollback()
        print(f"Erro durante a gravação na base de dados: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    scraping()
