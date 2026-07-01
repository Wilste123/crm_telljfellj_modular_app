# CRM Telljfellj – modulær appstruktur

Dato skrevet: 30.06.2026  
Forfatter: William Berg Steffenak - copyright

Dette er en mer vanlig appstruktur for Streamlit CRM-et ditt. Målet er å splitte appen i logiske moduler slik at det blir enklere å feilsøke, forbedre ytelse og jobbe videre med layout.

## Struktur

```text
crm_telljfellj_modular_app/
├── app.py
├── requirements.txt
├── .streamlit/secrets.example.toml
├── src/crm/
│   ├── __init__.py
│   ├── auth.py
│   ├── config.py
│   ├── context.py
│   ├── data.py
│   ├── layout.py
│   ├── utils.py
│   ├── documents.py
│   └── pages/
│       ├── dashboard.py
│       ├── customers.py
│       ├── sales.py
│       ├── leads.py
│       ├── operations.py
│       ├── invoicing.py
│       └── courses.py
└── tests/
```

## Kjøring

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Secrets

Kopier `.streamlit/secrets.example.toml` til `.streamlit/secrets.toml` lokalt, og fyll inn verdier.

```toml
SUPABASE_URL = "..."
SUPABASE_KEY = "..."
DEV_MODE = false
DEV_LOGIN_EMAIL = ""
DEV_LOGIN_PASSWORD = ""
```

## Viktig

- Funksjonalitet er forsøkt beholdt fra app_v32_layout.py.
- Koden er nå delt opp i moduler for kunder, salg, drift, fakturering, kursing og dokumenter.
- Dokumentmodulen bruker `Last ned` i stedet for signed URL.
- `data.py` støtter både hel datahenting og områdebasert datahenting.
- Neste steg er å kjøre appen og feilsøke én modul av gangen.
