from src.ui.gradio_ui import build_interface

app = build_interface()

if __name__ == "__main__":
    app.launch()