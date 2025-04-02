# update_db.py
import requests
import pandas as pd
import sqlite3
import os

# --- Настройки ---
EXCEL_URL = "https://fish-business.ru/upload/База%20данных_КонтрагентыСИННИГоловой%20XLSX.xlsx"
EXCEL_FILE = "contractors.xlsx"
DB_FILE = "contractors.db"
TABLE_NAME = "contractors"

def update_database():
    try:
        print("⬇️ Загружаем файл...")
        response = requests.get(EXCEL_URL)
        response.raise_for_status()

        with open(EXCEL_FILE, "wb") as f:
            f.write(response.content)

        print("📖 Читаем Excel...")
        df = pd.read_excel(EXCEL_FILE)

        # Берем только первые 2 столбца — ИНН и Название
        df = df.iloc[:, :2]
        df.columns = ["inn", "name"]  # Переименуем колонки для универсальности

        print("💾 Сохраняем в базу данных...")
        conn = sqlite3.connect(DB_FILE)
        df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
        conn.close()

        print("✅ Обновление базы завершено успешно.")
    except Exception as e:
        print(f"❌ Ошибка при обновлении базы данных: {e}")

if __name__ == "__main__":
    update_database()