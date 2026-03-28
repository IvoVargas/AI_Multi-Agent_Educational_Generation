from __future__ import annotations

import json

import gradio as gr

from src.graph import run_analysis_step, run_orchestrated_cycle, run_structure_step
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


def _sync_form_into_state(
    app_state,
    text_base,
    title,
    target_audience,
    education_level,
    presentation_goal,
    num_slides,
    language,
    extra_instructions,
):
    if not app_state:
        return _build_or_reset_state(
            text_base,
            title,
            target_audience,
            education_level,
            presentation_goal,
            num_slides,
            language,
            extra_instructions,
        )

    state = dict(app_state)
    state["user_input"] = text_base.strip()

    metadata = dict(state.get("metadata", {}))
    metadata.update(
        {
            "title": title.strip(),
            "target_audience": target_audience.strip(),
            "education_level": education_level.strip(),
            "presentation_goal": presentation_goal.strip(),
            "num_slides": int(num_slides),
            "language": language.strip() or "pt-PT",
            "extra_instructions": extra_instructions.strip(),
        }
    )
    state["metadata"] = metadata
    return state


def continue_with_orchestrator(
    app_state,
    text_base,
    title,
    target_audience,
    education_level,
    presentation_goal,
    num_slides,
    language,
    extra_instructions,
):
    state = _sync_form_into_state(
        app_state,
        text_base,
        title,
        target_audience,
        education_level,
        presentation_goal,
        num_slides,
        language,
        extra_instructions,
    )

    state = run_orchestrated_cycle(state)

    presentation_path = state.get("presentation_path") or None
    status_message = state.get("assistant_message") or f"Estado: {state.get('status', '')}"

    return (
        state,
        state.get("assistant_message", ""),
        _pretty(state.get("content_analysis", {})),
        _pretty(state.get("pedagogical_structure", {})),
        _pretty(state.get("slide_plan", [])),
        presentation_path,
        _status(status_message),
    )


def regenerate_analysis(feedback, app_state):
    if not app_state:
        raise gr.Error("Gera primeiro a análise conceptual.")

    state = dict(app_state)
    state["analysis_feedback"] = feedback.strip()
    state["analysis_approved"] = False
    state["pedagogical_structure"] = {}
    state["structure_approved"] = False
    state["slide_plan"] = []
    state["presentation_path"] = ""

    state = run_analysis_step(state)

    assistant_message = "Análise conceptual regenerada com base no feedback. Revê e aprova ou volta a reformular."
    state["assistant_message"] = assistant_message
    state["next_action"] = "wait_analysis_approval"
    state["awaiting_user_input"] = True
    state["status"] = "awaiting_input"

    return (
        state,
        assistant_message,
        _pretty(state.get("content_analysis", {})),
        _pretty(state.get("pedagogical_structure", {})),
        _pretty(state.get("slide_plan", [])),
        None,
        _status(assistant_message),
    )


def approve_analysis(app_state):
    if not app_state or not app_state.get("content_analysis"):
        raise gr.Error("Não existe análise para aprovar.")

    state = dict(app_state)
    state["analysis_approved"] = True
    state["assistant_message"] = "Análise aprovada. Carrega em 'Iniciar / Continuar com orquestrador' para gerar a estrutura pedagógica."
    state["next_action"] = "run_pedagogical_design"
    state["awaiting_user_input"] = False
    state["status"] = "ready_to_continue"

    return state, state["assistant_message"], _status(state["assistant_message"])


def regenerate_structure(feedback, app_state):
    if not app_state or not app_state.get("content_analysis"):
        raise gr.Error("Gera primeiro a estrutura pedagógica.")

    state = dict(app_state)
    state["structure_feedback"] = feedback.strip()
    state["structure_approved"] = False
    state["slide_plan"] = []
    state["presentation_path"] = ""

    state = run_structure_step(state)

    assistant_message = "Estrutura pedagógica regenerada com base no feedback. Revê e aprova ou volta a reformular."
    state["assistant_message"] = assistant_message
    state["next_action"] = "wait_structure_approval"
    state["awaiting_user_input"] = True
    state["status"] = "awaiting_input"

    return (
        state,
        assistant_message,
        _pretty(state.get("content_analysis", {})),
        _pretty(state.get("pedagogical_structure", {})),
        _pretty(state.get("slide_plan", [])),
        None,
        _status(assistant_message),
    )


def approve_structure(app_state):
    if not app_state or not app_state.get("pedagogical_structure"):
        raise gr.Error("Não existe estrutura para aprovar.")

    state = dict(app_state)
    state["structure_approved"] = True
    state["assistant_message"] = "Estrutura aprovada. Carrega em 'Iniciar / Continuar com orquestrador' para gerar o PowerPoint final."
    state["next_action"] = "run_multimedia_generation"
    state["awaiting_user_input"] = False
    state["status"] = "ready_to_continue"

    return state, state["assistant_message"], _status(state["assistant_message"])


def build_interface():
    with gr.Blocks(title="AI Multi-Agent Educational Generation") as demo:
        app_state = gr.State({})

        gr.Markdown("# AI Multi-Agent Educational Generation")
        gr.Markdown(
            "Protótipo com agente LLM orquestrador, agentes especializados e validação humana em duas etapas."
        )

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

                continue_btn = gr.Button("Iniciar / Continuar com orquestrador", variant="primary")

                analysis_feedback = gr.Textbox(label="Feedback para reformular a análise", lines=3)
                regenerate_analysis_btn = gr.Button("Regenerar análise")
                approve_analysis_btn = gr.Button("Aprovar análise")

                structure_feedback = gr.Textbox(label="Feedback para reformular a estrutura", lines=3)
                regenerate_structure_btn = gr.Button("Regenerar estrutura")
                approve_structure_btn = gr.Button("Aprovar estrutura")

            with gr.Column(scale=1):
                status_output = gr.Textbox(label="Estado do processo", lines=3)
                assistant_output = gr.Textbox(label="Mensagem do orquestrador", lines=4)
                analysis_output = gr.Textbox(label="Análise conceptual", lines=14)
                structure_output = gr.Textbox(label="Estrutura pedagógica", lines=14)
                slides_output = gr.Textbox(label="Plano de slides", lines=14)
                pptx_output = gr.File(label="PowerPoint gerado")

        continue_btn.click(
            fn=continue_with_orchestrator,
            inputs=[
                app_state,
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
                assistant_output,
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
                assistant_output,
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
            outputs=[app_state, assistant_output, status_output],
        )

        regenerate_structure_btn.click(
            fn=regenerate_structure,
            inputs=[structure_feedback, app_state],
            outputs=[
                app_state,
                assistant_output,
                analysis_output,
                structure_output,
                slides_output,
                pptx_output,
                status_output,
            ],
        )

        approve_structure_btn.click(
            fn=approve_structure,
            inputs=[app_state],
            outputs=[app_state, assistant_output, status_output],
        )

    return demo