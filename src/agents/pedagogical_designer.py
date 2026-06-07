from __future__ import annotations

from typing import Dict, List

from src.agents.file_intake import grounding_context_for_state
from src.models import PedagogicalStructureModel
from src.services.llm_service import LLMService
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)
llm = LLMService()


SOLO_LEVEL_HINTS = {
    "SOLO_2": "Uniestrutural: reconhecer, identificar ou descrever um aspeto isolado.",
    "SOLO_3": "Multiestrutural: enumerar, caracterizar ou comparar vários aspetos ainda pouco integrados.",
    "SOLO_4": "Relacional: explicar relações, integrar conceitos, justificar processos ou aplicar de forma contextualizada.",
    "SOLO_5": "Abstrato alargado: generalizar, formular hipóteses, criar, transferir ou avaliar em novos contextos.",
}


def _fallback_solo_outcomes(title: str, topics: List[str]) -> List[Dict]:
    clean_topics = [topic for topic in topics if str(topic).strip()] or [title]
    outcome_templates = [
        ("SOLO_2", "identificar", "conhecimento_teorico", "principal"),
        ("SOLO_3", "caracterizar", "conhecimento_teorico", "principal"),
        ("SOLO_4", "relacionar", "competencia_pratica_tecnica", "principal"),
        ("SOLO_5", "propor", "competencia_pratica_tecnica", "secundario"),
    ]

    outcomes: List[Dict] = []
    for idx, (level, verb, outcome_type, importance) in enumerate(outcome_templates, start=1):
        topic = clean_topics[min(idx - 1, len(clean_topics) - 1)]
        outcomes.append(
            {
                "id": idx,
                "outcome_type": outcome_type,
                "solo_level": level,
                "action_verb": verb,
                "description": f"{verb.capitalize()} {topic} no contexto de {title}.",
                "importance": importance,
                "related_topics": [topic],
                "suggested_learning_activity": f"Discussão orientada ou exercício curto sobre {topic}.",
                "suggested_assessment": f"Questão ou tarefa prática que evidencie a capacidade de {verb} {topic}.",
            }
        )
    return outcomes


def _fallback_structure(state: dict, source_names: list[str]) -> Dict:
    metadata = state.get("metadata", {})
    content_analysis = state.get("content_analysis", {})
    title = metadata.get("title", "").strip() or content_analysis.get("theme", "Apresentação")
    topics = content_analysis.get("main_topics", []) or ["introdução", "desenvolvimento", "síntese"]
    num_slides = int(metadata.get("num_slides", 6))
    solo_outcomes = _fallback_solo_outcomes(title, topics)

    slide_sequence = []
    outcome_count = max(1, len(solo_outcomes))
    for idx, topic in enumerate(topics[: max(1, num_slides - 2)], start=1):
        outcome = solo_outcomes[(idx - 1) % outcome_count]
        slide_sequence.append(
            {
                "slide_number": idx,
                "title": topic.capitalize(),
                "objective": f"Apresentar {topic} de acordo com o resultado de aprendizagem RA{outcome['id']}.",
                "content_points": [
                    f"Definir {topic}",
                    f"Explicar a relevância de {topic}",
                    f"Dar um exemplo relacionado com {topic}",
                ],
                "learning_outcome_ids": [outcome["id"]],
                "solo_level": outcome["solo_level"],
            }
        )

    return {
        "presentation_title": title,
        "solo_learning_outcomes": solo_outcomes,
        "learning_objectives": [
            outcome["description"] for outcome in solo_outcomes[: min(4, len(solo_outcomes))]
        ],
        "sections": [
            {
                "section_title": "Introdução",
                "goal": "Apresentar o tema e os conceitos base.",
                "topics": topics[:2],
            },
            {
                "section_title": "Desenvolvimento",
                "goal": "Explorar os tópicos principais com progressão SOLO.",
                "topics": topics[2:4] or topics[:2],
            },
            {
                "section_title": "Síntese e transferência",
                "goal": "Consolidar aprendizagens e promover aplicação em novos contextos.",
                "topics": topics[4:] or topics[-2:],
            },
        ],
        "slide_sequence": slide_sequence,
        "source_documents": source_names,
    }


