# RoadInsight AI

**Course:** Datenbanken und Web-Techniken (DBW), TU Chemnitz  
**Topic:** Open Data Integration with Accidents in Germany  
**Stack:** PostgreSQL · FastAPI · React · Ollama (llama3)

---

## Architecture

```
User
 └─▶ React Frontend (port 5173)
       └─▶ FastAPI Backend (port 8000)
             ├─▶ Ollama / llama3 (natural language intent extraction)
             └─▶ PostgreSQL (roadinsight schema)
```

---

## Prerequisites

| Tool | Version |
|---|---|
| Python | 3.11+ |
| Node.js | 18+ |
| PostgreSQL | 14+ |
| Ollama | latest |

---

## Step 1 — Download Raw Data

Create a `data/raw/` folder and download the following files:

### Unfallatlas (Accident Point Data)
- **2022:** https://www.opengeodata.nrw.de/produkte/transport_verkehr/unfallatlas/Unfallorte2022_EPSG25832_CSV.zip
- **2023:** https://www.opengeodata.nrw.de/produkte/transport_verkehr/unfallatlas/Unfallorte2023_EPSG25832_CSV.zip
- **2024:** https://www.opengeodata.nrw.de/produkte/transport_verkehr/unfallatlas/Unfallorte2024_EPSG25832_CSV.zip

Extract and place the CSV files as:
```
data/raw/Unfallorte2022.csv
data/raw/Unfallorte2023.csv
data/raw/Unfallorte2024.csv
```

### Regional Statistics (Population)
- **population_by_kreis.csv** — https://www.regionalstatistik.de/genesis/online

### Municipality Reference (AGS/GV-ISys)
- **municipalities.xlsx** — https://www.destatis.de/DE/Themen/Laender-Regionen/Regionales/Gemeindeverzeichnis/

### Additional Raw Files (included in submission)
These are already included in `data/raw/`:
- `accident_per_10000_per_city.csv`
- `accident_statistics_by_kreis.csv`
- `accidents_with_persons_per_month.csv`

---

## Step 2 — Database Setup

```bash
psql -U postgres -c "CREATE DATABASE roadinsight;"
psql -U postgres -d roadinsight -f sql/schema.sql
```

---

## Step 3 — ETL Pipeline

Run in this order:

```bash
# Build processed files from raw data
python scripts/build_regions.py
python scripts/build_population.py
python scripts/build_accidents.py

# Validate before loading
python scripts/pre_etl_gate.py
python scripts/preload_validation.py

# Load into PostgreSQL
python scripts/load_to_postgres.py

# Validate after loading
python scripts/validate_final_outputs.py
python scripts/final_etl_validation.py
```

Expected row counts after successful load:
| Table | Rows |
|---|---|
| accidents | 794,059 |
| regions | 10,953 |
| population | 12,994 |
| official_rates | 400 |

---

## Step 4 — Backend Setup

```bash
cd backend

# Configure environment
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# Install dependencies
pip install -r ../requirements.txt

# Start API server
uvicorn app:app --reload --port 8000
```

API available at: http://localhost:8000  
Swagger docs: http://localhost:8000/docs

---

## Step 5 — Ollama Setup

```bash
# Install from https://ollama.com
ollama pull llama3
```

Ensure `OLLAMA_URL=http://localhost:11434` in your `.env`.

---

## Step 6 — Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend available at: http://localhost:5173

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/query` | Natural language question |
| GET | `/api/faqs` | Preset example questions |
| GET | `/api/stats` | Dashboard statistics |
| GET | `/health` | Health check |

**Example:**
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How many accidents occurred in Saxony in 2023?"}'
```

---

## Mandatory Test Questions

All answered via `POST /api/query`:

1. What is the earliest accident year in the complete dataset?
2. How many accidents involving personal injury occurred in Saxony in 2023?
3. From which year onwards is data available for North Rhine-Westphalia?
4. From which year onwards is data available for Mecklenburg-Western Pomerania?
5. How many accidents involving pedestrians occurred in Berlin in 2023?
6. Traffic accidents per 100,000 inhabitants in Saxony in 2023 (cross-source query)

---

## Data Sources & Licences

| Source | Data | Licence |
|---|---|---|
| Unfallatlas (opengeodata.nrw.de) | Accident point data 2022–2024 | Datenlizenz Deutschland – Namensnennung – 2.0 |
| Regionalstatistik / GENESIS | Population by district | dl-de/by-2-0 |
| GV-ISys (Destatis) | Official AGS region keys | dl-de/by-2-0 |
