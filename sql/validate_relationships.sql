-- Find posts that have no matching user
SELECT
    p.post_id,
    p.user_id
FROM 'data/curated/posts.parquet' AS p
LEFT JOIN 'data/curated/users.parquet' AS u
    ON p.user_id = u.user_id
WHERE u.user_id IS NULL;
