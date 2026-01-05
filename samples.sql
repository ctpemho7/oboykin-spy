SELECT * FROM fact;

SELECT * FROM tmp_fact;

SELECT * FROM diff;
SELECT * FROM roll;


-- поля в diff
SELECT t.roll_id, t.shop_id, 
       f.price AS old_price, f.available AS old_count, 
       t.price AS new_price, t.available AS new_price    
FROM tmp_fact t
    LEFT JOIN fact f ON t.roll_id = f.roll_id AND t.shop_id = f.shop_id
    WHERE f.roll_id IS NULL                                                 -- Новый рулон
        OR t.price <> f.price                                               -- Изменилась цена
        OR t.available <> f.available                                       -- Изменилось наличие  
;




SELECT 
    d.roll_id,
    v.name,
    r.collection,
    r.article,
    r.uri,

    MAX(d.old_price) AS old_price,
    SUM(d.old_count) AS old_count,
    MAX(d.new_price) AS new_price,
    SUM(d.new_count) AS new_count
    -- string_agg('{BASE_URL}' || a.url, '\n') as photos
FROM diff d
    JOIN roll r ON d.roll_id = r.id
    JOIN vendor v ON r.vendor_id = v.id
    -- JOIN shop s ON d.shop_id = s.id
        -- LEFT JOIN asset a ON r.id = a.roll_id
GROUP BY d.roll_id, v.name, r.collection, r.article, r.uri
;


SELECT DISTINCT roll_id
FROM diff
;


SELECT 
    v.name AS vendor_name,
    r.collection AS collection_name, 
    r.article,
    'oboykin.ru' || r.uri AS URI,           
    
    SUM(COALESCE(d.old_count, 0)) AS total_old_count,
    SUM(d.new_count) AS total_new_count,

    MAX(d.old_price) AS old_price,
    MAX(d.new_price) AS new_price,
    -- список магазинов в одну строку с переносами
    STRING_AGG(
        s.name || ': ' || COALESCE(d.old_count, 0)::text || ' -> ' || d.new_count::text, 
        E'\n'
    ) AS shops_availability,
    (
        SELECT 'oboykin.ru' || a.url 
        FROM asset a 
        WHERE a.roll_id = r.id 
        LIMIT 1
    ) AS photo_url
FROM diff d
    JOIN roll r ON d.roll_id = r.id
    JOIN vendor v ON r.vendor_id = v.id
    JOIN shop s ON d.shop_id = s.id
GROUP BY 
    d.roll_id, v.name, r.collection, r.article, r.id
;