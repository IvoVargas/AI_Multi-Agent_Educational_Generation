from __future__ import annotations

import json

import gradio as gr

from src.graph import run_pipeline
from src.state import create_initial_state


def _run_generation(
    text_base: str,
    title: str,
    target_audience: str,
    education_level: str,
    presentation_goal: str,
    num_slides: int,
    language: str,
    extra_instructions: str,
):
    initial_state = create_initial_state(
        text_base=text_base,
        title=title,
        target_audience=target_audience,
        education_level=education_level,
        presentation_goal=presentation_goal,
        num_slides=num_slides,
        language=language,
        extra_instructions=extra_instructions,
    )

    final_state = run_pipeline(initial_state)

    analysis = json.dumps(final_state.get("content_analysis", {}), ensure_ascii=False, indent=2)
    structure = json.dumps(final_state.get("pedagogical_structure", {}), ensure_ascii=False, indent=2)
    slides = json.dumps(final_state.get("slide_plan", []), ensure_ascii=False, indent=2)
    pptx_file = final_state.get("presentation_path", "")

    return analysis, structure, slides, pptx_file


def build_interface():
    with gr.Blocks(title="AI Multi-Agent Educational Generation") as demo:
        gr.Markdown("# AI Multi-Agent Educational Generation")
        gr.Markdown("Protótipo mínimo para geração de apresentações educativas em PowerPoint.")

        with gr.Row():
            with gr.Column():
                text_base = gr.Textbox(label="Texto-base", lines=12)
                title = gr.Textbox(label="Título da apresentação")
                target_audience = gr.Textbox(label="Público-alvo")
                education_level = gr.Textbox(label="Nível de ensino")
                presentation_goal = gr.Textbox(label="Objetivo da apresentação")
                num_slides = gr.Number(label="Número aproximado de slides", value=6, precision=0)
                language = gr.Textbox(label="Idioma", value="pt-PT")
                extra_instructions = gr.Textbox(label="Instruções adicionais", lines=4)
                run_button = gr.Button("Iniciar geração")

            with gr.Column():
                analysis_output = gr.Textbox(label="Análise conceptual", lines=12)
                structure_output = gr.Textbox(label="Estrutura pedagógica", lines=12)
                slides_output = gr.Textbox(label="Plano de slides", lines=12)
                pptx_output = gr.File(label="PowerPoint gerado")

        run_button.click(
            fn=_run_generation,
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
                analysis_output,
                structure_output,
                slides_output,
                pptx_output,
            ],
        )

    return demo