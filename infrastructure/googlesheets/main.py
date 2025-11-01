import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class GoogleSheet:
    def __init__(self, spreadsheet_id: str, scopes: list = SCOPES) -> None:
        self.spreadsheet_id = spreadsheet_id
        self.scopes = scopes
        self.sheet: gspread.Spreadsheet = self.init_sheet()

    def init_sheet(self):
        creds = Credentials.from_service_account_file("token.json", scopes=self.scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(self.spreadsheet_id)
        return sheet

    def update(self, worksheet_name: str, lists):
        if worksheet_name == "Заявки пользователей":
            worksheet = self.sheet.worksheet(worksheet_name)
            print(worksheet)
            worksheet.update(
                [
                    [
                        "Имя",
                        "Контакты",
                        "Тип операции",
                        "Тип объекта",
                        "Примечание",
                        "Дата",
                    ],
                    *lists,
                ],
                f"A1:F{len(lists) + 1}",
            )
        elif worksheet_name == "Заявки на консультацию":
            worksheet = self.sheet.worksheet(worksheet_name)
            print(worksheet)
            worksheet.update(
                [["ФИО", "Номер телефона", "Дата"], *lists], f"A1:C{len(lists)+1}"
            )
