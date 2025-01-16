from aiogram import  Dispatcher
from aiogram.types import Update
from fastapi import FastAPI, HTTPException,status,Depends,BackgroundTasks, Form
from fastapi.security import APIKeyQuery
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
from pydantic import BaseModel
from contextlib import asynccontextmanager
from biznesLogic import router, logger,send_telegram_message
from init import (bot,SERV,WebhookURL,URL,PASSWORD,AdminIDSerg,DataBase, modelEmbed ,
                  client,collection_name, modelsqd)
from fastapi.middleware.cors import CORSMiddleware

dp = Dispatcher()
dp.include_routers(router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if SERV:
        await bot.set_webhook(url=WebhookURL,
                                  allowed_updates=dp.resolve_used_update_types(),
                                  drop_pending_updates=True)
        yield
        await bot.delete_webhook()
    else:
        await bot.delete_webhook()
        polling_task = asyncio.create_task(dp.start_polling(bot))
        yield
        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            pass


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

origins = [
   "http://localhost",
   "http://127.0.0.1",
   "http://localhost:5173",
    "http://zelse.asuscomm.com:5000/",
    "http://zelse.asuscomm.com"

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(f'/{URL}/webhook')
async def webhook(request: Request) -> None:
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)

  # статичний пароль
api_key_query = APIKeyQuery(name="password", auto_error=False)

def get_password(password: str = Depends(api_key_query)): # функція перевірки паролю
    if password != PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )
    return password


class QAData(BaseModel):
    id: int
    question: str
    answer: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, password: str = Depends(get_password)):
    """Веб-інтерфейс для редагування даних."""
    return templates.TemplateResponse('adminkaINFO.html', {
        "request": request,
        "URL":URL,  })


@app.get("/get_all", response_model=list[QAData])
async def get_all_data():
    """Отримує всі дані з колекції Qdrant."""
    results = client.scroll(collection_name=collection_name, limit=100)
    data = [
        {
            "id": point.id,
            "question": point.payload.get("question"),
            "answer": point.payload.get("answer")
        }
        for point in results[0]
    ]
    return data

@app.post("/update_all")
async def update_all_data(data: list[QAData]):
    """Оновлення даних."""
    points = []
    for item in data:
        vector = modelEmbed.encode(item.question).tolist()
        points.append(modelsqd.PointStruct(
            id=item.id,
            vector=vector,
            payload={"question": item.question, "answer": item.answer}
        ))

    client.upsert(collection_name=collection_name, points=points)
    return {"message": "Дані успішно оновлені!"}

@app.get("/add-data")
async def add_data():
    # Отримуємо кількість існуючих записів у колекції
    existing_points = client.count(collection_name=collection_name).count

    # Генеруємо новий ідентифікатор (наприклад, на основі кількості записів)
    new_id = existing_points + 1

    # Додаємо пустий запис
    client.upsert(
        collection_name=collection_name,
        points=[
            modelsqd.PointStruct(
                id=new_id,
                vector=[0] * 384,  # Порожній вектор, наприклад, нульовий
                payload={
                    "question": "",  # Порожнє питання
                    "answer": ""  # Порожня відповідь
                }
            )
        ]
    )

    print(f"Додано новий пустий запис з ID {new_id}.")

    return RedirectResponse("/", status_code=302)


async def mybroadcast(bro):
    records = await DataBase.getUserId()
    for telegram_id in records:
        await send_telegram_message(telegram_id, bro)
        #await bot.send_message(AdminIDSerg, f"Надіслано повідомлення користувачу {telegram_id}")
        await asyncio.sleep(3)

@app.get(f'/{URL}/broadcast')
async def broadcast(request: Request, background_tasks: BackgroundTasks, bro = None):
    if not bro:
        raise HTTPException(status_code=400, detail="Повідомлення не надано")

    background_tasks.add_task(mybroadcast, bro)
    return RedirectResponse(url=f'/?password={PASSWORD}', status_code=302)

@app.on_event("startup")
async def startup_event():
    logger.info(f"Старт бота")
   # scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Зупинка бота")

if __name__ == "__main__":
    port = 3021 if SERV else 5000
    uvicorn.run(app, host="0.0.0.0", port=port)