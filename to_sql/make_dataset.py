import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv()

    conn = psycopg2.connect(os.getenv("POSTGRES_URI"))
    cur = conn.cursor()

    try:
        cur.execute(
            """
        SELECT
            s.title,
            c.text AS comment_text
        FROM
            stories s
        JOIN
            comments c ON s.id = c.parent
        WHERE
            c.is_top_level = true
            AND c.text NOT IN ('[dead]', '[flagged]')
            AND s.title IS NOT NULL
        ORDER BY title;
        """
        )

        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]

        df = pd.DataFrame(rows, columns=column_names)
        df.to_parquet("comments.parquet", index=False)
    except Exception as e:
        print(e)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
