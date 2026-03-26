from __future__ import annotations

import json

import gradio as gr

from src.graph import (
    export_pptx_step,
    run_analysis_step,
    run_multimedia_step,
    run_structure_step,
)
from src.state import PrototypeState, create_initial_state


def _pretty(data) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def _status(message: str) -> str:
    return message


def _build_or_reset_state(
    text_base: str,
    title: str,
    target_audience: str,
    education_level: str,
    presentation_goal: str,
    num_slides: int,
    language: str,
    extra_instructions: str,
) -> PrototypeState:
    return create_initial_state(
        text_base=text_base,
        title=title,
        target_audience=target_audience,
        education_level=education_level,
        presentation_goal=presentation_goal,
        num_slides=int(num_slides),
        language=language,
        extra_instructions=extra_instructions,
    )


def generate_analysis(
    text_base,
    title,
    target_audience,
    education_level,
    presentation_goal,
    num_slides,
    language,
    extra_instructions,
):
    state = _build_or_reset_state(
        text_base,
        title,
        target_audience,
        education_level,
        presentation_goal,
        num_slides,
        language,
        extra_instructions,
    )
    state = run_analysis_step(state)

    return (
        state,
        _pretty(state.get("content_analysis", {})),
        "",
        "",
        None,
        _status("Análise conceptual gerada. Revê o resultado e aprova ou pede reformulação."),
    )


def regenerate_analysis(feedback, app_state):
    if not app_state:
        raise gr.Error("Gera primeiro a análise conceptual.")

    app_state["analysis_feedback"] = feedback.strip()
    app_state["analysis_approved"] = False
    app_state["pedagogical_structure"] = {}
    app_state["structure_approved"] = False
    app_state["slide_plan"] = []
    app_state["presentation_path"] = ""

    app_state = run_analysis_step(app_state)

    return (
        app_state,
        _pretty(app_state.get("content_analysis", {})),
        "",
        "",
        None,
        _status("Análise conceptual regenerada com base no feedback."),
    )


def approve_analysis(app_state):
    if not app_state or not app_state.get("content_analysis"):
        raise gr.Error("Não existe análise para aprovar.")

    app_state["analysis_approved"] = True
    return app_state, _status("Análise aprovada. Já podes gerar a estrutura pedagógica.")


def generate_structure(app_state):
    if not app_state or not app_state.get("analysis_approved"):
        raise gr.Error("Aprova primeiro a análise conceptual.")

    app_state = run_structure_step(app_state)

    return (
        app_state,
        _pretty(app_state.get("pedagogical_structure", {})),
        "",
        None,
        _status("Estrutura pedagógica gerada. Revê e aprova ou pede reformulação."),
    )


def regenerate_structure(feedback, app_state):
    if not app_state or not app_state.get("content_analysis"):
        raise gr.Error("Gera primeiro a estrutura pedagógica.")

    app_state["structure_feedback"] = feedback.strip()
    app_state["structure_approved"] = False
    app_state["slide_plan"] = []
    app_state["presentation_path"] = ""

    app_state = run_structure_step(app_state)

    return (
        app_state,
        _pretty(app_state.get("pedagogical_structure", {})),
        "",
        None,
        _status("Estrutura pedagógica regenerada com base no feedback."),
    )


def approve_structure(app_state):
    if not app_state or not app_state.get("pedagogical_structure"):
        raise gr.Error("Não existe estrutura para aprovar.")

    app_state["structure_approved"] = True
    return app_state, _status("Estrutura aprovada. Já podes gerar a apresentação final.")


def generate_presentation(app_state):
    if not app_state or not app_state.get("structure_approved"):
        raise gr.Error("Aprova primeiro a estrutura pedagógica.")

    app_state = run_multimedia_step(app_state)
    app_state = export_pptx_step(app_state)

    return (
        app_state,
        _pretty(app_state.get("slide_plan", [])),
        app_state.get("presentation_path", ""),
        _status("Apresentação gerada com sucesso."),
    )


def build_interface():
    with gr.Blocks(title="AI Multi-Agent Educational Generation") as demo:
        app_state = gr.State({})

        gr.Markdown("# AI Multi-Agent Educational Generation")
        gr.Markdown("Protótipo com validação humana real em duas etapas: análise conceptual e estrutura pedagógica.")

        with gr.Row():
            with gr.Column(scale=1):
                text_base = gr.Textbox(label="Texto-base", lines=12)
                title = gr.Textbox(label="Título da apresentação")
                target_audience = gr.Textbox(label="Público-alvo")
                education_level = gr.Textbox(label="Nível de ensino")
                presentation_goal = gr.Textbox(label="Objetivo da apresentação")
                num_slides = gr.Number(label="Número aproximado de slides", value=6, precision=0)
                language = gr.Textbox(label="Idioma", value="pt-PT")
                extra_instructions = gr.Textbox(label="Instruções adicionais", lines=4)

                generate_analysis_btn = gr.Button("1. Gerar análise conceptual", variant="primary")
                analysis_feedback = gr.Textbox(label="Feedback para reformular a análise", lines=3)
                regenerate_analysis_btn = gr.Button("1A. Regenerar análise")
                approve_analysis_btn = gr.Button("1B. Aprovar análise")

                generate_structure_btn = gr.Button("2. Gerar estrutura pedagógica", variant="primary")
                structure_feedback = gr.Textbox(label="Feedback para reformular a estrutura", lines=3)
                regenerate_structure_btn = gr.Button("2A. Regenerar estrutura")
                approve_structure_btn = gr.Button("2B. Aprovar estrutura")

                generate_presentation_btn = gr.Button("3. Gerar PowerPoint final", variant="primary")

            with gr.Column(scale=1):
                status_output = gr.Textbox(label="Estado do processo", lines=3)
                analysis_output = gr.Textbox(label="Análise conceptual", lines=14)
                structure_output = gr.Textbox(label="Estrutura pedagógica", lines=14)
                slides_output = gr.Textbox(label="Plano de slides", lines=14)
                pptx_output = gr.File(label="PowerPoint gerado")

        generate_analysis_btn.click(
            fn=generate_analysis,
            inputs=[
                text_base,
                title,
                target_audience,
                education_level,
                presentation_goal,
                num_slides,
                language,
                extra_instructions,
            ],
            outputs=[
                app_state,
                analysis_output,
                structure_output,
                slides_output,
                pptx_output,
                status_output,
            ],
        )

        regenerate_analysis_btn.click(
            fn=regenerate_analysis,
            inputs=[analysis_feedback, app_state],
            outputs=[
                app_state,
                analysis_output,
                structure_output,
                slides_output,
                pptx_output,
                status_output,
            ],
        )

        approve_analysis_btn.click(
            fn=approve_analysis,
            inputs=[app_state],
            outputs=[app_state, status_output],
        )

        generate_structure_btn.click(
            fn=generate_structure,
            inputs=[app_state],
            outputs=[
                app_state,
                structure_output,
                slides_output,
                pptx_output,
                status_output,
            ],
        )

        regenerate_structure_btn.click(
            fn=regenerate_structure,
            inputs=[structure_feedback, app_state],
            outputs=[
                app_state,
                structure_output,
                slides_output,
                pptx_output,
                status_output,
            ],
        )

        approve_structure_btn.click(
            fn=approve_structure,
            inputs=[app_state],
            outputs=[app_state, status_output],
        )

        generate_presentation_btn.click(
            fn=generate_presentation,
            inputs=[app_state],
            outputs=[
                app_state,
                slides_output,
                pptx_output,
                status_output,
            ],
        )

    return demo