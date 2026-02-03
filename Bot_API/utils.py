from pathlib import Path
import csv

# 1. Получаем путь к папке, где лежит текущий файл (utils)
utils_path = Path(__file__).resolve().parent

# 2. Поднимаемся на уровень выше к корню проекта (parent) и переходим в папку downloaded
PROJECT_ROOT = utils_path.parent
FILE_PATH = PROJECT_ROOT / 'downloaded' / 'profile.csv'


#####################################################
# The function pars profile from CSV
def pars_profile():
    if not FILE_PATH.exists():
        print(f"Файл не найден по пути: {FILE_PATH}")
        return []

    with open(FILE_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

#####################################################
# The function checks for a subscription; if there is one, it returns a vacancy with contacts.
def create_vacancy_text(vacancy, has_sub):
    text = (f"📌 <b>{vacancy.name_vacancy}</b>\n\n"
            f"🏢 Company: {vacancy.name_company}\n"
            f"💰 Salary: {vacancy.salary if vacancy.salary else 'not specified'}\n"
            f"📍 Geolocation: {vacancy.geolocation}\n\n"
            f"🔖 Description: {vacancy.description}\n\n"
            f"💎 Requirements: {vacancy.requirement}\n")

    if has_sub:
        text += f"\n<b>Contact:</b> {vacancy.contact}"
    else:
        text += f"\n<b>Contact:</b> 🔒 <i>Доступно только по подписке</i>"

    return text

#####################################################
