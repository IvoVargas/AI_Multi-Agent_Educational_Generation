from __future__ import annotations

from typing import Any, Dict, List, Tuple

import json

import gradio as gr

from src.agents.chat_intake import extract_chat_update
from src.agents.file_intake import add_uploaded_files_to_state
from src.graph import run_orchestrated_cycle
from src.state import PrototypeState, create_chat_initial_state
from src.utils.formatters import (
    render_analysis_markdown,
    render_analysis_preview_for_chat,
    render_slide_plan_markdown,
    render_slide_plan_preview_for_chat,
    render_solo_markdown,
    render_solo_preview_for_chat,
    render_status_html,
    render_structure_markdown,
    render_structure_preview_for_chat,
)

CHATBOT_HELP = """
- *Quero uma apresentação sobre redes neuronais para licenciatura em engenharia informática, com 8 slides, em português de Portugal e foco introdutório.*
- *Texto-base: os sistemas multiagente permitem dividir tarefas complexas por agentes especializados...*
- *Aprovo a análise.*
- *Reformula a estrutura e torna-a mais técnica.*
- *Anexa um PDF com os requisitos ou documentos de apoio e diz-me se devo tratá-los como brief, apoio, template ou assets visuais.*
- *Continua.*
- *Reinicia.*
"""

