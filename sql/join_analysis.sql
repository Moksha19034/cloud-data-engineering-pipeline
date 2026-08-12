-- Join posts with users
SELECT
    p.post_id,
    p.user_id,
    u.name,
    u.username,
    u.email,
    p.title,
    p.body_length
FROM 'data/curated/posts.parquet' AS p
INNER JOIN 'data/curated/users.parquet' AS u
    ON p.user_id = u.user_id
ORDER BY p.post_id
LIMIT 20;
