from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, Reaction, User
from responses import get_response
from database import DatabaseHandler
import re
# STEP 0: LOAD OUR TOKEN FROM ENVIRONMENT VARIABLES
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# STEP 1: BOT SETUP
intents: Intents = Intents.default()
intents.message_content = True
intents.reactions = True
client: Client = Client(intents=intents)

# STEP 2: DATABASE HANDLER
db_handler = DatabaseHandler("Muscu.db")

# STEP 3: MESSAGE FUNCTIONALITY
async def send_message(message: Message, user_message: str, user: User) -> None:
    print("send messages")
    if not user_message:
        return

    try:
        response = get_response(user.id, user_message, str(message.author), db_handler)

        print(user.id, user_message, str(message.author), db_handler)
        # Gestion des réponses avec emoji
        if isinstance(response, tuple):
            text, emoji = response
            bot_message = await message.channel.send(text)
            await bot_message.add_reaction(emoji)
        else:
            bot_message = await message.channel.send(response)

        # Ajout des réactions pour la commande "séance"
        if "détails de votre séance" in response:
            await bot_message.add_reaction("⚙️")
            await bot_message.add_reaction("💪")
            await bot_message.add_reaction("✅")

    except Exception as e:
        print(f"Erreur : {e}")

# STEP 4: HANDLING STARTUP
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')

# Function to add a new user to the database
async def add_new_user(user: User) -> None:
    if not db_handler.user_exists(user.id):
        db_handler.add_user(user.id, user.name)
        await user.send(f"Bienvenue {user.name}! Vous avez été ajouté à la base de données. Veuillez choisir un nom d'utilisateur en répondant avec !setname <votre_nom>.")

# Function to set the username
async def set_username(user: User, username: str) -> None:
    db_handler.update_username(user.id, username)
    await user.send(f"Votre nom d'utilisateur a été mis à jour en {username}.")


# STEP 5: HANDLING INCOMING MESSAGES
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    # Check if the user is new and add them to the database
    await add_new_user(message.author)

    user_message = message.content

    # Handle setting the username
    if user_message.startswith("!setname "):
        new_username = user_message.split(" ", 1)[1]
        await set_username(message.author, new_username)
        return

    await send_message(message, user_message, message.author)

@client.event
async def on_reaction_add(reaction: Reaction, user: User) -> None:
    if user.bot:
        return

    if reaction.emoji == "✅" and reaction.message.author == client.user:
        # Recherche du numéro de séance avec une expression régulière
        match = re.search(r"séance (\d+)", reaction.message.content)
        
        if match:
            session_number = int(match.group(1))  # Numéro de la séance
            user_id = user.id  # Utiliser l'ID de l'utilisateur qui réagit
            print("ID : ", user_id, "SEssion number", session_number)
            # Récupérer les détails de la séance
            results = db_handler.get_session_details(user_id=user_id, session_number=session_number)

            # Ajouter ces détails dans la table "Table_historique"
            for exo, groupe, reps, sets, poids in results:
                db_handler.insert_into_historique(user_id=user_id, session_number=session_number, exo=exo, groupe=groupe, reps=reps, sets=sets, poids=poids)
            
            await reaction.message.channel.send(f"Les détails de la séance {session_number} ont été ajoutés à votre historique ! 🎉")
        else:
            # Si aucun numéro de séance n'a été trouvé
            await reaction.message.channel.send("Impossible de récupérer le numéro de séance. Assurez-vous que le message du bot contient le mot 'séance' suivi du numéro.")
            
# STEP 7: MAIN ENTRY POINT
def main() -> None:
    client.run(TOKEN)

if __name__ == '__main__':
    main()