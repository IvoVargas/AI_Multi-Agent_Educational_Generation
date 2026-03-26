from __future__ import annotations

import re
from typing import Dict, List

from src.models import SlidePlanItemModel
from src.services.image_service import ImageService
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)
image_service = ImageService()


def _slugify(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", text).strip("_").lower() or "slide"


def _image_size_for_kind(kind: str) -> str:
    if kind == "title":
        return "1536x1024"   # landscape
    return "1024x1536"       # portrait


def run_multimedia_generator(state: dict) -> dict:
    logger.info("Multimedia generator started")
    pedagogical_structure = state.get("pedagogical_structure", {})
    metadata = state.get("metadata", {})
    title = pedagogical_structure.get("presentation_title", metadata.get("title", "Apresentação"))
    slide_sequence = pedagogical_structure.get("slide_sequence", [])

    slide_plan: List[Dict] = []

    title_item = SlidePlanItemModel(
        slide_number=0,
        title=title,
        bullets=[metadata.get("presentation_goal", "Apresentação educativa gerada pelo protótipo")],
        speaker_notes="Apresentar o tema, o objetivo e o enquadramento da sessão.",
        visual_description=f"Imagem de capa relacionada com {title}.",
        image_prompt=f"Educational title slide cover about {title}, clean academic presentation style",
        image_path=None,
        kind="title",
    )

    title_dict = title_item.model_dump()
    title_dict["image_path"] = image_service.generate_image(
        prompt=title_dict["image_prompt"],
        filename_stem=f"slide_00_{_slugify(title)}",
        size=_image_size_for_kind("title"),
    )
    slide_plan.append(title_dict)

    for slide in slide_sequence:
        item = SlidePlanItemModel(
            slide_number=slide.get("slide_number"),
            title=slide.get("title", "Slide"),
            bullets=slide.get("content_points", []) or ["Conteúdo não disponível"],
            speaker_notes=slide.get(
                "objective",
                "Explicar o conteúdo deste slide de forma clara e adequada ao público.",
            ),
            visual_description=f"Elemento visual educativo relacionado com {slide.get('title', 'o tema do slide')}.",
            image_prompt=f"Educational illustration for slide titled '{slide.get('title', 'Slide')}', clean presentation style",
            image_path=None,
            kind="content",
        )

        item_dict = item.model_dump()
        item_dict["image_path"] = image_service.generate_image(
            prompt=item_dict["image_prompt"],
            filename_stem=f"slide_{item_dict['slide_number']:02d}_{_slugify(item_dict['title'])}",
            size=_image_size_for_kind("content"),
        )
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
        visual_description="Ícone ou ilustração simples de encerramento.",
        image_prompt="Minimal educational closing slide illustration, clean academic style",
        image_path=None,
        kind="closing",
    )

    closing_dict = closing_item.model_dump()
    closing_dict["image_path"] = image_service.generate_image(
        prompt=closing_dict["image_prompt"],
        filename_stem="slide_final_conclusao",
        size=_image_size_for_kind("content"),
    )
    slide_plan.append(closing_dict)

    logger.info("Multimedia generator completed with %s slides", len(slide_plan))
    return {
        "slide_plan": slide_plan,
        "current_step": "multimedia_generation",
        "status": "slides_completed",
        "error_message": "",
    }