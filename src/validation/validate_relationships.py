import duckdb


POSTS_FILE = "data/curated/posts.parquet"
USERS_FILE = "data/curated/users.parquet"


def validate_post_user_relationship():
    con = duckdb.connect()

    query = f"""
        SELECT
            p.post_id,
            p.user_id
        FROM '{POSTS_FILE}' AS p
        LEFT JOIN '{USERS_FILE}' AS u
            ON p.user_id = u.user_id
        WHERE u.user_id IS NULL
    """

    result = con.execute(query).fetchdf()

    con.close()

    if not result.empty:
        print("❌ RELATIONSHIP CHECK FAILED")
        print(f"Orphan posts found: {len(result)}")
        print(result.to_string(index=False))
        raise ValueError("Posts contain user_id values with no matching user")

    print("✓ All posts have matching users")
    print("✓ Referential integrity check passed")


def main():
    print("Starting relationship validation...")

    validate_post_user_relationship()

    print("RELATIONSHIP VALIDATION: PASSED")


if __name__ == "__main__":
    main()
