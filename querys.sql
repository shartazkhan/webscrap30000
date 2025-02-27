-- Q1

MSCK REPAIR TABLE ccindex;

-- Q2

WITH lang_flags AS (
  SELECT 
    url_host_name,
    MAX(CASE WHEN content_languages LIKE '%ja%' THEN 1 ELSE 0 END) AS has_ja,
    MAX(CASE WHEN content_languages LIKE '%ko%' THEN 1 ELSE 0 END) AS has_ko
  FROM ccindex
  WHERE crawl = 'CC-MAIN-2023-50'  -- adjust to your desired crawl
    AND subset = 'warc'
  GROUP BY url_host_name
)
SELECT url_host_name
FROM lang_flags
WHERE has_ja = 1 AND has_ko = 1
LIMIT 30000;



