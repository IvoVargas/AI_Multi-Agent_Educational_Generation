# AI Multi-Agent Educational Generation (MVP)

Protótipo funcional de sistema **multi-agente** para apoiar docentes na geração de **plano de slides PowerPoint**.

## Objetivo do MVP

Este MVP implementa arquitetura com 4 agentes:
1. **Agente Principal (Orquestrador)**
2. **Analista de Conteúdo**
3. **Designer Pedagógico**
4. **Gerador de Slides PowerPoint**

A orquestração é feita com **LangGraph**.

## Arquitetura

```text
src/edu_multi_agent/
├── agents/
│   ├── orchestrator.py
│   ├── content_analyst.py
│   ├── instructional_designer.py
│   └── multimedia_generator.py
├── workflow/
│   └── graph.py
├── ui/
│   ├── cli.py
│   └── web.py
├── state.py
└── main.py
```

### Fluxo do grafo (LangGraph)

```text
START
  -> orchestrator (agente principal decide próximo passo)
  -> content_analyst
  -> review_content
  -> orchestrator
  -> instructional_designer
  -> review_design
  -> orchestrator
  -> multimedia_generator
  -> review_multimedia
  -> orchestrator
  -> END
```

## Interface Web (Gradio)

A aplicação agora usa **Gradio** em vez de interface de linha de comando.

Entradas:
- Tema
- Público-alvo
- Objetivos de aprendizagem (separados por `;`)
- Contexto adicional (texto livre)
- Upload de ficheiro `.txt` ou `.pdf` com material de referência

Saídas:
- Análise de conteúdo
- Proposta pedagógica
- Plano final de slides PowerPoint

## Requisitos

- Python 3.10+
- Dependências em `requirements.txt`

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Como executar

```bash
PYTHONPATH=src python -m edu_multi_agent.main
```

Depois abra o URL local exibido no terminal (normalmente `http://127.0.0.1:7860`).

## Notas do MVP

- O foco desta versão é **apenas** geração de plano de slides PowerPoint.
- O upload de PDF/TXT é usado como contexto para enriquecer os resultados.
- Os agentes ainda são stubs textuais para facilitar evolução futura.

## Próximos passos sugeridos

1. Integrar LLM real por agente.
2. Adicionar revisão humana etapa-a-etapa diretamente na UI web.
3. Gerar ficheiro `.pptx` real a partir do plano final.
4. Adicionar testes unitários para nós e rotas do grafo.
