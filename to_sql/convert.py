import pymongo
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

# MongoDB connection
mongo_client = pymongo.MongoClient(os.getenv("MONGO_URI"))
mongo_db = mongo_client["hn_scrape"]
items = mongo_db["items"]

# PostgreSQL connection
pg_conn = psycopg2.connect(os.getenv("POSTGRES_URI"))
pg_cur = pg_conn.cursor()

batch_size = 1000
batch = []


def transform_document(document):
    # Transform the MongoDB document to match PostgreSQL schema
    # This function should return the transformed data
    pass


def insert_batch(cursor, batch):
    # Insert the batch of transformed data into PostgreSQL
    # You might use cursor.executemany() with an INSERT INTO statement, or use the COPY command
    pass


pg_cur.execute("select * from users")
records = pg_cur.fetchall()

for record in records:
    print(record)

# for document in mongo_collection.find():
#     # Transform your document here
#     transformed_data = transform_document(document)
#     batch.append(transformed_data)

#     if len(batch) >= batch_size:
#         # Insert batch into PostgreSQL
#         insert_batch(pg_cur, batch)
#         batch = []  # Reset batch

# # Insert any remaining documents
# if batch:
#     insert_batch(pg_cur, batch)

# pg_conn.commit()

# Don't forget to close your connections
pg_cur.close()
pg_conn.close()
mongo_client.close()
