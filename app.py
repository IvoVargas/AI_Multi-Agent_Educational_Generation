from src.config import LOG_LEVEL
from src.ui.gradio_ui import build_interface
from src.utils.logging_utils import setup_logging

setup_logging(LOG_LEVEL)

app = build_interface()

if __name__ == "__main__":
    app.launch()