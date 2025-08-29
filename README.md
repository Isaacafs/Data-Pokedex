# Pokémon Pokedex Data com Airflow, Spark e PostgreSQL

Este projeto extrai informações de Pokémon da [PokéAPI](https://pokeapi.co/), processa os dados com **Apache Spark** e salva em um banco **PostgreSQL**, tudo orquestrado pelo **Apache Airflow**.

O objetivo é demonstrar um pipeline ETL completo (Extração, Transformação e Carga) utilizando ferramentas modernas de Big Data e workflow.

---

## 📂 Estrutura do projeto

pokedex_project/
│
├─ dags/
│ └─ pokedex_postgres_dag.py # DAG principal
├─ data/
│ └─ raw/ # JSONs baixados da API (opcional no git)
├─ airflow_jars/
│ └─ postgresql-42.7.7.jar # Driver JDBC do PostgreSQL para Spark
├─ requirements.txt # Dependências Python
├─ README.md
└─ .gitignore

## 🛠 Pré-requisitos

- Python 3.10+
- PostgreSQL 14+ instalado e rodando
- Apache Spark 3.x
- Apache Airflow 2.x
- Java 11+ (necessário para Spark)
- Bibliotecas Python do `requirements.txt`

---

## ⚡ Instalação e Configuração

1. Clone o repositório:
```bash
git clone https://github.com/usuario/Data-Pokedex.git
cd pokedex_project

2. Configure as variáveis de ambiente usadas no DAG (para PostgreSQL):

POSTGRES_USER=newton
POSTGRES_PASSWORD=12345678

3. Ajuste os caminhos no DAG, se necessário:

RAW_DATA_PATH → diretório onde os JSONs serão salvos

spark.jars → caminho para o driver JDBC do PostgreSQL

4. Inicialize o banco PostgreSQL (se ainda não existir):

-- Acesse o PostgreSQL como usuário postgres
psql -U postgres
-- Crie o banco
CREATE DATABASE pokedex_db;
-- Crie o usuário newton e dê permissões
CREATE USER seu_usuario WITH PASSWORD sua_senha;
GRANT ALL PRIVILEGES ON DATABASE pokedex_db TO seu_usuario;

🚀 Rodando o DAG
1. Inicialize o Airflow:

airflow db init
airflow webserver --port 8080
airflow scheduler

2. Abra o Airflow na web (http://localhost:8080) e ative o DAG pokedex_postgres_dag.

3. O DAG executa as seguintes etapas:

- Busca a lista de Pokémon na PokéAPI (limitada pelo POKEMON_LIMIT no DAG)

- Salva detalhes de cada Pokémon em arquivos JSON localmente

- Prepara o banco PostgreSQL, criando banco/tabela se necessário

- Transforma os JSONs em DataFrame Spark

- Salva os dados no PostgreSQL usando append (não sobrescreve dados já existentes)

📝 Testes e Debug

- Para testar apenas alguns Pokémon, altere POKEMON_LIMIT no DAG.

- Para reiniciar os dados no banco:

TRUNCATE TABLE pokemon_pokedex;

- Para verificar o conteúdo da tabela:

SELECT * FROM pokemon_pokedex;
