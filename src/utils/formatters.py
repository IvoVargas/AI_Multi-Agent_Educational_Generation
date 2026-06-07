from __future__ import annotations

from html import escape
from typing import Any, Dict, List


FIELD_LABELS = {
    "text_base": "texto-base",
    "title": "título",
    "target_audience": "público-alvo",
    "education_level": "nível de ensino",
    "presentation_goal": "objetivo da apresentação",
    "num_slides": "número de slides",
    "language": "idioma",
}

REQUIRED_METADATA_FIELDS = [
    "title",
    "target_audience",
    "education_level",
    "presentation_goal",
    "num_slides",
    "language",
]

ROLE_LABELS = {
    "brief": "Documento de requisitos",
    "support": "Documento de apoio",
    "visual": "Referência visual",
    "template": "Modelo",
    "other": "Outro",
}

SOLO_LABELS = {
    "SOLO_2": "SOLO 2 — Uniestrutural",
    "SOLO_3": "SOLO 3 — Multiestrutural",
    "SOLO_4": "SOLO 4 — Relacional",
    "SOLO_5": "SOLO 5 — Abstrato alargado",
}

OUTCOME_TYPE_LABELS = {
    "conhecimento_teorico": "Conhecimento teórico",
    "competencia_pratica_tecnica": "Competência prática/técnica",
    "competencia_social": "Competência social",
}

IMPORTANCE_LABELS = {
    "principal": "Principal",
    "secundario": "Secundário",
}

SLIDE_KIND_LABELS = {
    "title": "Título",
    "content": "Conteúdo",
    "closing": "Encerramento",
}

CURRENT_STEP_LABELS = {
    "input": "Entrada de dados",
    "orchestration": "Orquestração",
    "content_analysis": "Análise conceptual",
    "pedagogical_design": "Desenho pedagógico",
    "multimedia_generation": "Geração multimédia",
    "export": "Exportação",
}

STATUS_LABELS = {
    "initialized": "Inicializado",
    "awaiting_input": "A aguardar intervenção do utilizador",
    "ready_to_continue": "Pronto para continuar",
    "analysis_completed": "Análise conceptual concluída",
    "solo_structure_completed": "Resultados SOLO e estrutura pedagógica concluídos",
    "slides_completed": "Plano de slides concluído",
    "completed": "Concluído",
    "ingested": "Ficheiro processado",
}

NEXT_ACTION_LABELS = {
    "ask_user": "Recolher requisitos",
    "run_content_analysis": "Gerar análise conceptual",
    "wait_analysis_approval": "Aguardar aprovação da análise",
    "run_pedagogical_design": "Gerar resultados SOLO e estrutura pedagógica",
    "wait_structure_approval": "Aguardar aprovação dos resultados SOLO e da estrutura pedagógica",
    "run_multimedia_generation": "Gerar plano multimédia",
    "export_pptx": "Exportar PowerPoint",
    "completed": "Processo concluído",
}


