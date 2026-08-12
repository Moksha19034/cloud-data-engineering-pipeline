import duckdb
from pathlib import Path


POSTS_FILE = "data/curated/posts.parquet"
USERS_FILE = "data/curated/users.parquet"
OUTPUT_FILE = "data/curated/post_user_analytics.parquet"


def create_analytics_dataset():
    output_path = Path(OUTPUT_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect()

    query = f"""
        SELECT
            p.post_id,
            p.user_id,
            u.name,
            u.username,
            u.email,
            p.title,
            p.body,
            p.title_length,
            p.body_length,
            p.processed_at
        FROM '{POSTS_FILE}' AS p
        INNER JOIN '{USERS_FILE}' AS u
            ON p.user_id = u.user_id
    """

    df = con.execute(query).fetchdf()

    con.close()

    if df.empty:
        raise ValueError("Analytics dataset is empty")

    df.to_parquet(OUTPUT_FILE, index=False)

    print(f"Analytics dataset saved to: {OUTPUT_FILE}")
    print(f"Records created: {len(df)}")
    print(f"Columns: {list(df.columns)}")


def main():
    print("Starting analytics dataset creation...")

    create_analytics_dataset()

    print("Analytics dataset creation completed successfully.")


if __name__ == "__main__":
    main()
