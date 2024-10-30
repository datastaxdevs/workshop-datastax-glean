# Workshop Glean and DataStax

Demo showing how to index AstraDB data into Glean

You can follow this tutorial fully in a google collab or follow the instructions below to run locally


## Work in a Collab

[![Open In Colab](https://img.shields.io/badge/Open%20in%20Colab-blue?logo=google-colab&style=for-the-badge)](https://colab.research.google.com/github/datastaxdevs/workshop-datastax-glean/blob/main/astra-glean-datasource/astra-glean-import-notebook.ipynb)

## Run Locally

[![Run Locally](https://img.shields.io/badge/Run%20Locally-python3-blue?style=for-the-badge)](#)


### 1.1 Setup AstraDB

ℹ️ [Astra Reference documentation](https://docs.datastax.com/en/astra-db-serverless/databases/create-database.html)


`✅ 1.1.a`: Create an Astra ACCOUNT

Access [https://astra.datastax.com](https://astra.datastax.com) and register with `Google` or `Github` account.

![](https://github.com/datastaxdevs/mini-demo-astradb-glean/blob/main/images/01-login.png?raw=true)


`✅ 1.1.b`: Create an Astra Database

Get to the databases dashboard (by clicking on Databases in the left-hand navigation bar, expanding it if necessary), and click the `[Create Database]` button on the right.

![](https://github.com/datastaxdevs/mini-demo-astradb-glean/blob/main/images/02-create-db.png?raw=true)


- **ℹ️ Fields Description**

| Field                                      | Description                                                                                                                                                                                                                                   |
--------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Vector Database vs Serverless Database** | Choose `Vector Database` In june 2023, Cassandra introduced the support of vector search to enable Generative AI use cases.                                                                                                                   |
| **Database name**                          | It does not need to be unique, is not used to initialize a connection, and is only a label (keep it between 2 and 50 characters). It is recommended to have a database for each of your applications. The free tier is limited to 5 databases. |
| **Cloud Provider**                         | Choose whatever you like. Click a cloud provider logo, pick an Area in the list and finally pick a region. We recommend choosing a region that is closest to you to reduce latency. In free tier, there is very little difference.            |
| **Cloud Region**                           | Pick region close to you available for selected cloud provider and your plan.      

If all fields are filled properly, clicking the "Create Database" button will start the process.

![](https://github.com/datastaxdevs/mini-demo-astradb-glean/blob/main/images/03-pending-db.png?raw=true)


It should take a couple of minutes for your database to become `Active`.

![](https://github.com/datastaxdevs/mini-demo-astradb-glean/blob/main/images/04-active-db.png?raw=true)

`✅ 1.1.c`: Create an Astra TOKEN

To connect to your database, you need the API Endpoint and a token. The api endpoint is available on the database screen, there is a little icon to copy the URL in your clipboard. (it should look like `https://<db-id>-<db-region>.apps.astra.datastax.com`).

![](https://github.com/datastaxdevs/mini-demo-astradb-glean/blob/main/images/05-create-token-db.png?raw=true)

To get a token click the `[Generate Token]` button on the right. It will generate a token that you can copy to your clipboard.


## 2. Installation

### 2.1 Python Environment

- `✅ 2.1.a`: Create and activate a virtual environment

```console
python3 -m venv venv
```

_macOS_
```
source venv/bin/activate
```

_Windows_
```
venv\Scripts\activate
```

- `✅ 2.1.b`:Install the dependencies

```console
pip install astrapy==1.4.1 --no-deps
pip install -r requirements.txt
```

- `✅ 2.1.c`: Edit `.env`

_Copy `.env.example` as `.env`_

```ini
# Astra Configuration
export ASTRA_DB_APPLICATION_TOKEN=<change_me>
export ASTRA_DB_API_ENDPOINT=<change_me>
export ASTRA_DB_COLLECTION_NAME="plain_collection"

# Glean Configuration
export GLEAN_CUSTOMER=<you>
export GLEAN_DATASOURCE_NAME=<change_me>
export GLEAN_API_TOKEN=<change_me>
```


- `✅ 2.1.d`:Run the script

```console
python3 astra-glean-import-job.py
```




