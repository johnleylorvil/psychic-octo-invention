#!/usr/bin/env python3
"""
Script d'investigation de base de données Railway
Pour analyser la structure et le contenu des tables existantes
"""

import psycopg2
import psycopg2.extras
import sys
import json
from urllib.parse import urlparse
from tabulate import tabulate
import os


class RailwayDBInspector:
    def __init__(self, database_url):
        """
        Initialise l'inspecteur avec l'URL de la base de données Railway
        Format attendu: postgresql://user:password@host:port/database
        """
        self.database_url = database_url
        self.connection = None
        self.cursor = None

    def connect(self):
        """Établit la connexion à la base de données"""
        try:
            self.connection = psycopg2.connect(self.database_url)
            self.cursor = self.connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            print("✅ Connexion établie avec succès!")
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False

    def disconnect(self):
        """Ferme la connexion à la base de données"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("🔌 Connexion fermée")

    def get_all_tables(self):
        """Récupère toutes les tables de la base de données"""
        try:
            query = """
            SELECT 
                schemaname,
                tablename,
                tableowner
            FROM pg_tables 
            WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
            ORDER BY schemaname, tablename;
            """

            self.cursor.execute(query)
            tables = self.cursor.fetchall()
            return tables
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des tables: {e}")
            return []

    def get_table_structure(self, table_name, schema_name="public"):
        """Récupère la structure d'une table spécifique"""
        try:
            query = """
            SELECT 
                column_name,
                data_type,
                character_maximum_length,
                is_nullable,
                column_default,
                ordinal_position
            FROM information_schema.columns
            WHERE table_name = %s AND table_schema = %s
            ORDER BY ordinal_position;
            """

            self.cursor.execute(query, (table_name, schema_name))
            columns = self.cursor.fetchall()
            return columns
        except Exception as e:
            print(
                f"❌ Erreur lors de la récupération de la structure de {table_name}: {e}"
            )
            return []

    def get_table_constraints(self, table_name, schema_name="public"):
        """Récupère les contraintes d'une table"""
        try:
            query = """
            SELECT 
                tc.constraint_name,
                tc.constraint_type,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            LEFT JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.table_name = %s AND tc.table_schema = %s;
            """

            self.cursor.execute(query, (table_name, schema_name))
            constraints = self.cursor.fetchall()
            return constraints
        except Exception as e:
            print(
                f"❌ Erreur lors de la récupération des contraintes de {table_name}: {e}"
            )
            return []

    def get_table_sample_data(self, table_name, schema_name="public", limit=5):
        """Récupère un échantillon de données d'une table"""
        try:
            query = f"SELECT * FROM {schema_name}.{table_name} LIMIT %s;"
            self.cursor.execute(query, (limit,))
            sample_data = self.cursor.fetchall()
            return sample_data
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des données de {table_name}: {e}")
            return []

    def get_table_count(self, table_name, schema_name="public"):
        """Compte le nombre de lignes dans une table"""
        try:
            query = f"SELECT COUNT(*) as count FROM {schema_name}.{table_name};"
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            return result["count"] if result else 0
        except Exception as e:
            print(f"❌ Erreur lors du comptage de {table_name}: {e}")
            return 0

    def analyze_database(self):
        """Analyse complète de la base de données"""
        print("🔍 ANALYSE DE LA BASE DE DONNÉES RAILWAY")
        print("=" * 50)

        # Récupération des tables
        tables = self.get_all_tables()

        if not tables:
            print("❌ Aucune table trouvée!")
            return

        print(f"📊 Nombre total de tables: {len(tables)}")
        print()

        analysis_report = {
            "database_info": {
                "total_tables": len(tables),
                "url": (
                    self.database_url.split("@")[1]
                    if "@" in self.database_url
                    else "hidden"
                ),
            },
            "tables": {},
        }

        for table in tables:
            table_name = table["tablename"]
            schema_name = table["schemaname"]

            print(f"🔍 Analyse de la table: {schema_name}.{table_name}")
            print("-" * 30)

            # Structure de la table
            columns = self.get_table_structure(table_name, schema_name)
            constraints = self.get_table_constraints(table_name, schema_name)
            row_count = self.get_table_count(table_name, schema_name)
            sample_data = self.get_table_sample_data(table_name, schema_name, 3)

            table_info = {
                "schema": schema_name,
                "row_count": row_count,
                "columns": [],
                "constraints": [],
                "sample_data": [],
            }

            # Affichage des colonnes
            if columns:
                print("📋 Structure des colonnes:")
                column_data = []
                for col in columns:
                    column_info = {
                        "name": col["column_name"],
                        "type": col["data_type"],
                        "nullable": col["is_nullable"],
                        "default": col["column_default"],
                        "max_length": col["character_maximum_length"],
                    }
                    table_info["columns"].append(column_info)

                    column_data.append(
                        [
                            col["column_name"],
                            col["data_type"],
                            col["character_maximum_length"] or "",
                            col["is_nullable"],
                            col["column_default"] or "",
                        ]
                    )

                print(
                    tabulate(
                        column_data,
                        headers=["Colonne", "Type", "Longueur", "Nullable", "Défaut"],
                        tablefmt="grid",
                    )
                )

            # Affichage des contraintes
            if constraints:
                print("\n🔐 Contraintes:")
                constraint_data = []
                for constraint in constraints:
                    constraint_info = {
                        "name": constraint["constraint_name"],
                        "type": constraint["constraint_type"],
                        "column": constraint["column_name"],
                        "foreign_table": constraint["foreign_table_name"],
                        "foreign_column": constraint["foreign_column_name"],
                    }
                    table_info["constraints"].append(constraint_info)

                    constraint_data.append(
                        [
                            constraint["constraint_name"],
                            constraint["constraint_type"],
                            constraint["column_name"],
                            constraint["foreign_table_name"] or "",
                            constraint["foreign_column_name"] or "",
                        ]
                    )

                print(
                    tabulate(
                        constraint_data,
                        headers=[
                            "Nom",
                            "Type",
                            "Colonne",
                            "Table étrangère",
                            "Colonne étrangère",
                        ],
                        tablefmt="grid",
                    )
                )

            # Affichage du nombre de lignes
            print(f"\n📈 Nombre de lignes: {row_count}")

            # Affichage des données d'exemple
            if sample_data and row_count > 0:
                print("\n📄 Échantillon de données:")
                if sample_data:
                    # Convertir les données en format lisible
                    sample_rows = []
                    for row in sample_data:
                        sample_rows.append(list(row.values()))

                    headers = list(sample_data[0].keys()) if sample_data else []
                    table_info["sample_data"] = [dict(row) for row in sample_data]

                    print(tabulate(sample_rows[:3], headers=headers, tablefmt="grid"))

            analysis_report["tables"][table_name] = table_info
            print("\n" + "=" * 50 + "\n")

        # Sauvegarde du rapport en JSON
        with open("database_analysis_report.json", "w", encoding="utf-8") as f:
            json.dump(analysis_report, f, indent=2, ensure_ascii=False, default=str)

        print("💾 Rapport sauvegardé dans 'database_analysis_report.json'")

        # Génération de recommandations pour Django
        self.generate_django_recommendations(analysis_report)

    def generate_django_recommendations(self, analysis_report):
        """Génère des recommandations pour la structure Django"""
        print("\n🚀 RECOMMANDATIONS POUR LE BACKEND DJANGO")
        print("=" * 50)

        recommendations = []

        for table_name, table_info in analysis_report["tables"].items():
            if table_info["row_count"] > 0:
                # Analyser le type de table basé sur le nom et la structure
                if "product" in table_name.lower():
                    recommendations.append(
                        f"📦 Table {table_name}: Créer un modèle Product Django"
                    )
                elif "order" in table_name.lower():
                    recommendations.append(
                        f"🛒 Table {table_name}: Créer un modèle Order Django"
                    )
                elif "user" in table_name.lower():
                    recommendations.append(
                        f"👤 Table {table_name}: Étendre le modèle User Django"
                    )
                elif "category" in table_name.lower():
                    recommendations.append(
                        f"🏷️ Table {table_name}: Créer un modèle Category Django"
                    )
                elif "image" in table_name.lower():
                    recommendations.append(
                        f"🖼️ Table {table_name}: Gérer les images avec Django"
                    )
                else:
                    recommendations.append(
                        f"📋 Table {table_name}: Analyser pour créer le modèle approprié"
                    )

        for rec in recommendations:
            print(rec)

        print("\n📝 Prochaines étapes recommandées:")
        print("1. Créer les modèles Django basés sur les tables existantes")
        print("2. Configurer les relations entre les modèles")
        print("3. Créer les serializers DRF pour l'API")
        print("4. Implémenter les vues pour les opérations CRUD")
        print("5. Ajouter l'authentification et les permissions")
        print("6. Intégrer MonCash pour les paiements")


def main():
    """Fonction principale"""
    # URL de la base de données Railway configurée
    database_url = "postgresql://postgres:qRyfVhpBybUISEnGVlenCCkfREXVWDJd@switchback.proxy.rlwy.net:53820/railway"

    # Possibilité de passer une URL différente en argument
    if len(sys.argv) > 1:
        database_url = sys.argv[1]

    print(f"🔗 Connexion à la base de données Railway...")
    print(f"📍 Host: switchback.proxy.rlwy.net:53820")
    print(f"🗄️ Database: railway")
    print("-" * 50)

    inspector = RailwayDBInspector(database_url)

    if inspector.connect():
        try:
            inspector.analyze_database()
        finally:
            inspector.disconnect()
    else:
        print("❌ Impossible de se connecter à la base de données")
        sys.exit(1)


if __name__ == "__main__":
    main()