APP_CSS = """
html, body {
    margin: 0;
    padding: 0;
    height: 100%;
    overflow: hidden !important;
    background: #0b1220;
}

body {
    color: #e5e7eb;
}

.gradio-container {
    background: #0b1220;
    color: #e5e7eb;
    max-width: 100vw !important;
    height: 100vh !important;
    overflow: hidden !important;
    padding: 12px 14px !important;
}

.app-shell {
    height: calc(94vh - 24px);
    overflow: hidden;
    gap: 10px;
}

.header-shell {
    padding: 10px 14px;
    background: linear-gradient(180deg, #0f172a 0%, #0b1220 100%);
    border: 1px solid #1f2937;
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.22);
}

.header-shell h1,
.header-shell p,
label,
legend {
    color: #e5e7eb !important;
    margin-top: 0 !important;
    margin-bottom: 0.2rem !important;
}

.header-shell p {
    color: #94a3b8 !important;
}

.content-shell {
    flex: 1 1 auto !important;
    min-height: 0 !important;
    overflow: hidden;
    gap: 10px;
}

.left-shell,
.right-shell {
    min-height: 0 !important;
    height: 100%;
    overflow: hidden;
    gap: 10px;
}

.help-shell,
.composer-shell,
.file-shell,
.panel-shell,
.status-shell,
#chatbot-panel {
    background: #111827 !important;
    border: 1px solid #243041 !important;
    border-radius: 16px !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.24);
}

.help-shell {
    overflow: hidden;
}

.help-shell .label-wrap,
.help-shell .accordion-header {
    background: #111827 !important;
}

.help-shell .prose,
.help-shell .md,
.help-shell .markdown,
.panel-shell > .prose,
.panel-shell .prose,
.panel-shell .wrap,
.panel-shell .md,
.panel-shell .markdown,
.status-shell,
.file-shell,
#chatbot-panel .message,
#chatbot-panel .message * {
    color: #e5e7eb !important;
}

.panel-shell h1,
.panel-shell h2,
.panel-shell h3,
.panel-shell h4,
.panel-shell p,
.panel-shell li,
.panel-shell strong,
.panel-shell code,
.panel-shell em,
.help-shell h1,
.help-shell h2,
.help-shell h3,
.help-shell h4,
.help-shell p,
.help-shell li,
.help-shell strong,
.help-shell code,
.help-shell em {
    color: #e5e7eb !important;
}

#chatbot-panel {
    flex: 1 1 auto;
    min-height: 0 !important;
    overflow: hidden;
}

#chatbot-panel .wrap,
#chatbot-panel .bubble-wrap,
#chatbot-panel .message-wrap,
#chatbot-panel .messages {
    background: transparent !important;
}

#chatbot-panel .bubble-wrap {
    padding-inline: 10px;
}

#chatbot-panel .message {
    border-radius: 14px !important;
}

#chatbot-panel .message.user {
    background: #1d4ed8 !important;
    border-color: #2563eb !important;
}

#chatbot-panel .message.bot {
    background: #0f172a !important;
}

.composer-shell {
    padding: 10px;
}

.composer-row {
    align-items: stretch;
}

.composer-input textarea,
textarea,
input,
select {
    background: #0f172a !important;
    color: #e5e7eb !important;
    border: 1px solid #243041 !important;
}

.composer-input textarea {
    min-height: 78px !important;
}

.attachment-controls {
    margin-top: 10px;
    align-items: end;
}

.attachment-controls .wrap,
.attachment-controls .block,
.attachment-role {
    min-height: 0 !important;
}

button.primary,
.send-btn button {
    background: linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%) !important;
    border: none !important;
}

.send-btn button {
    min-height: 78px;
    border-radius: 14px !important;
}

.reset-btn button {
    min-height: 42px;
    border-radius: 14px !important;
    background: #1f2937 !important;
    border: 1px solid #334155 !important;
    color: #e5e7eb !important;
}

.tabs-shell {
    height: 100%;
    min-height: 0 !important;
    overflow: hidden;
}

.tabs-shell .tab-nav {
    gap: 6px;
    background: transparent !important;
    margin-bottom: 8px !important;
}

.tabs-shell button {
    border-radius: 12px !important;
}

.tabs-shell .tabitem {
    height: calc(100vh - 182px);
    min-height: 0 !important;
    overflow: hidden;
}

.tabs-shell .tabitem > div {
    height: 100%;
    min-height: 0 !important;
}

.status-panel,
.result-panel,
.export-panel {
    height: 100% !important;
    min-height: 0 !important;
    overflow: auto !important;
    padding: 6px;
}

.status-shell {
    padding: 14px;
}

.export-panel {
    padding: 14px;
}

.status-root {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.status-section {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.section-title {
    font-size: 0.92rem;
    font-weight: 700;
    color: #e5e7eb;
}

.progress-track {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: nowrap;
    overflow-x: auto;
    padding-bottom: 2px;
}

.progress-step {
    min-width: 76px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
}

.step-dot {
    width: 34px;
    height: 34px;
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.9rem;
    background: #0f172a;
    border: 1px solid #334155;
    color: #94a3b8;
}

.step-label {
    font-size: 0.78rem;
    color: #94a3b8;
    text-align: center;
    line-height: 1.2;
}

.progress-step.active .step-dot {
    background: rgba(37, 99, 235, 0.16);
    border-color: #3b82f6;
    color: #dbeafe;
}

.progress-step.active .step-label {
    color: #dbeafe;
}

.progress-step.complete .step-dot {
    background: rgba(16, 185, 129, 0.16);
    border-color: #10b981;
    color: #d1fae5;
}

.progress-step.complete .step-label {
    color: #d1fae5;
}

.progress-connector {
    flex: 1 0 24px;
    min-width: 24px;
    height: 2px;
    background: linear-gradient(90deg, #243041 0%, #334155 100%);
    border-radius: 999px;
}

.status-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
}

.status-card {
    background: #0f172a;
    border: 1px solid #243041;
    border-radius: 14px;
    padding: 12px;
}

.status-card.wide {
    grid-column: 1 / -1;
}

.subtle-label {
    font-size: 0.73rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 6px;
}

.big-value {
    color: #e5e7eb;
    font-size: 0.95rem;
    font-weight: 600;
    word-break: break-word;
}

.chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.status-chip,
.missing-chip {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    border-radius: 999px;
    padding: 7px 10px;
    line-height: 1;
}

.status-chip {
    background: #0f172a;
    border: 1px solid #243041;
}

.status-chip.muted {
    opacity: 0.72;
}

.source-chip {
    background: rgba(37, 99, 235, 0.12);
    border-color: rgba(59, 130, 246, 0.35);
}

.chip-label {
    color: #94a3b8;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}

.chip-value {
    color: #e5e7eb;
    font-size: 0.82rem;
    font-weight: 600;
    max-width: 220px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.missing-chip {
    background: rgba(245, 158, 11, 0.12);
    border: 1px solid rgba(245, 158, 11, 0.35);
    color: #fcd34d;
    font-size: 0.8rem;
    font-weight: 600;
}

.source-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.source-item {
    padding: 10px 12px;
    background: #0f172a;
    border: 1px solid #243041;
    border-radius: 12px;
}

.source-name {
    color: #e5e7eb;
    font-size: 0.9rem;
    font-weight: 700;
}

.source-meta {
    color: #94a3b8;
    font-size: 0.8rem;
    margin-top: 3px;
}

.file-preview,
.file-upload,
[data-testid="file"] {
    background: #111827 !important;
    border: 1px solid #243041 !important;
    color: #e5e7eb !important;
    border-radius: 14px !important;
}

@media (max-width: 1200px) {
    html, body, .gradio-container {
        overflow: auto !important;
        height: auto !important;
    }

    .app-shell {
        height: auto;
    }

    .content-shell,
    .left-shell,
    .right-shell,
    .tabs-shell .tabitem {
        height: auto !important;
        overflow: visible !important;
    }

    #chatbot-panel {
        min-height: 520px !important;
    }

    .status-grid {
        grid-template-columns: 1fr;
    }

    .status-card.wide {
        grid-column: auto;
    }
}
"""

