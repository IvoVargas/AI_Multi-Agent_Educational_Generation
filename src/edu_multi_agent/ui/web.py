from __future__ import annotations

from pathlib import Path

import gradio as gr
from pypdf import PdfReader

from edu_multi_agent.state import ReviewDecision, WorkflowState
from edu_multi_agent.workflow.graph import build_workflow


def _parse_learning_objectives(raw: str) -> list[str]:
    objectives = [obj.strip() for obj in raw.split(";") if obj.strip()]
    if objectives:
        return objectives
    return ["Compreender os conceitos fundamentais do tema."]


def _extract_source_text(file_path: str | None, text_input: str) -> str:
    base_text = text_input.strip()
    if not file_path:
        return base_text

    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".txt":
        file_text = path.read_text(encoding="utf-8", errors="ignore")
    elif suffix == ".pdf":
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        file_text = "\n".join(pages)
    else:
        file_text = ""

    combined = "\n\n".join(part for part in [base_text, file_text.strip()] if part)
    return combined.strip()


def _auto_approve_review_handler(_: str, __: str) -> tuple[ReviewDecision, str, str | None]:
    return "approve", "", None


def generate_slides_plan(
    topic: str,
    target_audience: str,
    objectives_raw: str,
    source_text: str,
    source_file: str | None,
) -> tuple[str, str, str, str]:
    if not topic.strip():
        return "", "", "", "Erro: o campo 'Tema' é obrigatório."

    learning_objectives = _parse_learning_objectives(objectives_raw)
    extracted_text = _extract_source_text(source_file, source_text)

    effective_topic = topic.strip()
    if extracted_text:
        effective_topic += "\n\nMaterial de referência fornecido pelo docente:\n" + extracted_text

    initial_state: WorkflowState = {
        "topic": effective_topic,
        "target_audience": target_audience.strip() or "Turma geral",
        "learning_objectives": learning_objectives,
        "review_history": [],
    }

    app = build_workflow(_auto_approve_review_handler)
    final_state = app.invoke(initial_state)

    return (
        final_state.get("content_analysis", ""),
        final_state.get("pedagogical_plan", ""),
        final_state.get("multimedia_content", ""),
        "Workflow executado com sucesso.",
    )


def build_web_app() -> gr.Blocks:
    with gr.Blocks(title="MVP Multi-Agente para Slides") as demo:
        gr.Markdown("# MVP Multi-Agente para Geração de Slides PowerPoint")
        gr.Markdown(
            "Forneça tema, público-alvo, objetivos e um ficheiro (`.txt` ou `.pdf`). "
            "O sistema gera análise, proposta pedagógica e plano final de slides."
        )

        with gr.Row():
            with gr.Column():
                topic = gr.Textbox(label="Tema", placeholder="Ex: Frações")
                target_audience = gr.Textbox(label="Público-alvo", placeholder="Ex: 7º ano")
                objectives = gr.Textbox(
                    label="Objetivos de aprendizagem (separados por ';')",
                    placeholder="Compreender frações; Resolver problemas simples",
                )
                source_text = gr.Textbox(
                    label="Contexto adicional (opcional)",
                    lines=6,
                    placeholder="Cole aqui notas, ementa ou orientações.",
                )
                source_file = gr.File(
                    label="Ficheiro de referência (.txt/.pdf)",
                    file_types=[".txt", ".pdf"],
                    type="filepath",
                )
                run_button = gr.Button("Gerar plano de slides", variant="primary")

            with gr.Column():
                status = gr.Textbox(label="Estado")
                analysis_output = gr.Textbox(label="1) Análise de conteúdo", lines=10)
                design_output = gr.Textbox(label="2) Proposta pedagógica", lines=10)
                slides_output = gr.Textbox(label="3) Plano final de slides PowerPoint", lines=14)

        run_button.click(
            fn=generate_slides_plan,
            inputs=[topic, target_audience, objectives, source_text, source_file],
            outputs=[analysis_output, design_output, slides_output, status],
        )

    return demo


def run_web() -> None:
    app = build_web_app()
    app.launch()
