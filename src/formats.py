import pandas as pd
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
import os


def read_csv(file_path):
    """Чтение CSV через pandas"""
    return pd.read_csv(file_path)


def read_json(file_path):
    """Чтение JSON"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return pd.DataFrame(data)


def read_xml(file_path):
    """Чтение XML через xml.etree.ElementTree"""
    tree = ET.parse(file_path)
    root = tree.getroot()
    data = []
    for item in root.findall('item'):
        row = {}
        for child in item:
            row[child.tag] = child.text
        data.append(row)
    return pd.DataFrame(data)


def analyze_df(df, source_name):
    """Анализ DataFrame"""
    print(f"\n{'=' * 50}")
    print(f"Источник: {source_name}")
    print(f"{'=' * 50}")
    print(f"Количество записей: {len(df)}")
    print(f"Столбцы: {list(df.columns)}")
    print(f"Типы данных:\n{df.dtypes}")
    print(f"Пропущенные значения:\n{df.isnull().sum()}")
    duplicates = df[df.duplicated(subset=['id'], keep=False)]
    print(f"Повторяющиеся id: {len(duplicates) if not duplicates.empty else 0}")
    if not duplicates.empty:
        print(f"Повторяющиеся id: {duplicates['id'].tolist()}")
    return df


def normalize_items(df):
    """
    Нормализация данных к единой схеме
    """
    df = df.copy()

    # 1. Приводим id к int
    df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)

    # 2. Приводим name к строке
    df['name'] = df['name'].astype(str)

    # 3. Нормализуем категории (первая буква заглавная, остальные строчные)
    df['category'] = df['category'].str.capitalize()

    # 4. Приводим value к float
    df['value'] = pd.to_numeric(df['value'], errors='coerce')

    # 5. Приводим updated_at к datetime
    df['updated_at'] = pd.to_datetime(df['updated_at'], errors='coerce')

    # 6. Приводим active к boolean
    df['active'] = df['active'].astype(str).str.lower()
    df['active'] = df['active'].map({'true': True, 'false': False, '1': True, '0': False})
    df['active'] = df['active'].fillna(False)

    # 7. Удаляем полные дубликаты
    df = df.drop_duplicates()

    return df


def resolve_conflicts(df, id_col='id'):
    """
    Разрешение конфликтов при одинаковых id
    Правило: оставляем запись с самой свежей датой updated_at
    """
    df = df.copy()
    df = df.sort_values('updated_at', ascending=False)
    df = df.drop_duplicates(subset=[id_col], keep='first')
    return df


def save_processed(df, base_path='data/processed'):
    """Сохранение обработанных данных в трех форматах"""
    Path(base_path).mkdir(parents=True, exist_ok=True)

    # CSV
    df.to_csv(f'{base_path}/items_normalized.csv', index=False, encoding='utf-8-sig')

    # JSON
    df.to_json(f'{base_path}/items_normalized.json', orient='records', force_ascii=False, indent=2)

    # XML
    root = ET.Element('items')
    for _, row in df.iterrows():
        item = ET.SubElement(root, 'item')
        for col in df.columns:
            child = ET.SubElement(item, col)
            child.text = str(row[col])
    tree = ET.ElementTree(root)
    tree.write(f'{base_path}/items_normalized.xml', encoding='utf-8', xml_declaration=True)


def main():
    """Главная функция этапа A"""
    print("\n" + "=" * 60)
    print("ЭТАП A: РАБОТА С ФОРМАТАМИ ДАННЫХ")
    print("=" * 60)

    # Чтение данных
    csv_df = read_csv('data/raw/items.csv')
    json_df = read_json('data/raw/items.json')
    xml_df = read_xml('data/raw/items.xml')

    # Анализ каждого источника
    analyze_df(csv_df, "CSV")
    analyze_df(json_df, "JSON")
    analyze_df(xml_df, "XML")

    # Нормализация
    csv_norm = normalize_items(csv_df)
    json_norm = normalize_items(json_df)
    xml_norm = normalize_items(xml_df)

    # Объединение
    combined = pd.concat([csv_norm, json_norm, xml_norm], ignore_index=True)

    # Разрешение конфликтов
    combined = resolve_conflicts(combined, 'id')

    print(f"\nПосле объединения и разрешения конфликтов:")
    print(f"Всего записей: {len(combined)}")
    print(f"Уникальных id: {combined['id'].nunique()}")

    # Сохранение
    save_processed(combined)
    print("\nДанные сохранены в data/processed/")

    return combined


if __name__ == "__main__":
    main()