from __future__ import annotations

import re
from typing import Dict, List

from src.agents.file_intake import grounding_context_for_state
from src.models import SlidePlanItemModel
from src.services.image_service import ImageService
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)
image_service = ImageService()


def _slugify(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", text).strip("_").lower() or "slide"


def _image_size_for_kind(kind: str) -> str:
    if kind == "title":
        return "1536x1024"
    return "1024x1536"


def _visual_asset_paths(state: dict) -> List[str]:
    return [item.get("path") for item in state.get("uploaded_files", []) if item.get("role") == "visual" and item.get("path")]


def _template_names(state: dict) -> List[str]:
    return [item.get("name") for item in state.get("uploaded_files", []) if item.get("role") == "template"]


def _compose_visual_description(base_text: str, source_names: List[str]) -> str:
    if not source_names:
        return base_text
    return f"{base_text} Referências disponíveis: {', '.join(source_names[:3])}."


def _outcome_map(pedagogical_structure: Dict, state: dict) -> Dict[int, Dict]:
    outcomes = pedagogical_structure.get("solo_learning_outcomes") or state.get("solo_learning_outcomes", []) or []
    mapped: Dict[int, Dict] = {}
    for outcome in outcomes:
        try:
            mapped[int(outcome.get("id"))] = outcome
        except Exception:
            continue
    return mapped


def _outcome_summary(outcome_ids: List[int], outcomes_by_id: Dict[int, Dict]) -> str:
    summaries = []
    for outcome_id in outcome_ids:
        outcome = outcomes_by_id.get(int(outcome_id))
        if not outcome:
            continue
        verb = outcome.get("action_verb", "").strip()
        description = outcome.get("description", "").strip()
        if verb and description and not description.lower().startswith(verb.lower()):
            description = f"{verb} {description}"
        summaries.append(
            f"RA{outcome_id} ({outcome.get('solo_level', 'SOLO')}): {description or verb}"
        )
    return "; ".join(summaries)


def _first_solo_level(outcome_ids: List[int], outcomes_by_id: Dict[int, Dict], fallback: str | None = None) -> str | None:
    if fallback:
        return fallback
    for outcome_id in outcome_ids:
        outcome = outcomes_by_id.get(int(outcome_id))
        if outcome and outcome.get("solo_level"):
            return outcome.get("solo_level")
    return None


def run_multimedia_generator(state: dict) -> dict:
    logger.info("Multimedia generator started")
    pedagogical_structure = state.get("pedagogical_structure", {})
    metadata = state.get("metadata", {})
    title = pedagogical_structure.get("presentation_title", metadata.get("title", "Apresentação"))
    slide_sequence = pedagogical_structure.get("slide_sequence", [])
    outcomes_by_id = _outcome_map(pedagogical_structure, state)

    query = " ".join([str(title), " ".join(str(slide.get("title", "")) for slide in slide_sequence[:6])])
    grounding_context, source_names = grounding_context_for_state(state, query=query, top_n=4)
    visual_assets = _visual_asset_paths(state)
    template_names = _template_names(state)

    slide_plan: List[Dict] = []

    title_item = SlidePlanItemModel(
        slide_number=0,
        title=title,
        bullets=[metadata.get("presentation_goal", "Apresentação educativa gerada pelo protótipo")],
        speaker_notes="Apresentar o tema, o objetivo, a lógica pedagógica e a progressão SOLO da sessão.",
        visual_description=_compose_visual_description(f"Imagem de capa relacionada com {title}.", source_names),
        image_prompt=(
            f"Educational title slide cover about {title}, clean academic presentation style. "
            f"Use the following references if relevant: {', '.join(source_names[:3])}. "
            f"Style references: {', '.join(template_names[:2]) if template_names else 'none'}"
        ),
        image_path=visual_assets[0] if visual_assets else None,
        kind="title",
    )

    title_dict = title_item.model_dump()
    if not title_dict.get("image_path"):
        title_dict["image_path"] = image_service.generate_image(
            prompt=title_dict["image_prompt"],
            filename_stem=f"slide_00_{_slugify(title)}",
            size=_image_size_for_kind("title"),
        )
    title_dict["source_documents"] = source_names
    slide_plan.append(title_dict)

    for idx, slide in enumerate(slide_sequence, start=1):
        asset_path = visual_assets[idx % len(visual_assets)] if visual_assets else None
        outcome_ids = slide.get("learning_outcome_ids", []) or []
        outcome_summary = _outcome_summary(outcome_ids, outcomes_by_id)
        solo_level = _first_solo_level(outcome_ids, outcomes_by_id, fallback=slide.get("solo_level"))
        solo_context = f" Alinhado com {solo_level}." if solo_level else ""
        notes = slide.get("objective", "Explicar o conteúdo deste slide de forma clara e adequada ao público.")
        if outcome_summary:
            notes = f"{notes}\n\nResultado(s) de aprendizagem SOLO: {outcome_summary}"

        item = SlidePlanItemModel(
            slide_number=slide.get("slide_number"),
            title=slide.get("title", "Slide"),
            bullets=slide.get("content_points", []) or ["Conteúdo não disponível"],
            speaker_notes=notes,
            visual_description=_compose_visual_description(
                f"Elemento visual educativo relacionado com {slide.get('title', 'o tema do slide')}.{solo_context}",
                source_names,
            ),
            image_prompt=(
                f"Educational illustration for slide titled '{slide.get('title', 'Slide')}', clean presentation style. "
                f"Pedagogical alignment: {solo_level or 'SOLO learning outcome'}; {outcome_summary or 'no specific outcome summary'}. "
                f"Grounding references: {', '.join(source_names[:3]) or 'none'}. "
                f"Use template cues from {', '.join(template_names[:2]) if template_names else 'no explicit template'}"
            ),
            image_path=asset_path,
            kind="content",
            learning_outcome_ids=outcome_ids,
            solo_level=solo_level,
            learning_outcome_summary=outcome_summary,
        )

        item_dict = item.model_dump()
        if not item_dict.get("image_path"):
            item_dict["image_path"] = image_service.generate_image(
                prompt=item_dict["image_prompt"],
                filename_stem=f"slide_{item_dict['slide_number']:02d}_{_slugify(item_dict['title'])}",
                size=_image_size_for_kind("content"),
            )
        item_dict["source_documents"] = source_names
        slide_plan.append(item_dict)

    closing_outcome_ids = [oid for oid, outcome in outcomes_by_id.items() if outcome.get("solo_level") in {"SOLO_4", "SOLO_5"}]
    closing_summary = _outcome_summary(closing_outcome_ids[:2], outcomes_by_id)
    closing_item = SlidePlanItemModel(
        slide_number=len(slide_plan),
        title="Conclusão",
        bullets=[
            "Síntese dos principais pontos abordados",
            "Reforço das ideias-chave da apresentação",
            "Possíveis extensões ou aplicações",
        ],
        speaker_notes=(
            "Fechar a apresentação com uma síntese breve e clara."
            + (f"\n\nRetomar resultados SOLO de maior complexidade: {closing_summary}" if closing_summary else "")
        ),
        visual_description=_compose_visual_description("Ícone ou ilustração simples de encerramento.", source_names),
        image_prompt="Minimal educational closing slide illustration, clean academic style",
        image_path=visual_assets[-1] if visual_assets else None,
        kind="closing",
        learning_outcome_ids=closing_outcome_ids[:2],
        solo_level="SOLO_5" if any(outcomes_by_id.get(oid, {}).get("solo_level") == "SOLO_5" for oid in closing_outcome_ids[:2]) else None,
        learning_outcome_summary=closing_summary,
    )

    closing_dict = closing_item.model_dump()
    if not closing_dict.get("image_path"):
        closing_dict["image_path"] = image_service.generate_image(
            prompt=closing_dict["image_prompt"],
            filename_stem="slide_final_conclusao",
            size=_image_size_for_kind("content"),
        )
    closing_dict["source_documents"] = source_names
    slide_plan.append(closing_dict)

    logger.info("Multimedia generator completed with %s slides", len(slide_plan))
    return {
        "slide_plan": slide_plan,
        "current_step": "multimedia_generation",
        "status": "slides_completed",
        "error_message": "",
    }
