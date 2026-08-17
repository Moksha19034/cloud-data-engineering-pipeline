import duckdb
from pathlib import Path


# =========================================================
# INPUT FILES
# =========================================================

POSTS_FILE = Path("data/staging/posts.parquet")
USERS_FILE = Path("data/curated/users.parquet")


# =========================================================
# VALIDATE FILES
# =========================================================

def validate_input_files():
    if not POSTS_FILE.exists():
        raise FileNotFoundError(
            f"Posts data file not found: {POSTS_FILE}"
        )

    if not USERS_FILE.exists():
        raise FileNotFoundError(
            f"Users data file not found: {USERS_FILE}"
        )


# =========================================================
# RELATIONSHIP VALIDATION
# =========================================================

def validate_post_user_relationship():
    validate_input_files()

    con = duckdb.connect()

    try:
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

    finally:
        con.close()

    if not result.empty:
        print("❌ RELATIONSHIP CHECK FAILED")
        print(f"Orphan posts found: {len(result)}")
        print(result.to_string(index=False))

        raise ValueError(
            "Posts contain user_id values with no matching user"
        )

    print("✓ All posts have matching users")
    print("✓ Referential integrity check passed")


# =========================================================
# MAIN
# =========================================================

def main():
    print("Starting relationship validation...")

    validate_post_user_relationship()

    print("RELATIONSHIP VALIDATION: PASSED")


if __name__ == "__main__":
    main()
