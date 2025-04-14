# tak włączasz dzbanie
# cd "C:/Users/Mateusz/Desktop/EMS"
# python EMS.py


import discord
from discord.ext import commands
# filepath: [EMS.py](http://_vscodecontentref_/2)
import os
import mysql.connector
from urllib.parse import urlparse

# Pobierz URL bazy danych z zmiennej środowiskowej
db_url = os.getenv("MYSQL_URL")  # Upewnij się, że zmienna jest ustawiona w środowisku

# Rozbij URL na części
url = urlparse(db_url)

# Połączenie z bazą danych
db = mysql.connector.connect(
    host=url.hostname,
    user=url.username,
    password=url.password,
    database=url.path[1:],  # Pomija pierwszy znak "/" w nazwie bazy
    port=url.port
)

cursor = db.cursor()  # Utwórz obiekt kursora






intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

    @bot.command()
    async def dodaj_pracownika(ctx, imie: str, odznaka: str, przydzial: str = "member", specjalizacje: str = "Brak", szkolenia: str = "Brak"):
        # Dodaj użytkownika z przydziałem, specjalizacją i szkoleniami do bazy danych
        cursor.execute(
            "INSERT INTO main (Imie, Odznaka, Przydzial, Specjalizacje, Szkolenia) VALUES (%s, %s, %s, %s, %s)",
            (imie, odznaka, przydzial, specjalizacje, szkolenia)
        )
        db.commit()
        await ctx.send(f"Pracownik {imie} z przydziałem {przydzial}, odznaką {odznaka}, specjalizacją {specjalizacje} i szkoleniami {szkolenia} został dodany do bazy danych!")

    # Obsługa błędów dla `dodaj_pracownika`
    @dodaj_pracownika.error
    async def dodaj_pracownika_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Error: Musisz podać wszystkie wymagane argumenty! `!dodaj_pracownika <imie> <odznaka> <przydzial> <specjalizacje> <szkolenia>``(używaj podwójnego cudzysłowu dla wielowyrazowych argumentów)`")

@bot.command()
async def test(ctx):
    await ctx.send('działam!')

@bot.command()
async def pracownicy(ctx):
    # Pobierz użytkowników z bazy danych
    cursor.execute("SELECT Imie, Przydzial, Odznaka, Specjalizacje, Szkolenia FROM main")
    users = cursor.fetchall()

    if not users:
        await ctx.send("Brak pracowników w bazie danych!")
        return

    # Tworzenie listy użytkowników
    user_list = "\n".join(
        f"{user[0]} (Przydział: {user[1]} | Odznaka: {user[2]} | Specjalizacje: {user[3]} | Szkolenia: {user[4]})"
        for user in users
    )
    await ctx.send(f"Pracownicy w bazie danych:\n{user_list}")

    @bot.command()
    async def nowy_przydzial(ctx, imie: str, przydzial: str):
        # Zaktualizuj przydział użytkownika w bazie danych
        cursor.execute("UPDATE main SET Przydzial = %s WHERE Imie = %s", (przydzial, imie))
        db.commit()
        await ctx.send(f"Zaktualizowano przydział pracownika {imie} na {przydzial}!")

@bot.command()
async def nowa_odznaka(ctx, imie: str, odznaka: str):
    # Zaktualizuj odznakę użytkownika w bazie danych
    cursor.execute("UPDATE main SET Odznaka = %s WHERE Imie = %s", (odznaka, imie))
    db.commit()
    await ctx.send(f"Zaktualizowano odznakę pracownika {imie} na {odznaka}!")

@bot.command()
async def nowe_specjalizacje(ctx, imie: str, specjalizacje: str):
    # Zaktualizuj specjalizacje użytkownika w bazie danych
    cursor.execute("UPDATE main SET Specjalizacje = %s WHERE Imie = %s", (specjalizacje, imie))
    db.commit()
    await ctx.send(f"Zaktualizowano specjalizacje pracownika {imie} na {specjalizacje}!")

@bot.command()
async def nowe_szkolenia(ctx, Imie: str, Szkolenia: str):
    # Update the szkolenia of a user in the database
    cursor.execute("UPDATE main SET Szkolenia = %s WHERE Imie = %s", (Szkolenia, Imie))
    db.commit()
    await ctx.send(f"Zaktualizowano szkolenia pracownika {Imie} na {Szkolenia}!")

@bot.command()
async def szukaj_pracownika(ctx, odznaka: str):
    # Wyszukaj użytkownika w bazie danych na podstawie odznaki
    cursor.execute("SELECT Imie, Przydzial, Specjalizacje, Szkolenia FROM main WHERE Odznaka = %s", (odznaka,))
    user = cursor.fetchone()

    if user:
        await ctx.send(
            f"Znaleziono pracownika:\n"
            f"Imię: {user[0]}\n"
            f"Przydział: {user[1]}\n"
            f"Specjalizacja: {user[2]}\n"
            f"Szkolenia: {user[3]}"
        )
    else:
        await ctx.send(f"Nie znaleziono pracownika z odznaką: {odznaka}")

@bot.command()
async def usun_pracownika(ctx, Imie: str = None, odznaka: str = None):
    # Usuń użytkownika na podstawie username lub odznaki
    if Imie:
        cursor.execute("DELETE FROM main WHERE Imie = %s", (Imie,))
        db.commit()
        await ctx.send(f"Pracownik {Imie} został usunięty z bazy danych!")
    elif odznaka:
        cursor.execute("DELETE FROM main WHERE odznaka = %s", (odznaka,))
        db.commit()
        await ctx.send(f"Pracownik z odznaką {odznaka} został usunięty z bazy danych!")
    else:
        await ctx.send("Musisz podać `Imie` lub `odznaka`, aby usunąć pracownika!")


bot.run(os.getenv("DISCORD_BOT_TOKEN"))