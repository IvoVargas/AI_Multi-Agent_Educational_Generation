from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.models import BriefExtractionModel, FileRoleClassificationModel, SupportDocumentSummaryModel
from src.services.document_ingestion import ingest_file, select_relevant_chunks, supported_file_message
from src.services.llm_service import LLMService
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)
llm = LLMService()

VALID_ROLES = {"auto", "brief", "support", "visual", "template", "other"}


def _safe_int(value: object) -> Optional[int]:
    try:
        parsed = int(value)
        return parsed if parsed > 0 else None
    except Exception:
        return None


def _heuristic_role(file_record: Dict[str, Any]) -> str:
    name = str(file_record.get("name", "")).lower()
    ext = str(file_record.get("extension", "")).lower()
    text = str(file_record.get("text_excerpt", "")).lower()

    if file_record.get("is_visual"):
        return "visual"
    if ext in {".pptx", ".potx"} and any(token in name for token in ["template", "modelo", "exemplo", "sample"]):
        return "template"
    if any(token in name for token in ["brief", "requisito", "requirements", "spec", "pedido", "input"]):
        return "brief"
    if any(token in text for token in ["público-alvo", "publico-alvo", "número de slides", "numero de slides", "objetivo da apresentação", "objetivo"]):
        return "brief"
    return "support" if file_record.get("is_textual") else "other"


def classify_file_role(file_record: Dict[str, Any], explicit_role: str = "auto") -> Tuple[str, str]:
    explicit_role = (explicit_role or "auto").strip().lower()
    if explicit_role in VALID_ROLES and explicit_role != "auto":
        return explicit_role, "Definido manualmente pelo utilizador."

    heuristic = _heuristic_role(file_record)
    if heuristic in {"visual", "template", "brief"}:
        return heuristic, "Classificado por heurística com base na extensão e no nome do ficheiro."

    excerpt = str(file_record.get("text_excerpt", "")).strip()
    if not excerpt:
        return heuristic, "Sem conteúdo textual suficiente; classificação por heurística."

    system_prompt = """
És um classificador de ficheiros para um sistema de geração de apresentações.
Responde apenas com JSON válido.

Estrutura obrigatória:
{
  "role": "brief" | "support" | "visual" | "template" | "other",
  "rationale": "string"
}
"""

    user_prompt = f"""
Nome do ficheiro: {file_record.get('name', '')}
Extensão: {file_record.get('extension', '')}
Resumo do conteúdo:
{excerpt[:1800]}

Classifica o papel mais útil deste ficheiro no sistema.
Escreve uma racional curta, mas sem limite rígido de caracteres.
"""

    try:
        response = llm.generate_structured(system_prompt=system_prompt, user_prompt=user_prompt, schema=FileRoleClassificationModel)
        role = response.get("role", heuristic)
        rationale = response.get("rationale", "Classificação automática por LLM.")
        if role not in VALID_ROLES:
            role = heuristic
        return role, rationale
    except Exception:
        logger.warning("File role classification failed for %s. Using heuristic.", file_record.get("name", ""), exc_info=True)
        return heuristic, "Classificação automática por heurística."


def _detect_language(text: str) -> str | None:
    lower = text.lower()
    if "pt-pt" in lower or "português de portugal" in lower or "portugues de portugal" in lower:
        return "pt-PT"
    if "português" in lower or "portugues" in lower:
        return "pt-PT"
    if "english" in lower or "inglês" in lower or "ingles" in lower:
        return "en-US"
    return None


