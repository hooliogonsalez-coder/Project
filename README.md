# Biometric Access System

Sistema biometricheskogo kontrola dostupa.

## Stack

- **Server:** FastAPI + PostgreSQL
- **Client:** CustomTkinter + OpenCV + InsightFace

## Struktura

```
biometric-access/
├── server/               # FastAPI backend
├── client/              # Desktop prilozhenie
└── docs/                # Dokumentatsiya
```

## Bystroe nachalo

### Server

```bash
cd server
pip install -r requirements.txt
cp .env.example .env
docker compose up -d
```

### Client

```bash
cd client
pip install -r requirements.txt
cp .env.example .env
python app/main.py
```

## Dokumentatsiya

- [Plan razrabotki](project_plan_biometric_access.md)