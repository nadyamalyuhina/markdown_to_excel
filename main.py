import sys
from pathlib import Path

from parser import parse_md
from exporter import export_xlsx


def convert(md_path: str) -> None:
    """Конвертирует .md в .xlsx c сохранением имени."""
    entries = parse_md(md_path)
    xlsx_path = Path(md_path).with_suffix(".xlsx")
    export_xlsx(entries, xlsx_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python main.py '<path_to_md>'")
        sys.exit(1)
    
    try:
        convert(sys.argv[1])
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
