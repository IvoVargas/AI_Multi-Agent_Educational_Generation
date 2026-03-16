# AI Multi-Agent Educational Generation (MVP)

<<<<<<< codex/create-mvp-for-multi-agent-educational-system-u3zt0x
Protótipo funcional de sistema **multi-agente** para apoiar docentes na geração de **plano de slides PowerPoint**.

## Objetivo do MVP

Este MVP implementa arquitetura com 4 agentes:
1. **Agente Principal (Orquestrador)**
2. **Analista de Conteúdo**
3. **Designer Pedagógico**
4. **Gerador de Slides PowerPoint**

A orquestração é feita com **LangGraph**.
=======
Protótipo funcional de um sistema **multi-agente** para apoiar docentes na criação de conteúdo educativo multimédia.

## Objetivo do MVP

Este MVP implementa uma arquitetura inicial com 4 agentes:
1. **Agente Principal (Orquestrador)**
2. **Analista de Conteúdo**
3. **Designer Pedagógico**
4. **Gerador Multimédia**

A orquestração é feita com **LangGraph**, incluindo **human-in-the-loop entre etapas** para revisão e aprovação antes de avançar no fluxo.
>>>>>>> main

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
<<<<<<< codex/create-mvp-for-multi-agent-educational-system-u3zt0x
│   ├── cli.py
│   └── web.py
=======
│   └── cli.py
>>>>>>> main
├── state.py
└── main.py
```

### Fluxo do grafo (LangGraph)

```text
START
  -> orchestrator (agente principal decide próximo passo)
  -> content_analyst
<<<<<<< codex/create-mvp-for-multi-agent-educational-system-u3zt0x
  -> review_content
  -> orchestrator
  -> instructional_designer
  -> review_design
  -> orchestrator
  -> multimedia_generator
  -> review_multimedia
=======
  -> review_content (humano: aprova | refaz | edita)
  -> orchestrator
  -> instructional_designer
  -> review_design (humano: aprova | refaz | edita)
  -> orchestrator
  -> multimedia_generator
  -> review_multimedia (humano: aprova | refaz | edita)
>>>>>>> main
  -> orchestrator
  -> END
```

<<<<<<< codex/create-mvp-for-multi-agent-educational-system-u3zt0x
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

=======
>>>>>>> main
## Requisitos

- Python 3.10+
- Dependências em `requirements.txt`

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

<<<<<<< codex/create-mvp-for-multi-agent-educational-system-u3zt0x
=======
> O ficheiro `.env.example` está incluído para futuras integrações com APIs externas.

>>>>>>> main
## Como executar

```bash
PYTHONPATH=src python -m edu_multi_agent.main
```

<<<<<<< codex/create-mvp-for-multi-agent-educational-system-u3zt0x
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
=======
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
>>>>>>> main
