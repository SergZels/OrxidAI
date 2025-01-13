from aiogram import  Dispatcher
from aiogram.types import Update
from fastapi import FastAPI, HTTPException,status,Depends,BackgroundTasks, Form
from fastapi.security import APIKeyQuery
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
import uvicorn
import asyncio

from contextlib import asynccontextmanager
from biznesLogic import router, logger,send_telegram_message
from init import bot,SERV,WebhookURL,URL,PASSWORD,AdminIDSerg,DataBase
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



@app.get(f'/{URL}', response_class=HTMLResponse)
async def adminka(request: Request, password: str = Depends(get_password)):

    logger.info(f"Вхід в адмінку")
    return "CB bot"


async def mybroadcast(bro):
    # records = await botBD.getUserId()
    # for telegram_id in records:
    #     await send_telegram_message(telegram_id, bro)
    #     #await bot.send_message(AdminIDSerg, f"Надіслано повідомлення користувачу {telegram_id}")
    #     await asyncio.sleep(3)
    pass

@app.post(f"/{URL}/broadcast")
async def start_broadcast(
        brotext: str = Form(...),  # Отримуємо дані як form-data
        sec: str = Form(...),  # Також form-data
        background_tasks: BackgroundTasks = BackgroundTasks()
):
    if sec=="1432":
        background_tasks.add_task(mybroadcast, brotext)
        return {"status": "Broadcast started!"}
    else:
        raise HTTPException(status_code=400, detail="Invalid secret key")

@app.get(f"/{URL}/api/users")
async def get_users():
    pass
   # users = await botBD.getUsers()
    #return {'users': users}

@app.get(f"/{URL}/api/response")
async def get_users():
    pass
    # resp = await botBD.getAllResponse()
   # return {'response': resp}

# @app.get(f"/{URL}/logs", response_class=HTMLResponse)
# async def get_logs(request: Request):
#     log_file_path = "Logfile.txt"  # Вкажіть шлях до вашого файлу логів
#     if os.path.exists(log_file_path):
#         try:
#             with open(log_file_path, "r", encoding="utf-8") as file:
#                 content = file.readlines()
#                 last_100_lines = ''.join(content[-100:])
#             html_content = f"""
#                 <html>
#                     <body>
#                         <h1>Логи</h1>
#                         <pre>{last_100_lines}</pre>
#                     </body>
#                 </html>
#                 """
#             return HTMLResponse(content=html_content)
#         except:
#             print("файл не відкрився")
#     else:
#         return "<html><body><h1>Файл логів не знайдено</h1></body></html>"

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