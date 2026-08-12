-- 1. View the first 10 posts
SELECT
    post_id,
    user_id,
    title,
    title_length,
    body_length
FROM 'data/curated/posts.parquet'
LIMIT 10;


-- 2. Count total posts
SELECT
    COUNT(*) AS total_posts
FROM 'data/curated/posts.parquet';


-- 3. Posts per user
SELECT
    user_id,
    COUNT(*) AS post_count
FROM 'data/curated/posts.parquet'
GROUP BY user_id
ORDER BY post_count DESC;


-- 4. Average title length
SELECT
    AVG(title_length) AS average_title_length
FROM 'data/curated/posts.parquet';


-- 5. Longest posts
SELECT
    post_id,
    user_id,
    title_length,
    body_length
FROM 'data/curated/posts.parquet'
ORDER BY body_length DESC
LIMIT 10;

-- 6. Posts with long bodies
SELECT
    post_id,
    user_id,
    title_length,
    body_length
FROM 'data/curated/posts.parquet'
WHERE body_length > 200
ORDER BY body_length DESC;


-- 7. Posts with long bodies and short titles
SELECT
    post_id,
    user_id,
    title_length,
    body_length
FROM 'data/curated/posts.parquet'
WHERE body_length > 200
  AND title_length < 40
ORDER BY body_length DESC;


-- 8. Users with more than 5 posts
SELECT
    user_id,
    COUNT(*) AS post_count
FROM 'data/curated/posts.parquet'
GROUP BY user_id
HAVING COUNT(*) > 5
ORDER BY post_count DESC;


-- 9. Classify posts by body length
SELECT
    post_id,
    user_id,
    body_length,
    CASE
        WHEN body_length > 200 THEN 'Long'
        WHEN body_length >= 150 THEN 'Medium'
        ELSE 'Short'
    END AS body_category
FROM 'data/curated/posts.parquet'
ORDER BY body_length DESC;
