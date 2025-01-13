import aiosqlite
import os
import datetime

class BotBD:
    def __init__(self) -> None:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "dbUsers.db")
        self.db_path = db_path

    async def is_subscriber_exists(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT telegramId FROM users") as cursor:
                rows = await cursor.fetchall()
                for i in rows:
                    if user_id == int(i[0]):
                        return True
        return False

    async def add_subscriber(self, user_id,nicname):
        date_now = datetime.datetime.now().strftime("%Y-%m-%d")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT INTO users (telegramId, subscribeDate, nicName) VALUES (?, ?, ?)", (user_id, date_now, nicname))
            await db.commit()



    async def getUserId(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT DISTINCT telegramId FROM users WHERE telegramId NOT NULL") as cursor:
                rows = await cursor.fetchall()
                return [i[0] for i in rows]

    async def getUserIdTEST(self):
        return [1080587853,1080587853,1080587853,1080587853,1080587853]

    async def getAllUsers(self):
        today = datetime.date.today()  # Отримуємо сьогоднішню дату
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT telegramId, number_of_requests, requestsCurentDate, curentDate 
                FROM users 
                WHERE curentDate = ?
                ORDER BY number_of_requests DESC
            """, (today,)) as cursor:
                rows = await cursor.fetchall()
                return '\n'.join([f"{i[0]} - ({i[1]}/{i[2]})" for i in rows[:30]])

    async def usersCount(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT DISTINCT telegramId FROM users") as cursor:
                rows = await cursor.fetchall()
                return len(rows)

    async def addNewResponse(self,text, user_id,nicname):
        date_now = datetime.datetime.now()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT INTO UserResponse (telegramID, nicname, text, createdate) VALUES (?, ?, ?, ?)", (user_id,nicname,text, date_now))
            await db.commit()

    async def getAllResponse(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT telegramID, nicname, text, createdate FROM UserResponse") as cursor:
                rows = await cursor.fetchall()
                return rows
               # return '\n'.join([f"{i[0]} - {i[1]}" for i in rows])

    async def getUsers(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT nicName,telegramID, subscribeDate, number_of_requests, paymentStatus, paymantsDate FROM users ORDER BY number_of_requests DESC") as cursor:
                rows = await cursor.fetchall()
                return rows