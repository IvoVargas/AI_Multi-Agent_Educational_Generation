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


def run_multimedia_generator(state: dict) -> dict:
    logger.info("Multimedia generator started")
    pedagogical_structure = state.get("pedagogical_structure", {})
    metadata = state.get("metadata", {})
    title = pedagogical_structure.get("presentation_title", metadata.get("title", "Apresentação"))
    slide_sequence = pedagogical_structure.get("slide_sequence", [])

    query = " ".join([str(title), " ".join(str(slide.get("title", "")) for slide in slide_sequence[:6])])
    grounding_context, source_names = grounding_context_for_state(state, query=query, top_n=4)
    visual_assets = _visual_asset_paths(state)
    template_names = _template_names(state)

    slide_plan: List[Dict] = []

    title_item = SlidePlanItemModel(
        slide_number=0,
        title=title,
        bullets=[metadata.get("presentation_goal", "Apresentação educativa gerada pelo protótipo")],
        speaker_notes="Apresentar o tema, o objetivo e o enquadramento da sessão.",
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
        item = SlidePlanItemModel(
            slide_number=slide.get("slide_number"),
            title=slide.get("title", "Slide"),
            bullets=slide.get("content_points", []) or ["Conteúdo não disponível"],
            speaker_notes=slide.get("objective", "Explicar o conteúdo deste slide de forma clara e adequada ao público."),
            visual_description=_compose_visual_description(
                f"Elemento visual educativo relacionado com {slide.get('title', 'o tema do slide')}.",
                source_names,
            ),
            image_prompt=(
                f"Educational illustration for slide titled '{slide.get('title', 'Slide')}', clean presentation style. "
                f"Grounding references: {', '.join(source_names[:3]) or 'none'}. "
                f"Use template cues from {', '.join(template_names[:2]) if template_names else 'no explicit template'}"
            ),
            image_path=asset_path,
            kind="content",
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

    closing_item = SlidePlanItemModel(
        slide_number=len(slide_plan),
        title="Conclusão",
        bullets=[
            "Síntese dos principais pontos abordados",
            "Reforço das ideias-chave da apresentação",
            "Possíveis extensões ou aplicações",
        ],
        speaker_notes="Fechar a apresentação com uma síntese breve e clara.",
        visual_description=_compose_visual_description("Ícone ou ilustração simples de encerramento.", source_names),
        image_prompt="Minimal educational closing slide illustration, clean academic style",
        image_path=visual_assets[-1] if visual_assets else None,
        kind="closing",
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
