fantauction/
├── pyproject.toml        # gestione dipendenze (Poetry)
├── .gitignore
├── src/
│   ├── fantauction/
│   │   ├── __init__.py
│   │   ├── domain/       # logica di dominio (entità, strategie, eventi)
│   │   │   ├── __init__.py
│   │   │   ├── auction.py
│   │   │   ├── team.py
│   │   │   ├── player.py
│   │   │   └── enums.py
│   │   ├── app/          # orchestratori e servizi applicativi
│   │   │   ├── __init__.py
│   │   │   └── auction_service.py
│   │   ├── infra/        # implementazioni tecniche (repo, db, ecc.)
│   │   │   ├── __init__.py
│   │   └── web/          # interfaccia HTTP e WebSocket
│   │       ├── __init__.py
│   │       ├── api.py
│   │       └── ws.py
│   └── main.py           # entrypoint FastAPI
└── tests/                # test unitari e di integrazione
    ├── __init__.py
    └── test_auction.py
