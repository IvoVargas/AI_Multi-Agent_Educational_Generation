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
    "brief": "Brief",
    "support": "Apoio",
    "visual": "Visual",
    "template": "Template",
    "other": "Outro",
}


def _bullet_list(items: List[str]) -> str:
    cleaned = [str(item).strip() for item in items if str(item).strip()]
    if not cleaned:
        return "- —"
    return "\n".join(f"- {item}" for item in cleaned)


def _kv_line(label: str, value: Any) -> str:
    text = str(value).strip() if value is not None else ""
    return f"**{label}:** {text or '—'}"


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


def _stage_flags(state: Dict[str, Any]) -> List[Dict[str, str]]:
    metadata = state.get("metadata", {})
    missing_fields = set(state.get("missing_fields", []) or [])
    content_analysis = bool(state.get("content_analysis"))
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
                <div class="big-value">{escape(str(state.get('current_step', '—') or '—'))}</div>
            </div>
            <div class="status-card compact">
                <div class="subtle-label">Estado</div>
                <div class="big-value">{escape(str(state.get('status', '—') or '—'))}</div>
            </div>
            <div class="status-card wide">
                <div class="subtle-label">Próxima ação</div>
                <div class="big-value">{escape(str(state.get('next_action', '—') or '—'))}</div>
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
        _kv_line("Fase atual", state.get("current_step", "—")),
        _kv_line("Estado", state.get("status", "—")),
        _kv_line("Próxima ação", state.get("next_action", "—")),
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


def render_structure_markdown(data: Dict[str, Any]) -> str:
    if not data:
        return "## Estrutura pedagógica\n\nAinda não foi gerada."

    sections_md = []
    for idx, section in enumerate(data.get("sections", []), start=1):
        sections_md.append("\n".join([
            f"### Secção {idx} — {section.get('section_title', '—')}",
            _kv_line("Objetivo", section.get("goal", "—")),
            f"**Tópicos:**\n{_bullet_list(section.get('topics', []))}",
        ]))

    slide_seq_md = []
    for slide in data.get("slide_sequence", []):
        slide_seq_md.append("\n".join([
            f"### Slide {slide.get('slide_number', '—')} — {slide.get('title', '—')}",
            _kv_line("Objetivo", slide.get("objective", "—")),
            f"**Pontos de conteúdo:**\n{_bullet_list(slide.get('content_points', []))}",
        ]))

    parts = [
        "## Estrutura pedagógica",
        _kv_line("Título da apresentação", data.get("presentation_title", "—")),
        f"**Objetivos de aprendizagem:**\n{_bullet_list(data.get('learning_objectives', []))}",
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
        blocks.append("\n".join([
            f"### Slide {slide.get('slide_number', '—')} — {slide.get('title', '—')}",
            _kv_line("Tipo", slide.get("kind", "content")),
            f"**Pontos principais:**\n{_bullet_list(slide.get('bullets', []))}",
            _kv_line("Notas do apresentador", slide.get("speaker_notes", "—")),
            _kv_line("Descrição visual", slide.get("visual_description", "—")),
            _kv_line("Imagem gerada", slide.get("image_path", "—") or "—"),
        ]))
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
