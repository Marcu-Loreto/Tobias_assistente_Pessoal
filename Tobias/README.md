# 🤖 Tobias — Assistente Pessoal de IA

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B.svg)](https://streamlit.io/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.1+-FF6B6B.svg)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Tobias é um assistente pessoal de IA crítico e assertivo, construído com arquitetura de agentes inteligentes. Ele combina múltiplos provedores de LLM, memória semântica vetorial e ferramentas especializadas para fornecer respostas de alta qualidade no estilo C-Level.

## ✨ Funcionalidades Principais

- **Assistente Inteligente** — Respostas diretas, factuais e fundamentadas em fontes
- **Pesquisa Web Avançada** — Busca aprofundada na internet com síntese de múltiplas fontes
- **Relatórios Executivos** — Geração de relatórios profissionais estilo C-Level com storytelling e visualização de dados
- **Calculadora Segura** — Cálculos matemáticos precisos para evitar alucinações numéricas
- **Validação de Dados** — Verificação de e-mails, CPFs e URLs
- **Análise de Segurança** — Detecção de senhas fracas e tentativas de prompt injection
- **Memória Híbrida** — Persistência conversacional (Redis) + busca semântica vetorial (Qdrant)
- **Roteamento Dinâmico de LLMs** — Seleção automática do melhor modelo baseado na complexidade da requisição
- **Processamento de Documentos** — Suporte a PDF, DOCX, XLSX, CSV e TXT

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit UI                             │
├─────────────────────────────────────────────────────────────────┤
│                     LangGraph Agent                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Detectar   │→ │   Verificar  │→ │   Router    │          │
│  │   Idioma     │  │   Admin      │  │   (Normal/  │          │
│  └──────────────┘  └──────────────┘  │   Maint.)    │          │
│                                      └──────┬───────┘          │
│                                            │                   │
│              ┌──────────────────────────────┴──────────────┐    │
│              │         Normal Mode (Tools + LLM)          │    │
│              │  ┌─────────┐    ┌─────────┐    ┌─────────┐  │    │
│              │  │  LLM    │───→│  Tools  │───→│  LLM    │  │    │
│              │  │ (OpenAI │    │ (Search,│    │         │  │    │
│              │  │ /Gemini)│    │ Calc,   │    │         │  │    │
│              │  └─────────┘    │ Valid.) │    └─────────┘  │    │
│              │                 └─────────┘                 │    │
│              └────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│                     Memory Layer                                │
│  ┌─────────────────────┐    ┌────────────────────────────────┐  │
│  │   Redis Memory      │    │      Qdrant Memory            │  │
│  │   (Conversacional)  │    │      (Vetorial/Semântica)    │  │
│  └─────────────────────┘    └────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Componentes Principais

| Componente | Descrição |
|------------|-----------|
| `main.py` | Interface Streamlit com gerenciamento de sessão |
| `core/graph.py` | Definição do grafo LangGraph com nodes e tools |
| `core/memory.py` | Sistema de memória dual (Redis + Qdrant) |
| `core/document_parser.py` | Extração de texto de múltiplos formatos |
| `app/router/model_selector.py` | Roteamento dinâmico de modelos |
| `app/clients/llm_client.py` | Fábrica de clientes LLM |
| `.agent/skills/` | Ferramentas especializadas do agente |

## 🚀 Quick Start

### Pré-requisitos

- Python 3.12+
- Redis (opcional, para memória conversacional)
- Qdrant (opcional, para memória vetorial)

### Instalação

```bash
# Clone o repositório
git clone <repo-url>
cd Tobias

# Instale as dependências
pip install uv
uv sync

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas chaves de API
```

### Executando Localmente

```bash
# Inicie o Redis (opcional)
redis-server

# Inicie o Qdrant (opcional)
docker run -p 6333:6333 qdrant/qdrant

# Execute a aplicação
uv run streamlit run main.py
```

Acesse: `http://localhost:8501`

### Executando com Docker

```bash
# Inicie todos os serviços
docker-compose up -d

# Acesse a aplicação
# http://localhost:8000
```

## ⚙️ Configuração

### Variáveis de Ambiente

| Variável | Descrição | Obrigatório |
|----------|-----------|--------------|
| `OPENAI_API_KEY` | Chave da API OpenAI | Sim |
| `GOOGLE_API_KEY` | Chave da API Google Gemini | Opcional |
| `REDIS_URL` | URL de conexão Redis | Opcional |
| `REDIS_TTL_SECONDS` | TTL das sessões no Redis (padrão: 3600) | Opcional |
| `QDRANT_URL` | URL do servidor Qdrant | Opcional |
| `QDRANT_COLLECTION` | Nome da collection (padrão: tobias_memory) | Opcional |
| `MODEL_OPENAI_STRONG` | Modelo forte OpenAI (padrão: gpt-4o) | Opcional |
| `MODEL_OPENAI_BALANCED` | Modelo balanceado OpenAI (padrão: gpt-4o-mini) | Opcional |
| `MODEL_GOOGLE_BALANCED` | Modelo Google (padrão: gemini-2.5-flash) | Opcional |
| `MODEL_GOOGLE_CHEAP` | Modelo Google econômico (padrão: gemini-2.5-flash-lite) | Opcional |

### Exemplo `.env`

```env
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
```

## 🔧 Desenvolvimento

### Estrutura do Projeto

```
Tobias/
├── main.py                      # Interface Streamlit
├── pyproject.toml               # Configurações do projeto
├── docker-compose.yml           # Orquestração de serviços
├── dockerfile                   # Container da aplicação
├── app/
│   ├── config/
│   │   └── models.py           # Definição de modelos LLM
│   ├── clients/
│   │   └── llm_client.py       # Fábrica de clientes LLM
│   └── router/
│       └── model_selector.py   # Roteamento dinâmico
├── core/
│   ├── graph.py                # Grafo LangGraph
│   ├── memory.py               # Sistema de memória
│   ├── document_parser.py      # Parser de documentos
│   └── utils.py                # Utilitários
├── .agent/
│   └── skills/                 # Ferramentas do agente
│       ├── search.py           # Pesquisa web
│       ├── calculator.py       # Calculadora
│       ├── validator.py        # Validador de dados
│       ├── security.py         # Análise de segurança
│       ├── relatorios/         # Skill de relatórios
│       └── pesquisa_web/       # Skill de pesquisa
└── prompts/
    └── agente.md               # Prompt de sistema
```

## 🛡️ Modo Administrador

O Tobias possui um modo de manutenção oculto para diagnóstico do sistema.

**Credenciais:**
- Usuário: `loreto`
- Token: `1423`

**Ativação:** Inclua "loreto" e "1423" em qualquer mensagem.

## 📝 Licença

MIT License — Veja o arquivo [LICENSE](LICENSE) para detalhes.

---

Desenvolvido com ❤️ usando LangGraph, Streamlit e múltiplos provedores de IA.
