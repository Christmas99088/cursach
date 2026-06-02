import time

import uvicorn
from fastapi import FastAPI

from SERVER.BD import SessionDep
from SERVER.Models import *

from sqlalchemy import text


app = FastAPI()


@app.get("/ping")
async def root():
    return "PONG"


@app.get("/")
async def get_(data: GET, session: SessionDep):
    try:
        result = await session.execute(text(data.SQL))

        # Получаем все строки как словари
        rows = result.mappings().all()

        # Преобразуем в список словарей
        data_list = []
        for row in rows:
            data_list.append(dict(row))

        return data_list
    except Exception as e:
        print(e)
        return 400

@app.post("/")
async def post(data: POST, session: SessionDep):
    try:
        print(data.SQL)
        await session.execute(text(data.SQL))
        await session.commit()

        return 200
    except Exception as e:
        print(e)
        await session.rollback()
        return 400

@app.delete("/")
async def delete_(data: DELETE, session: SessionDep):
    try:
        await session.execute(text(data.SQL))
        await session.commit()
        return 200
    except Exception as e:
        print(e)
        await session.rollback()
        return 400


@app.get("/")
async def update(data: UPDATE, session: SessionDep):
    try:
        await session.execute(text(data.SQL))
        await session.commit()
        return True
    except Exception as e:
        print(e)
        await session.rollback()
        return False




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)