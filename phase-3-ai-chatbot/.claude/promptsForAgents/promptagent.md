Spec-Kit Monorepo Folder Structure 
hackathon-todo/ 
├── .spec-kit/                    # Spec-Kit configuration 
│   └── config.yaml 
├── specs/                        # Spec-Kit managed specifications 
│   ├── overview.md               # Project overview 
│   ├── architecture.md           # System architecture 
│   ├── features/                 # Feature specifications 
│   │   ├── task-crud.md 
│   │   ├── authentication.md 
│   │   └── chatbot.md 
│   ├── api/                      # API specifications 
│   │   ├── rest-endpoints.md 
│   │   └── mcp-tools.md 
│   ├── database/                 # Database specifications 
│   │   └── schema.md 
│   └── ui/                       # UI specifications 
│       ├── components.md 
│       └── pages.md 
├── CLAUDE.md                     # Root Claude Code instructions 
├── frontend/ 
│   ├── CLAUDE.md 
│   └── ... (Next.js app) 
├── backend/ 
│   ├── CLAUDE.md 
│   └── ... (FastAPI app) 
├── docker-compose.yml 
└── README.md 