import sqlite3
from typing import List, Tuple

class DatabaseHandler:
    def __init__(self, db_path: str):
        """
        Initialise la connexion à la base de données.
        :param db_path: Chemin vers le fichier SQLite.
        """
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Permet un accès plus lisible aux colonnes

    def get_session_details(self, user_id: int, session_number: int) -> List[Tuple]:
        """
        Récupère les détails de la séance pour un utilisateur donné.
        :param user_id: L'ID de l'utilisateur.
        :param session_number: Le numéro de la séance.
        :return: Liste de tuples contenant les détails des exercices.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT TABLE_exo.exo, TABLE_exo.groupe_musculaire, TABLE_exo.REPS,
                       TABLE_exo.SETS, TABLE_exo.POIDS
                FROM TABLE_seance
                INNER JOIN TABLE_exo ON TABLE_seance.ID_exo = TABLE_exo.ID_exo
                WHERE TABLE_seance.ID_user = ? AND TABLE_seance.ID_seance_user = ?
            """, (user_id, session_number))

            results = cursor.fetchall()
            return results

        except sqlite3.Error as e:
            print(f"Erreur SQLite : {e}")
            return []
        finally:
            cursor.close()

    def insert_into_historique(self, user_id: int, session_number: int, exo: str, groupe: str, reps: int, sets: int, poids: int) -> None:
        """
        Insère les détails d'un exercice dans la table `Table_historique`.
        :param user_id: ID de l'utilisateur
        :param session_number: Numéro de la séance
        :param exo: Nom de l'exercice
        :param groupe: Groupe musculaire
        :param reps: Nombre de répétitions
        :param sets: Nombre de séries
        :param poids: Poids utilisé
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO Table_historique (ID_user, date, ID_seance_user, ID_exo, REP, SET, Poids)
                VALUES (?, DATE('now'), ?, ?, ?, ?, ?)
            """, (user_id, session_number, exo, reps, sets, poids))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Erreur SQLite : {e}")
        finally:
            cursor.close()