TAB_STATUS = "status"
TAB_ANALYSIS = "analysis"
TAB_SOLO = "solo"
TAB_STRUCTURE = "structure"
TAB_SLIDES = "slides"
TAB_EXPORT = "export"


def _append_turn(state: Dict[str, Any], role: str, content: str) -> None:
    history = list(state.get("conversation_history", []))
    history.append({"role": role, "content": content})
    state["conversation_history"] = history


def _normalize_uploaded_files(uploaded_files: Any) -> List[str]:
    if not uploaded_files:
        return []
    if isinstance(uploaded_files, str):
        return [uploaded_files]
    if isinstance(uploaded_files, list):
        return [item for item in uploaded_files if isinstance(item, str) and item.strip()]
    return []


def _merge_extracted_into_state(state: Dict[str, Any], extracted: Dict[str, Any]) -> Dict[str, Any]:
    metadata = dict(state.get("metadata", {}))

    for field in ["title", "target_audience", "education_level", "presentation_goal", "language"]:
        value = extracted.get(field)
        if isinstance(value, str) and value.strip():
            metadata[field] = value.strip()

    num_slides = extracted.get("num_slides")
    if isinstance(num_slides, int) and num_slides > 0:
        metadata["num_slides"] = num_slides

    extra_instructions = extracted.get("extra_instructions")
    if isinstance(extra_instructions, str) and extra_instructions.strip():
        existing = str(metadata.get("extra_instructions", "")).strip()
        metadata["extra_instructions"] = (
            f"{existing}\n{extra_instructions.strip()}" if existing else extra_instructions.strip()
        )

    text_base = extracted.get("text_base")
    if isinstance(text_base, str) and text_base.strip():
        existing_text = state.get("user_input", "").strip()
        if not existing_text:
            state["user_input"] = text_base.strip()
        elif text_base.strip().lower() not in existing_text.lower():
            state["user_input"] = f"{existing_text}\n\n{text_base.strip()}"

    state["metadata"] = metadata
    return state


def _assistant_reply_from_state(
    previous_state: Dict[str, Any],
    current_state: Dict[str, Any],
    fallback_message: str = "Estado atualizado.",
) -> str:
    parts: List[str] = []

    assistant_message = current_state.get("assistant_message", "").strip()
    parts.append(assistant_message or fallback_message)

    if not previous_state.get("content_analysis") and current_state.get("content_analysis"):
        preview = render_analysis_preview_for_chat(current_state.get("content_analysis", {}))
        if preview:
            parts.append(preview)

    if not previous_state.get("solo_learning_outcomes") and current_state.get("solo_learning_outcomes"):
        preview = render_solo_preview_for_chat(current_state)
        if preview:
            parts.append(preview)

    if not previous_state.get("pedagogical_structure") and current_state.get("pedagogical_structure"):
        preview = render_structure_preview_for_chat(current_state.get("pedagogical_structure", {}))
        if preview:
            parts.append(preview)

    if not previous_state.get("slide_plan") and current_state.get("slide_plan"):
        preview = render_slide_plan_preview_for_chat(current_state.get("slide_plan", []))
        if preview:
            parts.append(preview)

    if not previous_state.get("presentation_path") and current_state.get("presentation_path"):
        parts.append("### Exportação concluída\nO ficheiro PowerPoint já está pronto para download no separador **Exportar**.")

    return "\n\n".join(part for part in parts if part.strip())


