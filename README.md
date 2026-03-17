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

## Requisitos

- Python 3.10+
- Dependências em `requirements.txt`

## Instalação (Windows CMD)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> O ficheiro `.env.example` está incluído para futuras integrações com APIs externas.

## Como executar (Windows CMD)

```bash
set PYTHONPATH=src && python -m edu_multi_agent.main
```

Depois, introduza:
- tema,
- público-alvo,
- objetivos de aprendizagem (separados por `;`).

Em cada etapa de revisão humana, pode:
- **Aprovar** (`A`) e avançar,
- **Refazer com feedback** (`R`) e repetir a etapa do agente,
- **Editar manualmente** (`E`) e avançar com a versão editada.

## O que este MVP já entrega

- Estado partilhado do workflow.
- Agente principal responsável pela orquestração dos outros 3 agentes.
- 3 agentes especialistas com prompts/outputs iniciais simples (stubs).
- Grafo LangGraph com decisão centralizada no orquestrador e execução sequencial.
- Human-in-the-loop entre etapas com aprovar/refazer/editar.
- Interface CLI mínima para input e visualização de outputs intermédios/finais.

## Próximos passos sugeridos

1. Integrar LLM real por agente (mantendo o mesmo contrato de estado).
2. Persistir histórico de execução (ficheiro/DB).
3. Adicionar testes unitários dos nós e rotas do grafo.
4. Evoluir o gerador multimédia para formatos reais (slides, guião vídeo, quiz exportável).
