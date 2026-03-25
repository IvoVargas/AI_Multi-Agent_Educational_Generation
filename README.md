# AI Multi-Agent Educational Generation (MVP)

Protótipo funcional de sistema **multi-agente** para apoiar docentes na geração de **plano de slides PowerPoint**.

## Objetivo do MVP (V1)

A primeira versão do protótipo deve ser capaz de:
1. **receber um texto-base e metadados pela interface Gradio**
2. **executar um fluxo LangGraph com três agentes**
3. **mostrar ao utilizador:**
   - análise conceptual;
   - estrutura pedagógica;
   - proposta final de slides;
4. **permitir validação/reformulação em dois pontos**
5. **gerar uma apresentação final em PowerPoint (.pptx)**
6. **incluir, por slide, uma descrição visual ou prompt de imagem.**

---
Nesta V1, a geração real de imagem pode ficar opcional. O essencial é garantir:
- fluxo funcional;
- estrutura coerente;
- exportação do PowerPoint.


## Decisão de objetivos para a V1

1. **O que a V1 faz:**
   - gera texto dos slides;
   - gera sugestões visuais por slide;
   - exporta ficheiro .pptx;
   - suporta reformulação após análise e após estrutura pedagógica.

2. **O que a V1 não precisa de fazer:**
   - autenticação;
   - base de dados;
   - histórico persistente;
   - geração avançada de design;
   - integração LMS;
   - geração obrigatória de imagens reais;
   - múltiplos utilizadores em simultâneo.


## Arquitetura

```text
edu_multi_agent/
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
├── LICENSE
├── README.md
│
├── src/
│   ├── config.py
│   ├── state.py
│   ├── graph.py
│   ├── models.py
│   │
│   ├── agents/
│   │   ├── content_analyst.py
│   │   ├── pedagogical_designer.py
│   │   └── multimedia_generator.py
│   │
│   ├── services/
│   │   ├── llm_service.py
│   │   ├── pptx_service.py
│   │   └── image_service.py
│   │
│   ├── ui/
│   │   └── gradio_ui.py
│   │
│   └── utils/
│       ├── formatters.py
│       ├── validators.py
│       └── logging_utils.py
│
├── outputs/
│   ├── presentations/
│   └── images/
│
└── tests/
    ├── test_state.py
    ├── test_agents.py
    └── test_graph.py
```

### Fluxo do grafo (LangGraph)

```text
START
  -> content_analysis_node
  -> analysis_review_node
      -> pedagogical_design_node        se aprovado
      -> content_analysis_node          se reformulação
  -> structure_review_node
      -> multimedia_generation_node     se aprovado
      -> pedagogical_design_node        se reformulação
  -> export_pptx_node
  -> END
```

## Interface Gradio

A interface com três zonas:
### Zona 1 — input
 - textbox do texto-base;
 - campos dos metadados;
 - botão “Iniciar geração”.
### Zona 2 — validações
 - mostrar análise conceptual;
 - botão “Aprovar análise”;
 - caixa “Feedback de reformulação”.
 - mostrar estrutura pedagógica;
 - botão “Aprovar estrutura”;
 - caixa “Feedback de reformulação”.
### Zona 3 — resultado final
 - pré-visualização textual dos slides;
 - botão de download do .pptx.


 ## Criar e ativar o ambiente virtual no Windows

No terminal, dentro da pasta do projeto:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Aceder à interface em `http://127.0.0.1:7860` para testar o protótipo.