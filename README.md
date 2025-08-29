# Pokémon Pokedex Data com Airflow, Spark e PostgreSQL

Este projeto extrai informações de Pokémon da [PokéAPI](https://pokeapi.co/), processa os dados com **PySpark** e salva em um banco **PostgreSQL**, tudo orquestrado pelo **Airflow**.

O objetivo é demonstrar um pipeline ETL completo (Extração, Transformação e Carga) utilizando ferramentas modernas de Big Data e workflow.

O projeto foi feito usando WSL.

---

## 📂 Estrutura do projeto

```text
pokedex_project/
│
├─ dags/
│ └─ pokedex_postgres_dag.py # DAG principal
├─ data/
│ └─ raw/ # JSONs baixados da API
├─ airflow_jars/
│ └─ postgresql-42.7.7.jar # Driver JDBC do PostgreSQL para Spark
├─ README.md
└─ .gitignore
```

OBS: O repositório contém o código e instruções para rodar todo o projeto. Você pode organizar os diretórios de forma diferente, mas o resultado final será o mesmo.

### 🛠 Pré-requisitos e Instalação

As versões usadas neste projeto, e que serão necessárias, são:

- Python 3.10.12
- PostgreSQL 14.18
- PySpark 4.0.0
- Airflow 2.10.2
- JDK 17.0.16 (necessário para Spark)

#### 1. Python 3.10.12
Baixe e instale a versão específica no [site oficial do Python](https://www.python.org/downloads/release/python-31012/).  
Após a instalação, verifique a versão com:

```bash
python3 --version
```

#### 2. PostgreSQL 14.18

Baixe o instalador adequado do PostgreSQL, no ambiente virtual (Veja o ponto 'Criando o Ambiente Virtual').

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
psql --version

# Iniciar o serviço
sudo service postgresql start

# Verificar status
sudo service postgresql status
```

#### 3. PySpark 4.0.0

Instale o PySpark, no ambiente virtual (Veja o ponto 'Criando o Ambiente Virtual').

```bash
pip install pyspark==4.0.0
```

#### 4. Airflow

Use os comandos abaixo, no ambiente virtual (Veja o ponto 'Criando o Ambiente Virtual').

```bash
AIRFLOW_VERSION=2.10.2
PYTHON_VERSION=3.10
# Você pode mudar a versão do Airflow se quiser
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
```

#### 5. JDK 17.0.16

Baixe e instale o JDK do site oficial da Oracle ou Adoptium.
Verifique a instalação com:

```bash
java -version
```

## ⚡ Instalação e Configuração

#### 1. Clone o repositório:
```bash
git clone https://github.com/usuario/Data-Pokedex.git
cd pokedex_project
```

#### 2. Configure as variáveis de ambiente usadas no DAG (para PostgreSQL):

```bash
POSTGRES_USER= seu_usuario #ponha o nome de usuário que será utilizado
POSTGRES_PASSWORD= sua_senha #ponha a senha que será utilizada
```

#### 3. Ajuste os caminhos no DAG, se necessário:

```bash
RAW_DATA_PATH → diretório onde os JSONs serão salvos

spark.jars → caminho para o driver JDBC do PostgreSQL
```

#### 4. Inicialize o banco PostgreSQL (se ainda não existir):

```bash
-- Acesse o PostgreSQL como usuário postgres
psql -U postgres
-- Crie o banco
CREATE DATABASE pokedex_db;
-- Crie o seu usuário e dê permissões
CREATE USER seu_usuario WITH PASSWORD sua_senha;
GRANT ALL PRIVILEGES ON DATABASE pokedex_db TO seu_usuario;
```

#### 5. Ponha o DAG na pasta dags/ do seu projeto ou do Airflow, dependendo de onde você está executando o Airflow. Por exemplo:

```bash
# Copiando o DAG para o diretório de dags do projeto
cp pokedex_postgres_dag.py ~/caminho/para/seu/projeto/dags/

# Se estiver usando o diretório padrão do Airflow
cp pokedex_postgres_dag.py ~/airflow/dags/
```

## 💻 Criando o Ambiente Virtual

```bash
# 1. Criar o ambiente virtual
python3.10.2 -m venv airflow_venv

# 2. Ativar o ambiente virtual
source airflow_venv/bin/activate  # Linux/WSL

```

## 🚀 Rodando o DAG

#### 1. Inicialize o Airflow:

```bash
airflow db init
airflow webserver --port 8080
airflow scheduler
```

#### 2. Abra o Airflow na web (http://localhost:8080) e ative o DAG pokedex_postgres_dag.

#### 3. O DAG executa as seguintes etapas:

- Busca a lista de Pokémon na PokéAPI (limitada pelo POKEMON_LIMIT no DAG)

- Salva detalhes de cada Pokémon em arquivos JSON localmente

- Prepara o banco PostgreSQL, criando banco/tabela se necessário

- Transforma os JSONs em DataFrame Spark

- Salva os dados no PostgreSQL usando append (não sobrescreve dados já existentes)

📝 Testes e Debug

- Para testar apenas alguns Pokémon, altere POKEMON_LIMIT no DAG.

- Para reiniciar os dados no banco:

```bash
TRUNCATE TABLE pokemon_pokedex;
```

- Para verificar o conteúdo da tabela:

```bash
SELECT * FROM pokemon_pokedex;
```