def _label_from(mapping: Dict[str, str], value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return "—"
    return mapping.get(text, text.replace("_", " "))


def _bullet_list(items: List[str]) -> str:
    cleaned = [str(item).strip() for item in items if str(item).strip()]
    if not cleaned:
        return "- —"
    return "\n".join(f"- {item}" for item in cleaned)


def _kv_line(label: str, value: Any) -> str:
    text = str(value).strip() if value is not None else ""
    return f"**{label}:** {text or '—'}"


def _structure_field_line(label: str, value: Any) -> str:
    """Format structure fields with a Markdown hard line break.

    This prevents Gradio/Markdown from collapsing consecutive metadata
    fields into a single paragraph in the Estrutura tab.
    """
    text = str(value).strip() if value is not None else ""
    return f"**{label}:** {text or '—'}  "


def _slide_field_line(label: str, value: Any) -> str:
    """Format slide metadata with a Markdown hard line break.

    The Slides tab contains several consecutive metadata fields. The two
    trailing spaces keep each field on its own line in Gradio/Markdown.
    Multiline fields, such as presenter notes, keep their internal line
    breaks instead of being collapsed into one paragraph.
    """
    text = str(value).strip() if value is not None else ""
    if not text:
        return f"**{label}:** —  "
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "  \n".join(part.strip() for part in text.split("\n"))
    return f"**{label}:** {text}  "


def _metadata_chip(label: str, value: Any, dim: bool = False) -> str:
    safe_label = escape(label)
    safe_value = escape(str(value).strip()) if value is not None and str(value).strip() else "—"
    css_class = "status-chip muted" if dim else "status-chip"
    return (
        f'<span class="{css_class}">'
        f'<span class="chip-label">{safe_label}</span>'
        f'<span class="chip-value">{safe_value}</span>'
        f"</span>"
    )


def _source_chip(label: str, value: str) -> str:
    return (
        '<span class="status-chip source-chip">'
        f'<span class="chip-label">{escape(label)}</span>'
        f'<span class="chip-value">{escape(value)}</span>'
        '</span>'
    )


def _get_solo_outcomes(state_or_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
    outcomes = state_or_structure.get("solo_learning_outcomes", []) or []
    if not outcomes and state_or_structure.get("pedagogical_structure"):
        outcomes = state_or_structure.get("pedagogical_structure", {}).get("solo_learning_outcomes", []) or []
    return outcomes


def _stage_flags(state: Dict[str, Any]) -> List[Dict[str, str]]:
    metadata = state.get("metadata", {})
    missing_fields = set(state.get("missing_fields", []) or [])
    content_analysis = bool(state.get("content_analysis"))
    solo_outcomes = bool(_get_solo_outcomes(state))
    pedagogical_structure = bool(state.get("pedagogical_structure"))
    slide_plan = bool(state.get("slide_plan"))
    presentation_path = bool(state.get("presentation_path"))
    next_action = state.get("next_action", "")

    requirements_complete = bool(state.get("user_input", "").strip()) and all(
        str(metadata.get(field, "")).strip() and field not in missing_fields for field in REQUIRED_METADATA_FIELDS
    )
    if not state.get("user_input", "").strip() and any(
        item.get("role") in {"brief", "support", "template"} for item in state.get("uploaded_files", [])
    ):
        requirements_complete = all(
            str(metadata.get(field, "")).strip() and field not in missing_fields for field in REQUIRED_METADATA_FIELDS
        )

    return [
        {"id": "status", "label": "Requisitos", "state": "complete" if requirements_complete else "active" if next_action == "ask_user" else "pending"},
        {"id": "analysis", "label": "Análise", "state": "complete" if content_analysis else "active" if next_action in {"run_content_analysis", "wait_analysis_approval"} else "pending"},
        {"id": "solo", "label": "SOLO", "state": "complete" if solo_outcomes else "active" if next_action in {"run_pedagogical_design", "wait_structure_approval"} else "pending"},
        {"id": "structure", "label": "Estrutura", "state": "complete" if pedagogical_structure else "active" if next_action in {"run_pedagogical_design", "wait_structure_approval"} else "pending"},
        {"id": "slides", "label": "Slides", "state": "complete" if slide_plan else "active" if next_action in {"run_multimedia_generation"} else "pending"},
        {"id": "export", "label": "Exportação", "state": "complete" if presentation_path else "active" if next_action in {"export_pptx", "completed"} else "pending"},
    ]


def _render_source_summary(state: Dict[str, Any]) -> str:
    uploaded_files = state.get("uploaded_files", []) or []
    if not uploaded_files:
        return '<div class="big-value">Sem ficheiros anexados.</div>'

    role_counts: Dict[str, int] = {}
    for item in uploaded_files:
        role = str(item.get("role", "other"))
        role_counts[role] = role_counts.get(role, 0) + 1

    chips = [
        _source_chip(ROLE_LABELS.get(role, role.title()), f"{count} ficheiro(s)")
        for role, count in sorted(role_counts.items())
    ]

    items = []
    for item in uploaded_files[:8]:
        label = ROLE_LABELS.get(str(item.get("role", "other")), "Outro")
        summary = str(item.get("summary", "")).strip() or "Sem resumo disponível."
        items.append(
            f'<div class="source-item"><div class="source-name">{escape(str(item.get("name", "ficheiro")))}</div>'
            f'<div class="source-meta">{escape(label)} · {escape(summary[:180])}</div></div>'
        )
    return '<div class="chip-row">' + ''.join(chips) + '</div><div class="source-list">' + ''.join(items) + '</div>'


def render_status_html(state: Dict[str, Any]) -> str:
    metadata = state.get("metadata", {})
    missing_fields = state.get("missing_fields", []) or []
    stages = _stage_flags(state)

    stage_blocks = []
    for idx, stage in enumerate(stages, start=1):
        connector = '<div class="progress-connector"></div>' if idx < len(stages) else ""
        stage_blocks.append(
            f'<div class="progress-step {stage["state"]}"><div class="step-dot">{idx}</div><div class="step-label">{escape(stage["label"])}</div></div>{connector}'
        )

    chips = [
        _metadata_chip("Título", metadata.get("title"), dim=not metadata.get("title")),
        _metadata_chip("Público-alvo", metadata.get("target_audience"), dim=not metadata.get("target_audience")),
        _metadata_chip("Nível", metadata.get("education_level"), dim=not metadata.get("education_level")),
        _metadata_chip("Objetivo", metadata.get("presentation_goal"), dim=not metadata.get("presentation_goal")),
        _metadata_chip("Slides", metadata.get("num_slides"), dim=not metadata.get("num_slides")),
        _metadata_chip("Idioma", metadata.get("language"), dim=not metadata.get("language")),
    ]

    extra = str(metadata.get("extra_instructions", "")).strip()
    if extra:
        chips.append(_metadata_chip("Instruções", extra))

    missing_html = ""
    if missing_fields:
        badges = "".join(f'<span class="missing-chip">{escape(FIELD_LABELS.get(field, field))}</span>' for field in missing_fields)
        missing_html = f'<div class="missing-wrap"><div class="subtle-label">Em falta</div><div class="chip-row">{badges}</div></div>'

    return f"""
    <div class="status-root">
        <div class="status-section">
            <div class="section-title">Progresso</div>
            <div class="progress-track">{''.join(stage_blocks)}</div>
        </div>

        <div class="status-grid">
            <div class="status-card compact">
                <div class="subtle-label">Fase atual</div>
                <div class="big-value">{escape(_label_from(CURRENT_STEP_LABELS, state.get('current_step')))}</div>
            </div>
            <div class="status-card compact">
                <div class="subtle-label">Estado</div>
                <div class="big-value">{escape(_label_from(STATUS_LABELS, state.get('status')))}</div>
            </div>
            <div class="status-card wide">
                <div class="subtle-label">Próxima ação</div>
                <div class="big-value">{escape(_label_from(NEXT_ACTION_LABELS, state.get('next_action')))}</div>
            </div>
        </div>

        <div class="status-section">
            <div class="section-title">Metadados recolhidos</div>
            <div class="chip-row">{''.join(chips)}</div>
        </div>

        {missing_html}

        <div class="status-section">
            <div class="section-title">Fontes anexadas</div>
            {_render_source_summary(state)}
        </div>
    </div>
    """.strip()


def render_status_markdown(state: Dict[str, Any]) -> str:
    metadata = state.get("metadata", {})
    missing_fields = state.get("missing_fields", []) or []
    lines = [
        "## Estado do processo",
        _kv_line("Fase atual", _label_from(CURRENT_STEP_LABELS, state.get("current_step"))),
        _kv_line("Estado", _label_from(STATUS_LABELS, state.get("status"))),
        _kv_line("Próxima ação", _label_from(NEXT_ACTION_LABELS, state.get("next_action"))),
        _kv_line("Fontes", state.get("source_summary", "Sem ficheiros anexados.")),
    ]
    if missing_fields:
        readable = ", ".join(FIELD_LABELS.get(field, field) for field in missing_fields)
        lines.append(_kv_line("Em falta", readable))
    lines.extend([
        "\n## Metadados recolhidos",
        _kv_line("Título", metadata.get("title", "—")),
        _kv_line("Público-alvo", metadata.get("target_audience", "—")),
        _kv_line("Nível de ensino", metadata.get("education_level", "—")),
        _kv_line("Objetivo", metadata.get("presentation_goal", "—")),
        _kv_line("N.º de slides", metadata.get("num_slides", "—")),
        _kv_line("Idioma", metadata.get("language", "—")),
    ])
    extra = str(metadata.get("extra_instructions", "")).strip()
    if extra:
        lines.append(_kv_line("Instruções adicionais", extra))
    return "\n\n".join(lines)


def _source_note(source_documents: List[str]) -> str:
    if not source_documents:
        return ""
    return f"\n\n**Fontes usadas:** {', '.join(source_documents)}"


def render_analysis_markdown(data: Dict[str, Any]) -> str:
    if not data:
        return "## Análise conceptual\n\nAinda não foi gerada."
    return "\n\n".join([
        "## Análise conceptual",
        _kv_line("Tema", data.get("theme", "—")),
        f"**Resumo:**\n{data.get('summary', '—')}",
        f"**Conceitos-chave:**\n{_bullet_list(data.get('key_concepts', []))}",
        f"**Tópicos principais:**\n{_bullet_list(data.get('main_topics', []))}",
        f"**Pré-requisitos:**\n{_bullet_list(data.get('prerequisites', []))}",
        f"**Possíveis dificuldades:**\n{_bullet_list(data.get('possible_difficulties', []))}",
        _source_note(data.get("source_documents", [])),
    ]).strip()


def _solo_field_line(label: str, value: Any) -> str:
    """Format SOLO fields with a Markdown hard line break.

    Gradio/Markdown collapses single newlines inside the same paragraph.
    The two trailing spaces force each SOLO field to appear on its own line
    without adding excessive blank spacing between fields.
    """
    text = str(value).strip() if value is not None else ""
    return f"**{label}:** {text or '—'}  "


def _format_solo_outcome(outcome: Dict[str, Any]) -> str:
    outcome_id = outcome.get("id", "—")
    solo_level = SOLO_LABELS.get(outcome.get("solo_level"), outcome.get("solo_level", "—"))
    outcome_type = OUTCOME_TYPE_LABELS.get(outcome.get("outcome_type"), outcome.get("outcome_type", "—"))
    importance = IMPORTANCE_LABELS.get(outcome.get("importance"), outcome.get("importance", "—"))
    verb = outcome.get("action_verb", "—")
    description = outcome.get("description", "—")
    related_topics = outcome.get("related_topics", [])
    learning_activity = outcome.get("suggested_learning_activity", "")
    assessment = outcome.get("suggested_assessment", "")

    lines = [
        f"### RA{outcome_id} — {solo_level}",
        _solo_field_line("Tipo", outcome_type),
        _solo_field_line("Importância", importance),
        _solo_field_line("Verbo", verb),
        _solo_field_line("Descrição", description),
        "**Conteúdos/tópicos relacionados:**",
        _bullet_list(related_topics),
    ]
    if learning_activity or assessment:
        lines.append("")
    if learning_activity:
        lines.append(_solo_field_line("Atividade de ensino sugerida", learning_activity))
    if assessment:
        lines.append(_solo_field_line("Avaliação sugerida", assessment))
    return "\n".join(lines)


def render_solo_markdown(state_or_structure: Dict[str, Any]) -> str:
    outcomes = _get_solo_outcomes(state_or_structure)
    if not outcomes:
        return "## Resultados de aprendizagem SOLO\n\nAinda não foram gerados."

    blocks = [
        "## Resultados de aprendizagem SOLO",
        "Estes resultados funcionam como a camada pedagógica intermédia antes da geração dos conteúdos multimédia. O nível SOLO_1 não é usado porque não representa um resultado observável adequado.",
    ]
    blocks.extend(_format_solo_outcome(outcome) for outcome in outcomes)
    return "\n\n".join(blocks)


def render_structure_markdown(data: Dict[str, Any]) -> str:
    if not data:
        return "## Estrutura pedagógica\n\nAinda não foi gerada."

    sections_md = []
    for idx, section in enumerate(data.get("sections", []), start=1):
        sections_md.append("\n".join([
            f"### Secção {idx} — {section.get('section_title', '—')}",
            _structure_field_line("Objetivo", section.get("goal", "—")),
            "**Tópicos:**",
            _bullet_list(section.get("topics", [])),
        ]))

    slide_seq_md = []
    for slide in data.get("slide_sequence", []):
        outcome_ids = slide.get("learning_outcome_ids", []) or []
        outcome_label = ", ".join(f"RA{oid}" for oid in outcome_ids) if outcome_ids else "—"
        solo_label = SOLO_LABELS.get(slide.get("solo_level"), slide.get("solo_level", "—"))
        slide_seq_md.append("\n".join([
            f"### Slide {slide.get('slide_number', '—')} — {slide.get('title', '—')}",
            _structure_field_line("Objetivo", slide.get("objective", "—")),
            _structure_field_line("Resultados SOLO associados", outcome_label),
            _structure_field_line("Nível SOLO dominante", solo_label),
            "**Pontos de conteúdo:**",
            _bullet_list(slide.get("content_points", [])),
        ]))

    parts = [
        "## Estrutura pedagógica",
        _kv_line("Título da apresentação", data.get("presentation_title", "—")),
        f"**Objetivos de aprendizagem textuais:**\n{_bullet_list(data.get('learning_objectives', []))}",
        "## Secções",
        "\n\n".join(sections_md) if sections_md else "Ainda sem secções.",
        "## Sequência de slides",
        "\n\n".join(slide_seq_md) if slide_seq_md else "Ainda sem sequência de slides.",
        _source_note(data.get("source_documents", [])),
    ]
    return "\n\n".join(part for part in parts if str(part).strip())


def render_slide_plan_markdown(slide_plan: List[Dict[str, Any]]) -> str:
    if not slide_plan:
        return "## Plano de slides\n\nAinda não foi gerado."

    blocks = ["## Plano de slides"]
    source_documents = []
    for slide in slide_plan:
        source_documents.extend(slide.get("source_documents", []))
        outcome_ids = slide.get("learning_outcome_ids", []) or []
        outcome_label = ", ".join(f"RA{oid}" for oid in outcome_ids) if outcome_ids else "—"
        solo_label = SOLO_LABELS.get(slide.get("solo_level"), slide.get("solo_level", "—"))
        kind_label = SLIDE_KIND_LABELS.get(slide.get("kind", "content"), slide.get("kind", "content"))
        block = [
            f"### Slide {slide.get('slide_number', '—')} — {slide.get('title', '—')}",
            _slide_field_line("Tipo", kind_label),
            _slide_field_line("Resultados SOLO associados", outcome_label),
            _slide_field_line("Nível SOLO", solo_label),
        ]
        if slide.get("learning_outcome_summary"):
            block.append(_slide_field_line("Resumo do alinhamento", slide.get("learning_outcome_summary")))
        block.extend([
            "**Pontos principais:**",
            _bullet_list(slide.get("bullets", [])),
            "",
            _slide_field_line("Notas do apresentador", slide.get("speaker_notes", "—")),
            _slide_field_line("Descrição visual", slide.get("visual_description", "—")),
            _slide_field_line("Imagem gerada", slide.get("image_path", "—") or "—"),
        ])
        blocks.append("\n".join(block))
    unique_sources = list(dict.fromkeys(source_documents))
    if unique_sources:
        blocks.append(f"**Fontes visuais/factuais consideradas:** {', '.join(unique_sources)}")
    return "\n\n".join(blocks)


def render_analysis_preview_for_chat(data: Dict[str, Any]) -> str:
    if not data:
        return ""
    topics = data.get("main_topics", [])[:4]
    return "\n".join([
        "### Resumo da análise conceptual",
        _kv_line("Tema", data.get("theme", "—")),
        _kv_line("Tópicos principais", ", ".join(topics) if topics else "—"),
    ])


def render_solo_preview_for_chat(state_or_structure: Dict[str, Any]) -> str:
    outcomes = _get_solo_outcomes(state_or_structure)
    if not outcomes:
        return ""
    levels = [outcome.get("solo_level", "—") for outcome in outcomes]
    first = outcomes[0]
    return "\n".join([
        "### Resumo dos resultados SOLO",
        _kv_line("Total", len(outcomes)),
        _kv_line("Níveis usados", ", ".join(str(level) for level in dict.fromkeys(levels))),
        _kv_line("Primeiro resultado", f"RA{first.get('id', '—')} — {first.get('description', '—')}")
    ])


def render_structure_preview_for_chat(data: Dict[str, Any]) -> str:
    if not data:
        return ""
    objectives = data.get("learning_objectives", [])[:3]
    return "\n".join([
        "### Resumo da estrutura pedagógica",
        _kv_line("Título", data.get("presentation_title", "—")),
        _kv_line("Objetivos", ", ".join(objectives) if objectives else "—"),
        _kv_line("N.º de slides planeados", len(data.get("slide_sequence", []))),
    ])


def render_slide_plan_preview_for_chat(slide_plan: List[Dict[str, Any]]) -> str:
    if not slide_plan:
        return ""
    titles = [slide.get("title", "—") for slide in slide_plan[:5]]
    return "\n".join([
        "### Resumo do plano de slides",
        _kv_line("Total de slides no plano", len(slide_plan)),
        _kv_line("Primeiros títulos", ", ".join(titles)),
    ])
