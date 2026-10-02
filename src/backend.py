from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn

app = FastAPI()

# Хранилище данных
items_db = {}
next_id = 1


# Модель данных
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    category: str
    value: float
    updated_at: str
    active: bool


# Инициализация данными
def init_db():
    global next_id
    sample_items = [
        {"id": 1, "name": "Товар А", "category": "Электроника", "value": 150.5,
         "updated_at": "2024-01-15", "active": True},
        {"id": 2, "name": "Товар Б", "category": "Бытовая техника", "value": 2300.0,
         "updated_at": "2024-02-20", "active": False},
        {"id": 3, "name": "Товар В", "category": "Электроника", "value": 0.0,
         "updated_at": "2024-03-10", "active": True},
    ]
    for item in sample_items:
        items_db[item["id"]] = item
        if item["id"] >= next_id:
            next_id = item["id"] + 1


init_db()


# GET /api/items - получить все
@app.get("/api/items")
async def get_items():
    return list(items_db.values())


# GET /api/items/{id} - получить один
@app.get("/api/items/{item_id}")
async def get_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]


# POST /api/items - создать
@app.post("/api/items")
async def create_item(item: Item):
    global next_id
    new_id = next_id
    next_id += 1
    item_dict = item.dict()
    item_dict["id"] = new_id
    items_db[new_id] = item_dict
    return {"id": new_id, "message": "Item created"}


# PUT /api/items/{id} - полностью обновить
@app.put("/api/items/{item_id}")
async def update_item(item_id: int, item: Item):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    item_dict = item.dict()
    item_dict["id"] = item_id
    items_db[item_id] = item_dict
    return {"message": "Item updated"}


# PATCH /api/items/{id} - частично обновить
@app.patch("/api/items/{item_id}")
async def patch_item(item_id: int, item: dict):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item.items():
        if key in items_db[item_id]:
            items_db[item_id][key] = value
    return {"message": "Item patched"}


# DELETE /api/items/{id} - удалить
@app.delete("/api/items/{item_id}")
async def delete_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]
    return {"message": "Item deleted"}


# GET /dynamic - динамическая страница
@app.get("/dynamic")
async def dynamic_page():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Динамическая страница</title>
        <style>
            table { border-collapse: collapse; margin: 20px 0; }
            th, td { border: 1px solid #ddd; padding: 8px; }
            th { background-color: #f2f2f2; }
            .container { padding: 20px; font-family: Arial; }
            button { padding: 10px 20px; margin: 10px 0; font-size: 16px; cursor: pointer; }
            select { padding: 10px; font-size: 16px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Динамическая загрузка данных</h1>
            <button onclick="loadData()">Загрузить данные</button>
            <br>
            <label>Фильтр по категории: 
                <select id="categoryFilter" onchange="filterData()">
                    <option value="all">Все категории</option>
                    <option value="Электроника">Электроника</option>
                    <option value="Бытовая техника">Бытовая техника</option>
                    <option value="Мебель">Мебель</option>
                </select>
            </label>
            <div id="dataContainer">
                <p>Нажмите кнопку для загрузки данных...</p>
            </div>
        </div>
        <script>
            let allData = [];

            function loadData() {
                fetch('/api/items')
                    .then(response => response.json())
                    .then(data => {
                        allData = data;
                        renderTable(data);
                    })
                    .catch(error => {
                        document.getElementById('dataContainer').innerHTML = 
                            '<p style="color: red;">Ошибка загрузки: ' + error + '</p>';
                    });
            }

            function renderTable(data) {
                if (!data || data.length === 0) {
                    document.getElementById('dataContainer').innerHTML = 
                        '<p>Нет данных для отображения</p>';
                    return;
                }

                let html = '<table>';
                html += '<tr><th>ID</th><th>Название</th><th>Категория</th><th>Значение</th><th>Дата</th><th>Активен</th></tr>';

                data.forEach(item => {
                    html += '<tr>';
                    html += '<td>' + item.id + '</td>';
                    html += '<td>' + item.name + '</td>';
                    html += '<td>' + item.category + '</td>';
                    html += '<td>' + item.value + '</td>';
                    html += '<td>' + item.updated_at + '</td>';
                    html += '<td>' + (item.active ? 'Да' : 'Нет') + '</td>';
                    html += '</tr>';
                });

                html += '</table>';
                html += '<p>Всего записей: ' + data.length + '</p>';
                document.getElementById('dataContainer').innerHTML = html;
            }

            function filterData() {
                const filter = document.getElementById('categoryFilter').value;
                if (filter === 'all') {
                    renderTable(allData);
                } else {
                    const filtered = allData.filter(item => item.category === filter);
                    renderTable(filtered);
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html, media_type="text/html")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)