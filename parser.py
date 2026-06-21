import re
from pathlib import Path
from typing import TypedDict

class Entry(TypedDict):
    Header: str
    Number: str
    Text: str
    Link: str

class MarkdownParser:
    HEADER_RE = re.compile(r'\\(?:title|section\*)\{ЧАСТЬ (\d+)\}')
    NUMBER_RE = re.compile(r'^([АВСABC]\d+)\s+(.+)')
    LINK_RE = re.compile(r'!\[(?:[^\]]*)\]\((.+)\)')


    def __init__(self) -> None:
        self._accumulate_header: bool = False
        self._header_accum: list[str] = []
        self.entries: list[Entry] = []
        self.current_header: str = ""
        self.current_number: str = ""
        self.current_text: list[str] = []
        self.current_link: str = ""

    def parse(self, path: str) -> list[Entry]:
        """Точка входа: парсит файл и возвращает список записей."""
        if not Path(path).exists():
            raise FileNotFoundError(f"Файл не найден: {path}")
        
        self._reset_state()
        
        with open(path, encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.rstrip("\n")
                self._process_line(line)
        
        self._save_entry()  # последняя запись
        return self.entries

    def _reset_state(self) -> None:
        """Сброс состояния перед парсингом (для повторного использования)."""
        self.entries = []
        self.current_header = ""
        self.current_number = ""
        self.current_text = []
        self.current_link = ""
        self._accumulate_header = False
        self._header_accum = []

    def _process_line(self, line: str) -> None:
        """Диспетчер: определяет тип строки и делегирует обработку."""
         # 0. Накопление многострочного заголовка (приоритет выше всего)
        if self._accumulate_header:
            if "}" in line:
                self._header_accum.append(line[:line.index("}") + 1])
                full = "".join(self._header_accum)
                if m := self.HEADER_RE.match(full):
                    self._save_entry()
                    self.current_header = m.group(1)
                self._accumulate_header = False
                self._header_accum = []
            else:
                self._header_accum.append(line)
            return

        # 1. Начало многострочного заголовка
        if (line.startswith("\\title{") or line.startswith("\\section*{")) and "}" not in line:
            self._accumulate_header = True
            self._header_accum = [line]
            return

        # 2. Однострочный заголовок
        if m := self.HEADER_RE.match(line):
            self._save_entry()
            self.current_header = m.group(1)
            return
        
        # 3. Номер вопроса + начало текста
        if m := self.NUMBER_RE.match(line):
            self._save_entry()
            self.current_number = m.group(1)
            self.current_text = [m.group(2)]
            self.current_link = ""
            return

        # 4. Ссылка на изображение
        if m := self.LINK_RE.match(line):
            self.current_link = m.group(1)
            return

        # 5. Продолжение текста вопроса (пустые строки тоже сохраняются)
        if self.current_number:
            self.current_text.append(line)

    def _save_entry(self) -> None:
        """Сохраняет накопленную запись, если есть номер и текст."""
        if not self.current_number or not self.current_text:
            return
        
        self.entries.append(Entry(
            Header=self.current_header,
            Number=self.current_number,
            Text="\n".join(self.current_text).strip(),
            Link=self.current_link,
        ))
        # Сброс только полей записи, header сохраняется
        self.current_number = ""
        self.current_text = []
        self.current_link = ""


# Обратная совместимость: функция-обёртка
def parse_md(path: str) -> list[Entry]:
    """Парсит .md файл и возвращает список задач."""
    parser = MarkdownParser()
    return parser.parse(path)