def _recommended_tab_name(state: Dict[str, Any]) -> str:
    if state.get("presentation_path"):
        return "Exportar"
    if state.get("slide_plan"):
        return "Slides"
    if state.get("solo_learning_outcomes") and not state.get("structure_approved"):
        return "SOLO"
    if state.get("pedagogical_structure"):
        return "Estrutura"
    if state.get("content_analysis"):
        return "Análise"
    return "Estado"


def _render_outputs(state: Dict[str, Any]):
    presentation_path = state.get("presentation_path") or None
    file_update = gr.update(value=presentation_path) if presentation_path else gr.update()
    return (
        render_analysis_markdown(state.get("content_analysis", {})),
        render_solo_markdown(state),
        render_structure_markdown(state.get("pedagogical_structure", {})),
        render_slide_plan_markdown(state.get("slide_plan", [])),
        file_update,
        render_status_html(state),
    )


def _apply_chat_intent(state: Dict[str, Any], message: str, extracted: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    previous_state = dict(state)
    intent = extracted.get("user_intent", "unknown")
    state["last_user_message"] = message.strip()

    if intent == "restart":
        new_state = create_chat_initial_state()
        new_state["assistant_message"] = (
            "Processo reiniciado. Diz-me o tema, o público-alvo, o nível de ensino, o objetivo e, se quiseres, o texto-base ou ficheiros de apoio."
        )
        new_state["status"] = "initialized"
        return new_state, new_state["assistant_message"]

    state = _merge_extracted_into_state(state, extracted)

    if intent == "approve_analysis":
        if not state.get("content_analysis"):
            state["assistant_message"] = "Ainda não existe uma análise conceptual para aprovar."
            return state, state["assistant_message"]
        state["analysis_approved"] = True
        state = run_orchestrated_cycle(state)
        return state, _assistant_reply_from_state(previous_state, state, "Análise aprovada.")

    if intent == "approve_structure":
        if not state.get("pedagogical_structure"):
            state["assistant_message"] = "Ainda não existe uma estrutura pedagógica para aprovar."
            return state, state["assistant_message"]
        state["structure_approved"] = True
        state = run_orchestrated_cycle(state)
        return state, _assistant_reply_from_state(previous_state, state, "Estrutura e resultados SOLO aprovados.")

    if intent in {"regenerate_analysis", "unknown", "provide_requirements"} and state.get("next_action") == "wait_analysis_approval":
        feedback = extracted.get("feedback") or message.strip()
        state["analysis_feedback"] = feedback
        state["analysis_approved"] = False
        state["content_analysis"] = {}
        state["pedagogical_structure"] = {}
        state["solo_learning_outcomes"] = []
        state["structure_approved"] = False
        state["slide_plan"] = []
        state["presentation_path"] = ""
        state = run_orchestrated_cycle(state)
        return state, _assistant_reply_from_state(previous_state, state, "Análise reformulada.")

    if intent in {"regenerate_structure", "unknown", "provide_requirements"} and state.get("next_action") == "wait_structure_approval":
        feedback = extracted.get("feedback") or message.strip()
        state["structure_feedback"] = feedback
        state["analysis_approved"] = True
        state["structure_approved"] = False
        state["pedagogical_structure"] = {}
        state["solo_learning_outcomes"] = []
        state["slide_plan"] = []
        state["presentation_path"] = ""
        state = run_orchestrated_cycle(state)
        return state, _assistant_reply_from_state(previous_state, state, "Resultados SOLO e estrutura reformulados.")

    if intent in {"continue", "provide_requirements", "unknown"}:
        state = run_orchestrated_cycle(state)
        return state, _assistant_reply_from_state(previous_state, state, "Estado atualizado.")

    state["assistant_message"] = "Não consegui interpretar totalmente a tua mensagem, mas atualizei o estado com o que foi possível."
    return state, state["assistant_message"]


def handle_chat_message(app_state, chat_history, user_message, uploaded_files, upload_role):
    message = (user_message or "").strip()
    file_paths = _normalize_uploaded_files(uploaded_files)
    state: PrototypeState = dict(app_state) if app_state else create_chat_initial_state()
    history = list(chat_history or [])
    previous_state = dict(state)

    if not message and not file_paths:
        analysis_md, solo_md, structure_md, slides_md, file_output, status_html = _render_outputs(state)
        return (
            state,
            history,
            analysis_md,
            solo_md,
            structure_md,
            slides_md,
            file_output,
            status_html,
            gr.update(),
            gr.update(value=""),
            gr.update(value=[]),
            "",
        )

    file_notes: List[str] = []
    if file_paths:
        state, file_notes = add_uploaded_files_to_state(state, file_paths, selected_role=upload_role)

    if message:
        _append_turn(state, "user", message)
        history.append({"role": "user", "content": message})
        extracted = extract_chat_update(message, state)
        state, assistant_reply = _apply_chat_intent(state, message, extracted)
    else:
        state = run_orchestrated_cycle(state)
        assistant_reply = _assistant_reply_from_state(previous_state, state, "Ficheiros processados.")

    if file_notes:
        assistant_reply = "### Ficheiros processados\n" + "\n".join(file_notes) + ("\n\n" + assistant_reply if assistant_reply else "")

    _append_turn(state, "assistant", assistant_reply)
    history.append({"role": "assistant", "content": assistant_reply})

    analysis_md, solo_md, structure_md, slides_md, file_output, status_html = _render_outputs(state)

    # === SAFE AUTOMATIC TAB SWITCH ===
    tab_name = _recommended_tab_name(state)
    js_code = f"window.switchToTab('{tab_name}');" if tab_name != "Estado" else ""

    return (
        state,
        history,
        analysis_md,
        solo_md,
        structure_md,
        slides_md,
        file_output,
        status_html,
        gr.update(),           # Never change tab in the main event (fixes "processing" stuck)
        gr.update(value=""),
        gr.update(value=[]),
        js_code,
    )


def reset_chat():
    state = create_chat_initial_state()
    analysis_md, solo_md, structure_md, slides_md, file_output, status_html = _render_outputs(state)
    return (
        state,
        [],
        analysis_md,
        solo_md,
        structure_md,
        slides_md,
        file_output,
        status_html,
        gr.update(selected=TAB_STATUS),
        gr.update(value=""),
        gr.update(value=[]),
        "",
    )


def build_interface():
    with gr.Blocks(title="AI Multi-Agent Educational Generation") as demo:
        app_state = gr.State(create_chat_initial_state())

        # Hidden component to trigger JavaScript safely
        js_trigger = gr.Textbox(visible=False, elem_id="js_trigger")

        # Reliable JavaScript for automatic tab switching (after response is ready)
        demo.load(
            fn=None,
            js="""
            () => {
                window.switchToTab = function(tabName) {
                    console.log('[AutoTab] Trying to switch to: ' + tabName);
                    setTimeout(() => {
                        const tabs = document.querySelectorAll('.tabs-shell button');
                        for (let tab of tabs) {
                            if (tab.textContent.trim() === tabName) {
                                console.log('[AutoTab] ✓ Clicking tab: ' + tabName);
                                tab.click();
                                return;
                            }
                        }
                        console.log('[AutoTab] ✗ Tab not found: ' + tabName);
                    }, 250);
                };
            }
            """
        )

        with gr.Column(elem_classes=["app-shell"]):
            with gr.Column(elem_classes=["header-shell"]):
                gr.Markdown("# AI Multi-Agent Educational Generation")
                gr.Markdown(
                    "Protótipo com interação totalmente por chat: recolha de requisitos, aprovação e reformulação em linguagem natural, com anexos para briefing e grounding."
                )

            with gr.Row(elem_classes=["content-shell"], equal_height=True):
                with gr.Column(scale=8, elem_classes=["left-shell"]):
                    with gr.Accordion("Exemplos de mensagens", open=False, elem_classes=["help-shell"]):
                        gr.Markdown(CHATBOT_HELP)

                    chatbot = gr.Chatbot(
                        label="Conversa com o orquestrador",
                        height=260,
                        elem_id="chatbot-panel",
                    )

                    with gr.Column(elem_classes=["composer-shell"]):
                        with gr.Row(elem_classes=["composer-row"]):
                            chat_input = gr.Textbox(
                                label="Mensagem",
                                placeholder="Escreve aqui o tema, requisitos, feedback, aprovação ou instruções sobre os anexos...",
                                lines=4,
                                scale=8,
                                elem_classes=["composer-input"],
                            )
                            send_btn = gr.Button("Enviar", variant="primary", scale=1, elem_classes=["send-btn"])

                        with gr.Row(elem_classes=["attachment-controls"]):
                            attachment_input = gr.File(
                                label="Anexos",
                                file_count="multiple",
                                file_types=[".txt", ".md", ".pdf", ".docx", ".pptx", ".potx", ".png", ".jpg", ".jpeg", ".webp"],
                                type="filepath",
                                scale=5,
                            )
                            upload_role = gr.Dropdown(
                                label="Usar anexos como",
                                choices=["auto", "brief", "support", "visual", "template", "other"],
                                value="auto",
                                scale=2,
                                elem_classes=["attachment-role"],
                            )
                        reset_btn = gr.Button("Reiniciar conversa", elem_classes=["reset-btn"])

                with gr.Column(scale=5, elem_classes=["right-shell"]):
                    with gr.Tabs(selected=TAB_STATUS, elem_classes=["tabs-shell"]) as result_tabs:
                        with gr.Tab("Estado", id=TAB_STATUS):
                            status_output = gr.HTML(
                                render_status_html(create_chat_initial_state()),
                                elem_classes=["status-shell", "status-panel"],
                                height=690,
                            )
                        with gr.Tab("Análise", id=TAB_ANALYSIS):
                            analysis_output = gr.Markdown(
                                render_analysis_markdown({}),
                                elem_classes=["panel-shell", "result-panel"],
                                height=690,
                            )
                        with gr.Tab("SOLO", id=TAB_SOLO):
                            solo_output = gr.Markdown(
                                render_solo_markdown(create_chat_initial_state()),
                                elem_classes=["panel-shell", "result-panel"],
                                height=690,
                            )
                        with gr.Tab("Estrutura", id=TAB_STRUCTURE):
                            structure_output = gr.Markdown(
                                render_structure_markdown({}),
                                elem_classes=["panel-shell", "result-panel"],
                                height=690,
                            )
                        with gr.Tab("Slides", id=TAB_SLIDES):
                            slides_output = gr.Markdown(
                                render_slide_plan_markdown([]),
                                elem_classes=["panel-shell", "result-panel"],
                                height=690,
                            )
                        with gr.Tab("Exportar", id=TAB_EXPORT):
                            with gr.Column(elem_classes=["file-shell", "export-panel"]):
                                gr.Markdown(
                                    "## Exportação\n\nQuando a apresentação estiver pronta, o ficheiro aparecerá aqui para download."
                                )
                                pptx_output = gr.File(label="PowerPoint gerado")

        outputs = [
            app_state,
            chatbot,
            analysis_output,
            solo_output,
            structure_output,
            slides_output,
            pptx_output,
            status_output,
            result_tabs,
            chat_input,
            attachment_input,
            js_trigger,          # ← new hidden component for JS
        ]

        send_btn.click(
            fn=handle_chat_message,
            inputs=[app_state, chatbot, chat_input, attachment_input, upload_role],
            outputs=outputs,
        ).then(
            fn=None,
            inputs=[js_trigger],
            outputs=None,
            js="(js) => { if (js) eval(js); }"
        )

        chat_input.submit(
            fn=handle_chat_message,
            inputs=[app_state, chatbot, chat_input, attachment_input, upload_role],
            outputs=outputs,
        ).then(
            fn=None,
            inputs=[js_trigger],
            outputs=None,
            js="(js) => { if (js) eval(js); }"
        )

        reset_btn.click(
            fn=reset_chat,
            inputs=[],
            outputs=outputs,
        )

    return demo