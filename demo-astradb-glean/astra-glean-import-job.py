import os
from dotenv import load_dotenv
from getpass import getpass
import pandas as pd
from astrapy import DataAPIClient
from tqdm import tqdm  # Progress bar with tqdm
import json
import glean_indexing_api_client as indexing_api
from glean_indexing_api_client.api import datasources_api, documents_api
from glean_indexing_api_client.model.custom_datasource_config import CustomDatasourceConfig
from glean_indexing_api_client.model.object_definition import ObjectDefinition
from glean_indexing_api_client.model.index_document_request import IndexDocumentRequest
from glean_indexing_api_client.model.document_definition import DocumentDefinition
from glean_indexing_api_client.model.content_definition import ContentDefinition
from glean_indexing_api_client.model.document_permissions_definition import DocumentPermissionsDefinition
from datasets import load_dataset
from colorama import Fore, Style  # For color coding the output

# Load environment variables from .env
load_dotenv()

ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_API_ENDPOINT      = os.getenv("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_COLLECTION_NAME   = os.getenv("ASTRA_DB_COLLECTION_NAME")
GLEAN_API_TOKEN            = os.getenv("GLEAN_API_TOKEN")
GLEAN_CUSTOMER             = os.getenv("GLEAN_CUSTOMER")
GLEAN_DATASOURCE_NAME      = os.getenv("GLEAN_DATASOURCE_NAME")

print(f"{Fore.GREEN}============================={Style.RESET_ALL}")
print(f"{Fore.GREEN} ASTRADB - GLEAN INTEGRATION {Style.RESET_ALL}")
print(f"{Fore.GREEN}============================={Style.RESET_ALL}\n")

# Initialize Astra DB client
client = DataAPIClient(ASTRA_DB_APPLICATION_TOKEN, caller_name="glean", caller_version="1.0")
database = client.get_database(ASTRA_DB_API_ENDPOINT)
print(f"{Fore.CYAN}[ OK ] - Credentials are OK, your database name is {Style.RESET_ALL}{database.info().name}")

# Create collection
plain_collection = database.create_collection(ASTRA_DB_COLLECTION_NAME, check_exists=False)
print(f"{Fore.CYAN}[ OK ] - Collection {Style.RESET_ALL}{ASTRA_DB_COLLECTION_NAME}{Fore.CYAN} is ready{Style.RESET_ALL}")

# Load philosopher dataset
print(f"{Fore.CYAN}[INFO] - Downloading Data from Hugging Face 🤗{Style.RESET_ALL}")
philo_dataset = load_dataset("datastax/philosopher-quotes")["train"]
print(f"{Fore.CYAN}[ OK ] - Dataset loaded in memory{Style.RESET_ALL}")
print(f"{Fore.CYAN}[INFO] - Record: {Style.RESET_ALL}{philo_dataset[16]}")
philo_dataframe = pd.DataFrame.from_dict(philo_dataset)

# Progress bar for loading to Astra
def load_to_astra(df, collection):
    len_df = len(df)
    print(f"{Fore.CYAN}[INFO] - Starting data insertion into Astra DB...{Style.RESET_ALL}")
    
    for i in tqdm(range(len_df), desc="Inserting documents", colour="green"):
        try:
            collection.insert_one({
                "_id": i,
                "author": df.loc[i, "author"],
                "quote": df.loc[i, "quote"],
                "tags": df.loc[i, "tags"].split(";") if pd.notna(df.loc[i, "tags"]) else []
            })
        except Exception as error:
            print(f"{Fore.RED}Error while inserting document {i}: {error}{Style.RESET_ALL}")

# Flush the collection before inserting new data
plain_collection.delete_many({})
print(f"{Fore.CYAN}[ OK ] - Collection has been flushed{Style.RESET_ALL}")

# Insert documents into Astra DB
load_to_astra(philo_dataframe, plain_collection)
print(f"{Fore.CYAN}[ OK ] - Load finished{Style.RESET_ALL}")

# Setup Glean API
GLEAN_API_ENDPOINT = f"https://{GLEAN_CUSTOMER}-be.glean.com/api/index/v1"
print(f"{Fore.CYAN}[INFO] - Glean API setup, endpoint is:{Style.RESET_ALL} {GLEAN_API_ENDPOINT}")

# Initialize Glean client
configuration = indexing_api.Configuration(host=GLEAN_API_ENDPOINT, access_token=GLEAN_API_TOKEN)
api_client = indexing_api.ApiClient(configuration)
datasource_api = datasources_api.DatasourcesApi(api_client)
print(f"{Fore.CYAN}[ OK ] - Glean client initialized{Style.RESET_ALL}")

# Create and register datasource in Glean
datasource_config = CustomDatasourceConfig(
    name=GLEAN_DATASOURCE_NAME,
    display_name='AstraDB Collection DataSource',
    datasource_category='PUBLISHED_CONTENT',
    url_regex='^https://your_astra_db_url',  # Replace with actual regex
    object_definitions=[
        ObjectDefinition(
            doc_category='PUBLISHED_CONTENT',
            name='AstraVectorEntry'
        )
    ]
)

try:
    datasource_api.adddatasource_post(datasource_config)
    print(f"{Fore.GREEN}[ OK ] - DataSource has been created!{Style.RESET_ALL}")
except indexing_api.ApiException as e:
    print(f"{Fore.RED}[ ERROR ] - Error creating datasource: {e}{Style.RESET_ALL}")

# Function to index Astra documents into Glean
def index_astra_document_into_glean(astra_document):
    document_id = str(astra_document['_id'])
    title = astra_document['author'] + ' quote_' + str(astra_document['_id'])
    body_text = astra_document['quote']
    datasource_name = GLEAN_DATASOURCE_NAME
    request = IndexDocumentRequest(
        document=DocumentDefinition(
            datasource=datasource_name,
            title=title,
            id=document_id,
            view_url="https://your_astra_db_url",
            body=ContentDefinition(mime_type="text/plain", text_content=body_text),
            permissions=DocumentPermissionsDefinition(allow_anonymous_access=True),
        )
    )
    documents_api_client = documents_api.DocumentsApi(api_client)
    try:
        documents_api_client.indexdocument_post(request)
    except indexing_api.ApiException as e:
        print(f"{Fore.RED}Error indexing document {document_id}: {e}{Style.RESET_ALL}")

# Index documents from Astra DB to Glean
def index_documents_to_glean(collection):
    total_docs = collection.estimated_document_count() 
    with tqdm(total=total_docs, desc="Indexing documents to Glean", unit="doc", colour="blue") as pbar:
        for doc in collection.find():
            try:
                index_astra_document_into_glean(doc)
                pbar.set_postfix({"Status": f"Indexed {doc['_id']}"})
            except Exception as error:
                pbar.set_postfix({"Status": f"Error with {doc['_id']}"})
                print(f"{Fore.RED}Error indexing document {doc['_id']}: {error}{Style.RESET_ALL}")
            pbar.update(1)  # Update progress bar after each document

# Use the function to index documents into Glean
index_documents_to_glean(plain_collection)

print(f"{Fore.GREEN}Batch Ended Successfully!{Style.RESET_ALL}")