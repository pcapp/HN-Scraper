from pydantic import BaseModel, ValidationError
from pydantic_core import ErrorDetails
import pymongo
import psycopg2
from dotenv import load_dotenv
import os
from typing_extensions import TypedDict
from typing import Dict, List, Optional, Any, Tuple
from pprint import pprint


class Story(BaseModel):
    id: int
    by: str
    text: Optional[str] = None
    time: int
    kids: Optional[List[int]] = []
    score: int
    title: Optional[str] = None
    url: Optional[str] = None


class Comment(BaseModel):
    id: int
    by: str
    kids: Optional[List[int]] = []
    parent: int
    text: str
    time: int


class ErrorDetails(TypedDict):
    loc: Tuple[str]
    msg: str
    type: str


class SkippedRecord(BaseModel):
    record: Dict[str, Any]
    errors: List[ErrorDetails]


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


query = {"deleted": {"$exists": False}}
results = items.find(query).sort("time", pymongo.ASCENDING)

stories = {}
users = set()
skipped = []
num_top_level_comments = 0

for result in results:
    item_type = result.get("type")

    if item_type == "story":
        try:
            story = Story(**result)
            stories[story.id] = story
        except ValidationError as e:
            skipped_record = SkippedRecord(record=result, errors=e.errors())
            skipped.append(skipped)
    elif item_type == "comment":
        try:
            comment = Comment(**result)
            users.add(comment.by)

            if comment.parent in stories:
                num_top_level_comments += 1
        except ValidationError as e:
            skipped_record = SkippedRecord(record=result, errors=e.errors())
            skipped.append(skipped)

print(f"{len(skipped)} unusable items.")
print(f"{num_top_level_comments:,} top-level comments found.")

# pg_cur.execute("select * from  users")
# records = pg_cur.fetchall()

# for record in records:
#     print(record)

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
