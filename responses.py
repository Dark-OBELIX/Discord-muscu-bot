from random import choice
from database import DatabaseHandler
from typing import List, Tuple

def format_session_details(results: List[Tuple], session_number: int) -> str:
    """
    Formate les résultats de la séance en une chaîne lisible, incluant le numéro de séance.
    :param results: Liste de tuples contenant les détails des exercices.
    :param session_number: Le numéro de la séance.
    :return: Une chaîne formatée.
    """
    if not results:
        return f"Aucune séance trouvée pour le numéro {session_number}."

    formatted_result = f"Voici les détails de votre séance {session_number} :\n"
    for exo, groupe, reps, sets, poids in results:
        formatted_result += f"- **{exo}** ({groupe}): {sets} sets x {reps} reps à {poids} kg\n"

    return formatted_result

def get_response(userid : int, user_input: str, sender: str, db_handler: DatabaseHandler):
    """
    Gère la réponse en fonction de l'entrée utilisateur.
    :param user_input: Le message de l'utilisateur
    :param sender: Le nom de l'utilisateur
    :param db_handler: Instance pour les requêtes à la base de données
    :return: Une réponse texte ou un tuple (texte, emoji)
    """
    lowered = user_input.lower()

    # Salutations
    if 'hello' in lowered:
        return (f"Hello there, {sender}!", "👋")

    elif 'how are you' in lowered:
        return "I'm good, thanks for asking!"

    elif 'bye' in lowered:
        return "See you soon! 👋"

    # Commande "séance"
    elif 'séance' in lowered:
        session_number = ''.join(filter(str.isdigit, lowered))
        if session_number:
            results = db_handler.get_session_details(userid, session_number=int(session_number))
            return format_session_details(results, session_number)
        else:
            return "Merci de spécifier un numéro de séance valide, par exemple : 'séance 3'."

    # Réponse par défaut
    else:
        return choice([
            "Je ne comprends pas ta demande. Essaie 'hello' ou 'séance X'.",
            "Peux-tu reformuler ? Je n'ai pas compris.",
            "Commande inconnue. Tape 'séance 3' pour voir une séance d'exemple."
        ])