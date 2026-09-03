# UniScope — DGES Candidate Search API & Data Scraper

UniScope is a Python backend that collects higher education placement lists from the Portuguese government portal (DGES), cleans up the raw HTML data and saves it into a SQL database, and makes it available through a FastAPI REST API.

---

## What It Does

* **Collects Data:** A scraper built with `requests` and `BeautifulSoup4` copies how DGES forms are submitted, formats course and institution IDs correctly, and reads candidate placement tables from the HTML.
* **Stores Data:** Uses SQLAlchemy ORM to connect candidates, institutions, and courses in a database.
* **Allows Frontend Access:** CORS is set up so web frontends can call this API from a different domain.

---

## Tech Stack

* **Language:** Python 3.11+
* **Framework:** FastAPI
* **ORM / Database:** SQLAlchemy (SQLite / PostgreSQL)
* **Web Scraping:** BeautifulSoup4, Requests
* **Validation & Schemas:** Pydantic
* **Server:** Uvicorn

---

## API Endpoints

### General

* **`GET /`** — Health check. Returns `"API WORKING!"`.

---

### Candidates

#### `GET /api/v1/candidatos/search`
Searches for candidate names, including their course and institution.

* **Query Parameters:**
  * `nome` *(string, required)*: Name to search for (at least 2 characters). Works with multi-word names (e.g. `Maria Silva`).
  * `limit` *(integer, optional)*: Max results to return. Default: `50`, Max: `200`.
* **Example Response:**
```json
[
  {
    "id": 1042,
    "nome": "Maria Silva",
    "instituicao_id": 1500,
    "instituicao_nome": "Universidade de Lisboa",
    "curso_codigo_dges": 9147,
    "curso_nome": "Engenharia Informática"
  }
]
```

---

### Institutions

#### `GET /api/v1/instituicoes`
Lists all institutions. Can be filtered by type.

* **Query Parameters:**
  * `type` *(string, optional)*: Filter by institution type (partial match works).
* **Example Response:**
```json
[
  {
    "id": 1500,
    "nome": "Universidade de Lisboa",
    "type": "Universidade Pública"
  }
]
```

#### `GET /api/v1/instituicoes/{inst_id}`
Returns one institution and its list of courses.

* **Path Parameters:**
  * `inst_id` *(integer, required)*: The institution's ID.
* **Errors:**
  * `404` — Institution not found.
* **Example Response:**
```json
{
  "id": 1500,
  "nome": "Universidade de Lisboa",
  "type": "Universidade Pública",
  "cursos": [
    {
      "id": 9147,
      "codigo_dges": 9147,
      "nome": "Engenharia Informática",
      "vagas": 120
    }
  ]
}
```

---

### Courses

#### `GET /api/v1/cursos`
Lists courses. Can be searched and filtered.

* **Query Parameters:**
  * `search` *(string, optional)*: Search term to match against course name.
  * `min_vagas` *(integer, optional)*: Only show courses with at least this many open spots. Default: `0`.
  * `type` *(string, optional)*: Filter by course type (partial match works).
* **Example Response:**
```json
[
  {
    "id": 9147,
    "codigo_dges": 9147,
    "nome": "Engenharia Informática",
    "vagas": 120,
    "type": "Licenciatura"
  }
]
```

#### `GET /api/v1/cursos/{curso_id}`
Returns one course by its ID.

* **Path Parameters:**
  * `curso_id` *(integer, required)*: The course's ID.
* **Errors:**
  * `404` — Course not found.
* **Example Response:**
```json
{
  "id": 9147,
  "codigo_dges": 9147,
  "nome": "Engenharia Informática",
  "vagas": 120,
  "type": "Licenciatura"
}
```
