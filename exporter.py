from openpyxl import Workbook


def export_xlsx(entries: list[dict], path: str) -> None:
    """Записывает список задач в .xlsx файл."""
    wb = Workbook()
    ws = wb.active
    ws.append(["Часть", "Номер вопроса", "Вопрос", "Рисунок"])
    for entry in entries:
        ws.append([entry["Header"], entry["Number"], entry["Text"], entry["Link"]])
    wb.save(path)
