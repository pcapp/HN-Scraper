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

insert_user_query = """
INSERT INTO users (id) VALUES (%s)
ON CONFLICT(id)
DO NOTHING
"""


def clear_old_data():
    pg_cur.execute("delete from stories")
    pg_cur.execute("delete from users")


def build_insert_stories_query(story: Story) -> tuple[str, List[Any]]:
    pairs = {}
    pairs["id"] = story.id
    pairs["by"] = story.by
    pairs["text"] = story.text
    pairs["time"] = story.time
    pairs["score"] = story.score

    if story.url:
        pairs["url"] = story.url
    if story.text:
        pairs["text"] = story.text
    if story.title:
        pairs["title"] = story.title

    column_names = []
    values = []
    placeholders = []

    for k, v in pairs.items():
        column_names.append(k)
        if k == "time":
            placeholders.append("to_timestamp(%s)")
        else:
            placeholders.append("%s")

        values.append(v)

    query = f"""
    INSERT INTO stories ({", ".join(column_names)})
    VALUES ({", ".join(placeholders)})
    """

    return query, values


clear_old_data()

query = {"deleted": {"$exists": False}}
results = items.find(query).sort("time", pymongo.ASCENDING)

users = set()
stories = set()
num_stories = 0
skipped = []
num_top_level_comments = 0

for result in results:
    item_type = result.get("type")

    if item_type == "story":
        try:
            story = Story(**result)

            if story.by not in users:
                batch.append(pg_cur.mogrify(insert_user_query, (story.by,)))
                users.add(story.by)

            query, values = build_insert_stories_query(story)

            num_stories += 1
            stories.add(story.id)
            batch.append(pg_cur.mogrify(query, values))

        except ValidationError as e:
            skipped_record = SkippedRecord(record=result, errors=e.errors())
            skipped.append(skipped)
    elif item_type == "comment":
        try:
            comment = Comment(**result)

            if comment.by not in users:
                batch.append(pg_cur.mogrify(insert_user_query, (comment.by,)))
                users.add(comment.by)

            # Add the comment to the comments table after coffee.

            if comment.parent in stories:
                num_top_level_comments += 1
        except ValidationError as e:
            skipped_record = SkippedRecord(record=result, errors=e.errors())
            skipped.append(skipped)

    if len(batch) >= batch_size:
        pg_cur.execute(b";".join(batch))
        batch = []

# Insert any remaining documents
if batch:
    pg_cur.execute(b";".join(batch))

pg_conn.commit()

print(f"{len(skipped):,} unusable items.")
print(f"{num_stories} usable stories found.")
print(f"{num_top_level_comments:,} top-level comments found.")
print(f"{len(users):,} users found.")

# Close connectiosn
pg_cur.close()
pg_conn.close()
mongo_client.close()
