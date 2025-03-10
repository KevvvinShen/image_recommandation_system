"""
This script is used to ingest the image embeddings into Amazon OpenSearch Service.
"""
import os
import tqdm as tq
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth, helpers
from requests_aws4auth import AWS4Auth
import boto3
import time
import pandas as pd

HOST = "zpk856m0m1vlibqyoa38.us-west-2.aoss.amazonaws.com"

INDEX_NAME = "image_vectors"
VECTOR_NAME = "vectors"
VECTOR_MAPPING = "image_files"

def initialize_opensearch_client():
    """
    param: None
    return: OpenSearch client object
    exception: None
    description: Initialize OpenSearch client
    """
    REGION = "us-west-2" # OpenSearch region
    service = 'aoss' # OpenSearch service name
    
    credentials = boto3.Session().get_credentials()
    auth = AWSV4SignerAuth(credentials, REGION, service)

    client = OpenSearch(
        hosts=[{'host': HOST, 'port': 443}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        pool_maxsize=300
    )
    return client

def ingest_embeddings():
    """
    param: None
    return: None
    exception: None
    description: Ingest embeddings into OpenSearch
    explanation: This function is used to ingest the image embeddings into Amazon OpenSearch Service.
    vector index with associate vector and text mapping fields
    """
    client = initialize_opensearch_client()
    now_path = os.path.dirname(__file__)
    print(now_path)
    # get embeddings from the data folder


    embeddings_files = os.listdir(os.path.join(now_path, "data"))
    for file in embeddings_files:
        # print(file)
        path = os.path.join(now_path, f"data/{file}")
        final_embeddings_dataset = pd.read_pickle(path)
        # print(f"Read embeddings from {final_embeddings_dataset}")

        # Ingest embeddings into vector index with associate vector and text mapping fields
        actions = []
        for idx, record in tq.tqdm(final_embeddings_dataset.iterrows(), total=len(final_embeddings_dataset)):
            if '/data/data/data' not in record['image_url']:
                actions.append({
                    "_index": INDEX_NAME, 
                    VECTOR_NAME: record['image_embedding'], 
                    VECTOR_MAPPING: record['image_url']
                })
        helpers.bulk(client, actions)
        print(f"{file}: Ingested embeddings successfully into OpenSearch", len(actions))
        time.sleep(3)

if __name__ == "__main__":
    # calculate the running time
    start_time = time.time()
    ingest_embeddings()
    end_time = time.time()
    print(f"Time taken to ingest embeddings: {end_time - start_time} seconds")
