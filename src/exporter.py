import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ReportExporter:
    """
    Manages generation and local disk storage of markdown newsletters.
    """
    def __init__(self, output_dir: str = "./news_reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def save_report(self, frequency: str, summary_content: str) -> str:
        """
        Save formatted markdown summary to disk with timestamp metadata.
        """
        freq_name = frequency.capitalize()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        filename = f"{frequency.lower()}_ai_digest_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)

        header = f"# 📰 {freq_name} Artificial Intelligence Industry Digest\n"
        header += f"**Generated Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(header + summary_content)

        logger.info(f"Saved news summary digest to '{filepath}'.")
        return filepath
