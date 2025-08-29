import json
import time
import requests
from pathlib import Path
import psycopg2
import os

from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
from pyspark.sql import SparkSession

RAW_DATA_PATH = "/home/seu_usuario/airflow/data/raw/"
POKEMON_LIMIT = 151

# Configuração do banco
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_DB = "pokedex_db"
POSTGRES_TABLE = "pokemon_pokedex"
POSTGRES_USER = "seu_usuario"
POSTGRES_PASSWORD = "sua_senha"

@dag(
    dag_id='pokedex_postgres_dag',
    description='Extrai Pokémon, processa com Spark e salva no PostgreSQL.',
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
    tags=['pokedex', 'api', 'spark', 'postgres'],
)
def pokedex_postgres_dag():

    @task
    def get_pokemon_list() -> list:
        response = requests.get(f"https://pokeapi.co/api/v2/pokemon?limit={POKEMON_LIMIT}")
        response.raise_for_status()
        return response.json()['results']

    @task
    def fetch_and_save_pokemon_details(pokemon: dict):
        response = requests.get(pokemon['url'])
        response.raise_for_status()
        pokemon_data = response.json()

        Path(RAW_DATA_PATH).mkdir(parents=True, exist_ok=True)
        with open(Path(RAW_DATA_PATH) / f"{pokemon_data['id']}.json", "w", encoding="utf-8") as f:
            json.dump(pokemon_data, f, ensure_ascii=False, indent=4)

        time.sleep(0.2)

    @task
    def prepare_postgres():
        """Cria o banco e a tabela caso não existam"""
        conn = psycopg2.connect(
            dbname="postgres",
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Cria o banco se não existir
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{POSTGRES_DB}'")
        exists = cursor.fetchone()
        if not exists:
            cursor.execute(f"CREATE DATABASE {POSTGRES_DB}")

        # Conecta no banco específico
        conn.close()
        conn = psycopg2.connect(
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT
        )
        cursor = conn.cursor()

        # Cria a tabela se não existir
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {POSTGRES_TABLE} (
                id INTEGER PRIMARY KEY,
                name TEXT,
                height INTEGER,
                weight INTEGER,
                base_experience INTEGER
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()

    @task
    def transform_and_save_to_postgres():
        spark = SparkSession.builder \
            .appName("PokemonToPostgres") \
            .config("spark.jars", "/home/newton/airflow_jars/postgresql-42.7.7.jar") \
            .config("spark.driver.extraClassPath", "/home/newton/airflow_jars/postgresql-42.7.7.jar") \
            .config("spark.executor.extraClassPath", "/home/newton/airflow_jars/postgresql-42.7.7.jar") \
            .getOrCreate()


        # Lê JSONs
        df = spark.read.option("multiline", "true").json(f"{RAW_DATA_PATH}/*.json")

        # Seleciona colunas
        df_selected = df.select(
            "id", "name", "height", "weight", "base_experience"
        ).orderBy("id")

        # Salva no PostgreSQL usando append (não sobrescreve)
        df_selected.write \
            .format("jdbc") \
            .option("url", f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}") \
            .option("dbtable", POSTGRES_TABLE) \
            .option("user", POSTGRES_USER) \
            .option("password", POSTGRES_PASSWORD) \
            .option("driver", "org.postgresql.Driver") \
            .mode("append") \
            .save()

        spark.stop()

    # Orquestração
    pokemon_list = get_pokemon_list()
    details = fetch_and_save_pokemon_details.expand(pokemon=pokemon_list)
    prepare = prepare_postgres()
    prepare >> details >> transform_and_save_to_postgres()

pokedex_postgres_dag()
