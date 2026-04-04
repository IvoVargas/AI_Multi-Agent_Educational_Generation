from __future__ import annotations

from typing import Any, Dict, List


def _escape_md(text: Any) -> str:
    value = "" if text is None else str(text)
    return value.replace("\n", "  \n")


def _bullet_list(items: List[Any]) -> str:
    cleaned = [str(item).strip() for item in (items or []) if str(item).strip()]
    if not cleaned:
        return "- _Sem informação disponível._"
    return "\n".join(f"- { _escape_md(item) }" for item in cleaned)


def format_status(message: str) -> str:
    message = (message or "Sem estado disponível.").strip()
    return f"## Estado do processo\n\n{_escape_md(message)}"


def format_orchestrator_message(message: str) -> str:
    message = (message or "Ainda sem mensagens do orquestrador.").strip()
    return f"## Mensagem do orquestrador\n\n{_escape_md(message)}"



def format_content_analysis(data: Dict[str, Any]) -> str:
    if not data:
        return "## Análise conceptual\n\n_A análise ainda não foi gerada._"

    parts = [
        "## Análise conceptual",
        "",
        f"### Tema\n{_escape_md(data.get('theme', '—'))}",
        "",
        f"### Resumo\n{_escape_md(data.get('summary', '—'))}",
        "",
        f"### Conceitos-chave\n{_bullet_list(data.get('key_concepts', []))}",
        "",
        f"### Tópicos principais\n{_bullet_list(data.get('main_topics', []))}",
        "",
        f"### Pré-requisitos\n{_bullet_list(data.get('prerequisites', []))}",
        "",
        f"### Possíveis dificuldades\n{_bullet_list(data.get('possible_difficulties', []))}",
    ]
    return "\n".join(parts)



def format_pedagogical_structure(data: Dict[str, Any]) -> str:
    if not data:
        return "## Estrutura pedagógica\n\n_A estrutura ainda não foi gerada._"

    parts = [
        "## Estrutura pedagógica",
        "",
        f"### Título da apresentação\n{_escape_md(data.get('presentation_title', '—'))}",
        "",
        f"### Objetivos de aprendizagem\n{_bullet_list(data.get('learning_objectives', []))}",
        "",
        "### Secções",
    ]

    sections = data.get("sections", []) or []
    if not sections:
        parts.append("_Sem secções definidas._")
    else:
        for idx, section in enumerate(sections, start=1):
            parts.extend(
                [
                    "",
                    f"**{idx}. { _escape_md(section.get('section_title', 'Secção')) }**",
                    "",
                    f"Objetivo: { _escape_md(section.get('goal', '—')) }",
                    "",
                    _bullet_list(section.get("topics", [])),
                ]
            )

    parts.extend(["", "### Sequência de slides"])
    sequence = data.get("slide_sequence", []) or []
    if not sequence:
        parts.append("_Sem sequência de slides definida._")
    else:
        for item in sequence:
            parts.extend(
                [
                    "",
                    f"**Slide {item.get('slide_number', '—')} — { _escape_md(item.get('title', 'Sem título')) }**",
                    "",
                    f"Objetivo: { _escape_md(item.get('objective', '—')) }",
                    "",
                    _bullet_list(item.get("content_points", [])),
                ]
            )

    return "\n".join(parts)



def format_slide_plan(slides: List[Dict[str, Any]]) -> str:
    if not slides:
        return "## Plano de slides\n\n_O plano de slides ainda não foi gerado._"

    parts = ["## Plano de slides"]

    for slide in slides:
        kind = slide.get("kind", "content")
        parts.extend(
            [
                "",
                f"### Slide {slide.get('slide_number', '—')} — { _escape_md(slide.get('title', 'Sem título')) }",
                "",
                f"**Tipo:** { _escape_md(kind) }",
                "",
                "**Pontos principais**",
                "",
                _bullet_list(slide.get("bullets", [])),
                "",
                f"**Notas do apresentador**  \n{_escape_md(slide.get('speaker_notes', '—'))}",
                "",
                f"**Descrição visual**  \n{_escape_md(slide.get('visual_description', '—'))}",
            ]
        )

        image_path = str(slide.get("image_path", "")).strip()
        if image_path:
            parts.extend(["", f"**Imagem gerada:** `{image_path}`"])

    return "\n".join(parts)