def _heuristic_brief_extract(text: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    match = re.search(r"(\d{1,2})\s*slides?", text, flags=re.IGNORECASE)
    if match:
        result["num_slides"] = int(match.group(1))

    title_match = re.search(r"(?:t[íi]tulo|tema)\s*[:\-]\s*(.+)", text, flags=re.IGNORECASE)
    if title_match:
        result["title"] = title_match.group(1).strip()[:200]

    audience_match = re.search(r"(?:público-alvo|publico-alvo)\s*[:\-]\s*(.+)", text, flags=re.IGNORECASE)
    if audience_match:
        result["target_audience"] = audience_match.group(1).strip()[:250]

    level_match = re.search(r"(?:nível de ensino|nivel de ensino)\s*[:\-]\s*(.+)", text, flags=re.IGNORECASE)
    if level_match:
        result["education_level"] = level_match.group(1).strip()[:120]

    goal_match = re.search(r"(?:objetivo|objetivo da apresentação|objetivo da apresentacao)\s*[:\-]\s*(.+)", text, flags=re.IGNORECASE)
    if goal_match:
        result["presentation_goal"] = goal_match.group(1).strip()[:250]

    language = _detect_language(text)
    if language:
        result["language"] = language

    result["text_base"] = text[:4000].strip() if text.strip() else None
    return {k: v for k, v in result.items() if v}


def extract_brief_metadata(file_record: Dict[str, Any]) -> Dict[str, Any]:
    excerpt = str(file_record.get("text", "") or file_record.get("text_excerpt", "")).strip()
    if not excerpt:
        return {"text_base": None}

    system_prompt = """
És um extrator de requisitos para apresentações educativas.
Responde apenas com JSON válido.

Estrutura obrigatória:
{
  "title": "string | null",
  "target_audience": "string | null",
  "education_level": "string | null",
  "presentation_goal": "string | null",
  "num_slides": 6,
  "language": "string | null",
  "extra_instructions": "string | null",
  "text_base": "string | null"
}
"""

    user_prompt = f"""
Extrai deste documento os requisitos que forem claramente identificáveis.
Se um campo não estiver claro, devolve null.

Documento: {file_record.get('name', '')}
Conteúdo:
{excerpt[:7000]}
"""

    try:
        return llm.generate_structured(system_prompt=system_prompt, user_prompt=user_prompt, schema=BriefExtractionModel)
    except Exception:
        logger.warning("Brief metadata extraction failed for %s. Using heuristic.", file_record.get("name", ""), exc_info=True)
        return _heuristic_brief_extract(excerpt)


def summarize_support_document(file_record: Dict[str, Any]) -> Dict[str, Any]:
    excerpt = str(file_record.get("text", "") or file_record.get("text_excerpt", "")).strip()
    if not excerpt:
        return {"summary": "Documento sem texto extraível.", "key_points": [], "preferred_usage": "reference"}

    system_prompt = """
És um resumidor de documentos de apoio para apresentações.
Responde apenas com JSON válido.

Estrutura obrigatória:
{
  "summary": "string",
  "key_points": ["string"],
  "preferred_usage": "grounding" | "style_reference" | "visual_reference" | "reference"
}
"""

    user_prompt = f"""
Resume o documento e indica como deve ser usado no pipeline.

Documento: {file_record.get('name', '')}
Conteúdo:
{excerpt[:7000]}

Podes devolver todos os key_points relevantes do documento. Não os limites artificialmente.
"""

    try:
        return llm.generate_structured(system_prompt=system_prompt, user_prompt=user_prompt, schema=SupportDocumentSummaryModel)
    except Exception:
        logger.warning("Support document summarization failed for %s. Using heuristic.", file_record.get("name", ""), exc_info=True)
        sentences = [line.strip() for line in excerpt.splitlines() if line.strip()][:5]
        return {
            "summary": sentences[0][:300] if sentences else f"Documento de apoio: {file_record.get('name', '')}",
            "key_points": sentences,
            "preferred_usage": "grounding",
        }


def _merge_brief_into_state(state: Dict[str, Any], brief_data: Dict[str, Any]) -> None:
    metadata = dict(state.get("metadata", {}))
    for key in ["title", "target_audience", "education_level", "presentation_goal", "language"]:
        value = brief_data.get(key)
        if isinstance(value, str) and value.strip() and not str(metadata.get(key, "")).strip():
            metadata[key] = value.strip()

    num_slides = _safe_int(brief_data.get("num_slides"))
    if num_slides and int(metadata.get("num_slides", 0) or 0) <= 0:
        metadata["num_slides"] = num_slides

    extra = brief_data.get("extra_instructions")
    if isinstance(extra, str) and extra.strip():
        existing = str(metadata.get("extra_instructions", "")).strip()
        metadata["extra_instructions"] = f"{existing}\n{extra.strip()}".strip() if existing else extra.strip()

    text_base = brief_data.get("text_base")
    if isinstance(text_base, str) and text_base.strip() and not state.get("user_input", "").strip():
        state["user_input"] = text_base.strip()

    state["metadata"] = metadata


def _build_knowledge_chunks(file_record: Dict[str, Any], role: str) -> List[Dict[str, Any]]:
    chunks: List[Dict[str, Any]] = []
    for index, text in enumerate(file_record.get("chunks", []), start=1):
        chunks.append(
            {
                "attachment_id": file_record.get("id"),
                "attachment_name": file_record.get("name"),
                "role": role,
                "chunk_index": index,
                "text": text,
            }
        )
    return chunks


def add_uploaded_files_to_state(
    state: Dict[str, Any],
    uploaded_files: List[str] | None,
    selected_role: str = "auto",
) -> Tuple[Dict[str, Any], List[str]]:
    if not uploaded_files:
        return state, []

    updated = dict(state)
    attachments = list(updated.get("uploaded_files", []))
    knowledge_chunks = list(updated.get("knowledge_chunks", []))
    existing_paths = {str(item.get("path", "")) for item in attachments}
    messages: List[str] = []

    explicit_role = (selected_role or "auto").strip().lower()
    has_existing_brief = any(item.get("role") == "brief" for item in attachments)
    first_auto_brief_assigned = has_existing_brief

    for file_path in uploaded_files:
        if not file_path:
            continue
        unsupported = supported_file_message(file_path)
        if unsupported:
            messages.append(f"- {unsupported}")
            continue
        if str(file_path) in existing_paths:
            messages.append(f"- O ficheiro **{Path(file_path).name}** já estava anexado e foi mantido.")
            continue

        file_record = ingest_file(file_path)

        if explicit_role == "auto" and not first_auto_brief_assigned:
            role = "brief"
            rationale = "Primeiro ficheiro em modo auto: tratado como briefing principal."
            first_auto_brief_assigned = True
        else:
            role, rationale = classify_file_role(file_record, explicit_role=explicit_role)

        file_record["role"] = role
        file_record["role_rationale"] = rationale

        if role == "brief":
            brief_data = extract_brief_metadata(file_record)
            file_record["summary_data"] = brief_data
            file_record["summary"] = "Documento usado como briefing principal."
            _merge_brief_into_state(updated, brief_data)
            used_for = ["metadata_extraction", "text_base"]
        elif role == "support":
            summary = summarize_support_document(file_record)
            file_record["summary_data"] = summary
            file_record["summary"] = summary.get("summary", "")
            file_record["key_points"] = summary.get("key_points", [])
            used_for = ["grounding"]
            knowledge_chunks.extend(_build_knowledge_chunks(file_record, role))
        elif role == "template":
            summary = summarize_support_document(file_record)
            file_record["summary_data"] = summary
            file_record["summary"] = summary.get("summary", "Template de referência.")
            file_record["key_points"] = summary.get("key_points", [])
            used_for = ["style_reference"]
            knowledge_chunks.extend(_build_knowledge_chunks(file_record, role))
        elif role == "visual":
            file_record["summary"] = "Asset visual disponível para reutilização ou referência visual."
            used_for = ["visual_reference"]
        else:
            summary = summarize_support_document(file_record) if file_record.get("is_textual") else {"summary": "Ficheiro anexado como referência geral.", "key_points": []}
            file_record["summary_data"] = summary
            file_record["summary"] = summary.get("summary", "Ficheiro de referência geral.")
            file_record["key_points"] = summary.get("key_points", [])
            used_for = ["reference"]
            knowledge_chunks.extend(_build_knowledge_chunks(file_record, "support"))

        file_record["used_for"] = used_for
        attachments.append(file_record)
        existing_paths.add(str(file_path))
        messages.append(
            f"- **{file_record['name']}** → `{role}`. {file_record.get('summary', '').strip() or rationale}"
        )

    updated["uploaded_files"] = attachments
    updated["knowledge_chunks"] = knowledge_chunks
    updated["retrieval_enabled"] = bool(knowledge_chunks)
    updated["source_summary"] = f"{len(attachments)} ficheiro(s) anexado(s), {len(knowledge_chunks)} chunks indexados."
    return updated, messages


def grounding_context_for_state(state: Dict[str, Any], query: str, top_n: int = 5) -> Tuple[str, List[str]]:
    attachments = list(state.get("uploaded_files", []))
    knowledge_chunks = list(state.get("knowledge_chunks", []))
    if not attachments:
        return "", []

    selected = select_relevant_chunks(knowledge_chunks, query, top_n=top_n)
    if not selected:
        selected = [chunk for chunk in knowledge_chunks[:top_n]]

    blocks: List[str] = []
    source_names: List[str] = []
    for item in selected:
        name = str(item.get("attachment_name", "Documento"))
        if name not in source_names:
            source_names.append(name)
        blocks.append(f"Fonte: {name}\nExcerto:\n{item.get('text', '')}")

    templates = [item.get("name") for item in attachments if item.get("role") == "template"]
    visuals = [item.get("name") for item in attachments if item.get("role") == "visual"]
    extras: List[str] = []
    if templates:
        extras.append("Templates ou referências de estilo disponíveis: " + ", ".join(map(str, templates[:3])))
        source_names.extend([name for name in templates if name not in source_names])
    if visuals:
        extras.append("Assets visuais disponíveis: " + ", ".join(map(str, visuals[:5])))
        source_names.extend([name for name in visuals if name not in source_names])

    context_parts = []
    if blocks:
        context_parts.append("\n\n".join(blocks))
    if extras:
        context_parts.append("\n".join(extras))
    return "\n\n".join(part for part in context_parts if part.strip()), source_names