def run_pedagogical_designer(state: dict) -> dict:
    logger.info("Pedagogical designer started")
    metadata = state.get("metadata", {})
    content_analysis = state.get("content_analysis", {})
    feedback = state.get("structure_feedback", "").strip()
    query = " ".join(
        str(part)
        for part in [content_analysis.get("theme", ""), " ".join(content_analysis.get("main_topics", [])), feedback]
        if str(part).strip()
    )
    grounding_context, source_names = grounding_context_for_state(state, query=query, top_n=5)

    system_prompt = """
És um Designer Pedagógico para um sistema de geração de apresentações educativas.
A tua primeira tarefa é formular resultados de aprendizagem usando a Taxonomia SOLO.
Só depois de formulares esses resultados é que deves propor a estrutura da apresentação e a sequência de slides.
Usa a análise conceptual como guia principal e os documentos anexados apenas como suporte factual e de estrutura.
Responde apenas com JSON válido.

Regras obrigatórias para Taxonomia SOLO:
- Não uses SOLO_1/pre-structural; esse nível não é adequado para resultados de aprendizagem.
- Usa apenas: SOLO_2, SOLO_3, SOLO_4 e SOLO_5.
- Cada resultado deve começar por um verbo de ação observável.
- Cada resultado deve ser avaliável e ligado a um ou mais tópicos/conteúdos.
- A progressão deve, sempre que fizer sentido, ir de níveis mais simples para níveis mais complexos.
- Alinha cada slide com pelo menos um resultado de aprendizagem através de learning_outcome_ids.

Guia de níveis:
- SOLO_2: uniestrutural; identificar, reconhecer, descrever um aspeto isolado.
- SOLO_3: multiestrutural; enumerar, caracterizar, comparar vários aspetos.
- SOLO_4: relacional; explicar relações, integrar conceitos, aplicar de forma contextualizada.
- SOLO_5: abstrato alargado; generalizar, criar, avaliar, transferir para novos contextos.

Estrutura obrigatória:
{
  "presentation_title": "string",
  "solo_learning_outcomes": [
    {
      "id": 1,
      "outcome_type": "conhecimento_teorico | competencia_pratica_tecnica | competencia_social",
      "solo_level": "SOLO_2 | SOLO_3 | SOLO_4 | SOLO_5",
      "action_verb": "string",
      "description": "string",
      "importance": "principal | secundario",
      "related_topics": ["string"],
      "suggested_learning_activity": "string",
      "suggested_assessment": "string"
    }
  ],
  "learning_objectives": ["string"],
  "sections": [
    {
      "section_title": "string",
      "goal": "string",
      "topics": ["string"]
    }
  ],
  "slide_sequence": [
    {
      "slide_number": 1,
      "title": "string",
      "objective": "string",
      "content_points": ["string"],
      "learning_outcome_ids": [1],
      "solo_level": "SOLO_2 | SOLO_3 | SOLO_4 | SOLO_5"
    }
  ]
}
"""

    user_prompt = f"""
Análise conceptual:
{content_analysis}

Metadados:
{metadata}

Número pretendido de slides de conteúdo, excluindo capa e conclusão se aplicável:
{metadata.get('num_slides', 6)}

Fontes de apoio:
{grounding_context or 'Sem fontes adicionais.'}

Feedback anterior:
{feedback if feedback else 'Sem feedback anterior.'}

Taxonomia SOLO disponível:
{SOLO_LEVEL_HINTS}
"""

    try:
        pedagogical_structure = llm.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema=PedagogicalStructureModel,
        )
        pedagogical_structure["source_documents"] = source_names
    except Exception:
        logger.exception("Pedagogical designer failed. Using fallback.")
        pedagogical_structure = _fallback_structure(state, source_names)

    solo_learning_outcomes = pedagogical_structure.get("solo_learning_outcomes", [])

    logger.info("Pedagogical designer completed with %s SOLO outcomes", len(solo_learning_outcomes))
    return {
        "pedagogical_structure": pedagogical_structure,
        "solo_learning_outcomes": solo_learning_outcomes,
        "structure_approved": False,
        "slide_plan": [],
        "presentation_path": "",
        "current_step": "pedagogical_design",
        "status": "solo_structure_completed",
        "error_message": "",
    }
