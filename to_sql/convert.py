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


insert_user_query = """
INSERT INTO users (id) VALUES (%s)
ON CONFLICT(id)
DO NOTHING
"""


def build_insert_stories_query(story: Story) -> str:
    pairs = {}
    pairs["id"] = str(story.id)
    pairs["by"] = str(story.by)
    pairs["text"] = f'"{story.text}"'
    pairs["time"] = f"to_timestamp({story.time})"

    column_names = []
    values = []

    for k, v in pairs.items():
        column_names.append(k)
        values.append(v)

    query = f"""
    INSERT INTO stories ({", ".join(column_names)})
    VALUES ({", ".join(values)})
    """

    return query


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
            users.add(comment.by)
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

print(f"{len(skipped):,} unusable items.")
print(f"{num_top_level_comments:,} top-level comments found.")
print(f"{len(users):,} users found.")

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
