-- Garum mock data
-- Load after data/db.sql. Reference and catalogue rows use conflict-safe
-- inserts; historical rows are intended for a fresh test database.

PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- Catalogue reference data
INSERT OR IGNORE INTO brands (name) VALUES
    ('Casa Verde'),
    ('Alpine Farms'),
    ('Panificio Roma'),
    ('Acqua Blu');

INSERT OR IGNORE INTO categories (name) VALUES
    ('Fruit'),
    ('Vegetables'),
    ('Dairy'),
    ('Grains'),
    ('Protein'),
    ('Breakfast'),
    ('Cooking fats');

INSERT OR IGNORE INTO nutrition_recommendation_sources
    (name, version, url, retrieved_at)
VALUES
    ('Garum sample nutrition dataset', '2026.1', NULL, '2026-11-01T09:00:00');

INSERT OR IGNORE INTO foods (name, brand_id, is_food) VALUES
    ('Rolled oats', (SELECT id FROM brands WHERE name = 'Alpine Farms'), 1),
    ('Greek yogurt', (SELECT id FROM brands WHERE name = 'Alpine Farms'), 1),
    ('Banana', (SELECT id FROM brands WHERE name = 'Casa Verde'), 1),
    ('Blueberries', (SELECT id FROM brands WHERE name = 'Casa Verde'), 1),
    ('Chicken breast', (SELECT id FROM brands WHERE name = 'Casa Verde'), 1),
    ('Brown rice', (SELECT id FROM brands WHERE name = 'Alpine Farms'), 1),
    ('Tomato', (SELECT id FROM brands WHERE name = 'Casa Verde'), 1),
    ('Spinach', (SELECT id FROM brands WHERE name = 'Casa Verde'), 1),
    ('Whole-wheat bread', (SELECT id FROM brands WHERE name = 'Panificio Roma'), 1),
    ('Extra virgin olive oil', (SELECT id FROM brands WHERE name = 'Casa Verde'), 1),
    ('Dish soap', (SELECT id FROM brands WHERE name = 'Casa Verde'), 0);

INSERT OR IGNORE INTO food_categories (food_id, category_id)
SELECT f.id, c.id
FROM foods AS f
JOIN categories AS c ON c.name = CASE f.name
    WHEN 'Rolled oats' THEN 'Grains'
    WHEN 'Greek yogurt' THEN 'Dairy'
    WHEN 'Banana' THEN 'Fruit'
    WHEN 'Blueberries' THEN 'Fruit'
    WHEN 'Chicken breast' THEN 'Protein'
    WHEN 'Brown rice' THEN 'Grains'
    WHEN 'Tomato' THEN 'Vegetables'
    WHEN 'Spinach' THEN 'Vegetables'
    WHEN 'Whole-wheat bread' THEN 'Grains'
    WHEN 'Extra virgin olive oil' THEN 'Cooking fats'
    ELSE ''
END
WHERE f.is_food = 1;

INSERT OR IGNORE INTO food_categories (food_id, category_id)
SELECT f.id, c.id
FROM foods AS f
JOIN categories AS c ON c.name = 'Breakfast'
WHERE f.name IN ('Rolled oats', 'Greek yogurt', 'Banana', 'Blueberries');

-- Food nutrient values use grams as the reporting basis.
INSERT OR IGNORE INTO food_nutrient_bases
    (food_id, basis_quantity, basis_unit_id, source_id)
SELECT f.id, 100, u.id,
       (SELECT id FROM nutrition_recommendation_sources
        WHERE name = 'Garum sample nutrition dataset' AND version = '2026.1')
FROM foods AS f
JOIN units AS u ON u.code = 'g'
JOIN (
    SELECT 'Rolled oats' AS food_name
    UNION ALL SELECT 'Greek yogurt'
    UNION ALL SELECT 'Banana'
    UNION ALL SELECT 'Blueberries'
    UNION ALL SELECT 'Chicken breast'
    UNION ALL SELECT 'Brown rice'
    UNION ALL SELECT 'Tomato'
    UNION ALL SELECT 'Spinach'
    UNION ALL SELECT 'Whole-wheat bread'
    UNION ALL SELECT 'Extra virgin olive oil'
) AS s ON s.food_name = f.name;

-- Common nutrient values per 100 g. Values not listed remain zero.
INSERT OR IGNORE INTO food_nutrients (food_id, base_id, nutrient_type_id, amount)
SELECT f.id, p.id, n.id, v.amount
FROM food_nutrient_bases AS p
JOIN foods AS f ON f.id = p.food_id
JOIN nutrients AS n
JOIN (
    SELECT 'Rolled oats' AS food_name, 'kcals' AS code, 389.0 AS amount
    UNION ALL SELECT 'Rolled oats', 'protein', 16.9
    UNION ALL SELECT 'Rolled oats', 'carbs', 66.3
    UNION ALL SELECT 'Rolled oats', 'sugar', 0.9
    UNION ALL SELECT 'Rolled oats', 'fat', 6.9
    UNION ALL SELECT 'Rolled oats', 'fiber', 10.6
    UNION ALL SELECT 'Greek yogurt', 'kcals', 97.0
    UNION ALL SELECT 'Greek yogurt', 'protein', 9.0
    UNION ALL SELECT 'Greek yogurt', 'carbs', 3.9
    UNION ALL SELECT 'Greek yogurt', 'sugar', 3.6
    UNION ALL SELECT 'Greek yogurt', 'fat', 5.0
    UNION ALL SELECT 'Greek yogurt', 'calcium', 110.0
    UNION ALL SELECT 'Banana', 'kcals', 89.0
    UNION ALL SELECT 'Banana', 'protein', 1.1
    UNION ALL SELECT 'Banana', 'carbs', 22.8
    UNION ALL SELECT 'Banana', 'sugar', 12.2
    UNION ALL SELECT 'Banana', 'fiber', 2.6
    UNION ALL SELECT 'Banana', 'potassium', 358.0
    UNION ALL SELECT 'Banana', 'vitamin_c', 8.7
    UNION ALL SELECT 'Blueberries', 'kcals', 57.0
    UNION ALL SELECT 'Blueberries', 'protein', 0.7
    UNION ALL SELECT 'Blueberries', 'carbs', 14.5
    UNION ALL SELECT 'Blueberries', 'sugar', 10.0
    UNION ALL SELECT 'Blueberries', 'fiber', 2.4
    UNION ALL SELECT 'Blueberries', 'vitamin_c', 9.7
    UNION ALL SELECT 'Chicken breast', 'kcals', 165.0
    UNION ALL SELECT 'Chicken breast', 'protein', 31.0
    UNION ALL SELECT 'Chicken breast', 'fat', 3.6
    UNION ALL SELECT 'Chicken breast', 'sodium', 74.0
    UNION ALL SELECT 'Chicken breast', 'vitamin_b12', 0.3
    UNION ALL SELECT 'Brown rice', 'kcals', 123.0
    UNION ALL SELECT 'Brown rice', 'protein', 2.7
    UNION ALL SELECT 'Brown rice', 'carbs', 25.6
    UNION ALL SELECT 'Brown rice', 'fiber', 1.6
    UNION ALL SELECT 'Brown rice', 'magnesium', 39.0
    UNION ALL SELECT 'Tomato', 'kcals', 18.0
    UNION ALL SELECT 'Tomato', 'protein', 0.9
    UNION ALL SELECT 'Tomato', 'carbs', 3.9
    UNION ALL SELECT 'Tomato', 'sugar', 2.6
    UNION ALL SELECT 'Tomato', 'fiber', 1.2
    UNION ALL SELECT 'Tomato', 'vitamin_c', 13.7
    UNION ALL SELECT 'Spinach', 'kcals', 23.0
    UNION ALL SELECT 'Spinach', 'protein', 2.9
    UNION ALL SELECT 'Spinach', 'carbs', 3.6
    UNION ALL SELECT 'Spinach', 'fiber', 2.2
    UNION ALL SELECT 'Spinach', 'iron', 2.7
    UNION ALL SELECT 'Spinach', 'vitamin_a', 469.0
    UNION ALL SELECT 'Spinach', 'vitamin_c', 28.1
    UNION ALL SELECT 'Whole-wheat bread', 'kcals', 247.0
    UNION ALL SELECT 'Whole-wheat bread', 'protein', 13.0
    UNION ALL SELECT 'Whole-wheat bread', 'carbs', 41.0
    UNION ALL SELECT 'Whole-wheat bread', 'fiber', 7.0
    UNION ALL SELECT 'Whole-wheat bread', 'sodium', 400.0
    UNION ALL SELECT 'Extra virgin olive oil', 'kcals', 884.0
    UNION ALL SELECT 'Extra virgin olive oil', 'fat', 100.0
) AS v ON v.food_name = f.name AND v.code = n.code;

INSERT OR IGNORE INTO suggested_frequencies
    (category_id, frequency_per_week, amount, unit_id, source_id, valid_from)
SELECT c.id, r.frequency_per_week, r.amount, u.id,
       (SELECT id FROM nutrition_recommendation_sources
        WHERE name = 'Garum sample nutrition dataset' AND version = '2026.1'),
       '2026-01-01'
FROM categories AS c
JOIN units AS u ON u.code = r.unit_code
JOIN (
    SELECT 'Fruit' AS category_name, 7.0 AS frequency_per_week, 2.0 AS amount, 'unit' AS unit_code
    UNION ALL SELECT 'Vegetables', 14.0, 400.0, 'g'
    UNION ALL SELECT 'Protein', 7.0, 150.0, 'g'
    UNION ALL SELECT 'Dairy', 7.0, 170.0, 'g'
) AS r ON r.category_name = c.name;

-- Recipes and their ingredients
INSERT OR IGNORE INTO recipes
    (name, servings)
VALUES
    ('Overnight oats', 2),
    ('Chicken rice bowl', 2);

INSERT OR IGNORE INTO recipe_ingredients (recipe_id, food_id, quantity, unit_id)
SELECT r.id, f.id, i.quantity, u.id
FROM (
    SELECT 'Overnight oats' AS recipe_name, 'Rolled oats' AS food_name, 80 AS quantity, 'g' AS unit_code
    UNION ALL SELECT 'Overnight oats', 'Greek yogurt', 340, 'g'
    UNION ALL SELECT 'Overnight oats', 'Banana', 1, 'unit'
    UNION ALL SELECT 'Overnight oats', 'Blueberries', 100, 'g'
    UNION ALL SELECT 'Chicken rice bowl', 'Chicken breast', 300, 'g'
    UNION ALL SELECT 'Chicken rice bowl', 'Brown rice', 300, 'g'
    UNION ALL SELECT 'Chicken rice bowl', 'Tomato', 150, 'g'
    UNION ALL SELECT 'Chicken rice bowl', 'Spinach', 60, 'g'
    UNION ALL SELECT 'Chicken rice bowl', 'Extra virgin olive oil', 15, 'ml'
) AS i
JOIN recipes AS r ON r.name = i.recipe_name
JOIN foods AS f ON f.name = i.food_name
JOIN units AS u ON u.code = i.unit_code;

-- Current stock, including one manually described item.
INSERT OR IGNORE INTO inventory (food_id, description, quantity, unit_id, updated_at)
SELECT f.id, '', i.quantity, u.id, i.updated_at
FROM (
    SELECT 'Rolled oats' AS food_name, 750 AS quantity, 'g' AS unit_code, '2026-11-09T18:00:00' AS updated_at
    UNION ALL SELECT 'Greek yogurt', 3, 'unit', '2026-11-10T07:30:00'
    UNION ALL SELECT 'Chicken breast', 450, 'g', '2026-11-09T18:00:00'
    UNION ALL SELECT 'Brown rice', 1, 'kg', '2026-11-08T16:00:00'
    UNION ALL SELECT 'Banana', 4, 'unit', '2026-11-10T07:30:00'
) AS i
JOIN foods AS f ON f.name = i.food_name
JOIN units AS u ON u.code = i.unit_code;

INSERT OR IGNORE INTO inventory
    (food_id, description, quantity, unit_id, updated_at)
SELECT NULL, 'Homemade tomato sauce', 500, u.id, '2026-11-09T18:00:00'
FROM units AS u
WHERE u.code = 'g';

-- Daily nutrient recommendations are stored per kilogram of body weight.
INSERT OR IGNORE INTO daily_nutrition_goals
    (nutrient_type_id, amount_per_kg, unit_id, source_id)
SELECT n.id, g.amount_per_kg, u.id,
       (SELECT id FROM nutrition_recommendation_sources
        WHERE name = 'Garum sample nutrition dataset' AND version = '2026.1')
FROM nutrients AS n
JOIN units AS u ON u.code = g.unit_code
JOIN (
    SELECT 'protein' AS code, 2.0 AS amount_per_kg, 'g' AS unit_code
    UNION ALL SELECT 'carbs', 3.0, 'g'
    UNION ALL SELECT 'fat', 1.0, 'g'
    UNION ALL SELECT 'fiber', 0.3, 'g'
    UNION ALL SELECT 'calcium', 14.3, 'mg'
    UNION ALL SELECT 'iron', 0.13, 'mg'
) AS g ON g.code = n.code;

-- Diary entries cover individual foods, recipes, and a manually entered meal.
INSERT OR IGNORE INTO consumptions
    (occurred_on, meal, food_id, recipe_id, quantity, unit_id, spend_usd, notes)
SELECT e.occurred_on, e.meal, f.id, NULL, e.quantity, u.id, e.spend_usd, e.notes
FROM (
    SELECT '2026-11-10' AS occurred_on, 'Breakfast' AS meal, 'Rolled oats' AS food_name, 40 AS quantity, 'g' AS unit_code, 0.22 AS spend_usd, 'Prepared as overnight oats.' AS notes
    UNION ALL SELECT '2026-11-10', 'Breakfast', 'Banana', 1, 'unit', 0.30, ''
    UNION ALL SELECT '2026-11-10', 'Lunch', 'Chicken breast', 150, 'g', 1.75, ''
    UNION ALL SELECT '2026-11-09', 'Breakfast', 'Greek yogurt', 170, 'g', 1.10, ''
    UNION ALL SELECT '2026-11-08', 'Snack', 'Blueberries', 148, 'g', 1.25, ''
) AS e
JOIN foods AS f ON f.name = e.food_name
JOIN units AS u ON u.code = e.unit_code;

INSERT OR IGNORE INTO consumptions
    (occurred_on, meal, recipe_id, quantity, unit_id, spend_usd, notes)
SELECT e.occurred_on, e.meal, r.id, e.quantity, u.id, e.spend_usd, e.notes
FROM (
    SELECT '2026-11-09' AS occurred_on, 'Lunch' AS meal, 'Chicken rice bowl' AS recipe_name, 1 AS quantity, 'serving' AS unit_code, 3.20 AS spend_usd, 'Two servings prepared for meal prep.' AS notes
    UNION ALL SELECT '2026-11-07', 'Dinner', 'Overnight oats', 1, 'serving', 1.40, ''
) AS e
JOIN recipes AS r ON r.name = e.recipe_name
JOIN units AS u ON u.code = e.unit_code;

INSERT OR IGNORE INTO consumptions
    (occurred_on, meal, quantity, unit_id, spend_usd, notes)
SELECT '2026-11-06', 'Dinner', 1, u.id, 2.50,
       'Manual meal entry used to test entries without a catalogue reference.'
FROM units AS u
WHERE u.code = 'serving';

-- Stores, prices, grocery bills, and purchases.
INSERT OR IGNORE INTO stores (name, location, maps_link) VALUES
    ('Mercato Centrale', 'Via Roma 10', 'https://maps.example.test/mercato-centrale'),
    ('Coop del Quartiere', 'Piazza Verdi 4', 'https://maps.example.test/coop-quartiere');

INSERT OR IGNORE INTO store_items
    (store_id, food_id, current_price, package_quantity, package_unit_id)
SELECT s.id, f.id, i.current_price, i.package_quantity, u.id
FROM (
    SELECT 'Mercato Centrale' AS store_name, 'Rolled oats' AS food_name, 2.49 AS current_price, 500 AS package_quantity, 'g' AS unit_code
    UNION ALL SELECT 'Mercato Centrale', 'Greek yogurt', 1.29, 500, 'g'
    UNION ALL SELECT 'Mercato Centrale', 'Chicken breast', 8.90, 600, 'g'
    UNION ALL SELECT 'Mercato Centrale', 'Banana', 1.79, 1, 'kg'
    UNION ALL SELECT 'Coop del Quartiere', 'Rolled oats', 2.69, 500, 'g'
    UNION ALL SELECT 'Coop del Quartiere', 'Greek yogurt', 1.19, 500, 'g'
    UNION ALL SELECT 'Coop del Quartiere', 'Brown rice', 2.99, 1, 'kg'
    UNION ALL SELECT 'Coop del Quartiere', 'Spinach', 1.49, 250, 'g'
) AS i
JOIN stores AS s ON s.name = i.store_name
JOIN foods AS f ON f.name = i.food_name
JOIN units AS u ON u.code = i.unit_code;

INSERT OR IGNORE INTO price_history (store_id, food_id, price, observed_at)
SELECT s.id, f.id, p.price, p.observed_at
FROM (
    SELECT 'Mercato Centrale' AS store_name, 'Rolled oats' AS food_name, 2.79 AS price, '2026-10-15T10:00:00' AS observed_at
    UNION ALL SELECT 'Mercato Centrale', 'Rolled oats', 2.49, '2026-11-05T10:00:00'
    UNION ALL SELECT 'Coop del Quartiere', 'Rolled oats', 2.89, '2026-10-15T10:00:00'
    UNION ALL SELECT 'Coop del Quartiere', 'Rolled oats', 2.69, '2026-11-05T10:00:00'
    UNION ALL SELECT 'Mercato Centrale', 'Greek yogurt', 1.39, '2026-10-20T10:00:00'
    UNION ALL SELECT 'Mercato Centrale', 'Greek yogurt', 1.29, '2026-11-05T10:00:00'
) AS p
JOIN stores AS s ON s.name = p.store_name
JOIN foods AS f ON f.name = p.food_name;

INSERT OR IGNORE INTO grocery_bills
    (store_id, total_amount, purchased_at, notes)
SELECT s.id, b.total_amount, b.purchased_at, b.notes
FROM stores AS s
JOIN (
    SELECT 'Mercato Centrale' AS store_name, 17.68 AS total_amount,
        '2026-11-09T17:30:00' AS purchased_at, 'Weekly grocery run.' AS notes
    UNION ALL SELECT 'Coop del Quartiere', 8.67, '2026-11-05T18:10:00',
        'Pantry restock.'
) AS b ON b.store_name = s.name;

INSERT OR IGNORE INTO purchases
    (bill_id, store_id, food_id, quantity, unit_id, unit_price,
     discount_percent, purchased_at)
SELECT b.id, s.id, f.id, p.quantity, u.id, p.unit_price,
       p.discount_percent, p.purchased_at
FROM (
    SELECT '2026-11-09T17:30:00' AS bill_purchased_at, 'Mercato Centrale' AS store_name,
        'Rolled oats' AS food_name, 1 AS quantity, 'unit' AS unit_code,
        2.49 AS unit_price, 0 AS discount_percent, '2026-11-09T17:30:00' AS purchased_at
    UNION ALL SELECT '2026-11-09T17:30:00', 'Mercato Centrale', 'Greek yogurt', 2, 'unit', 1.29, 0, '2026-11-09T17:30:00'
    UNION ALL SELECT '2026-11-09T17:30:00', 'Mercato Centrale', 'Chicken breast', 1, 'unit', 8.90, 10, '2026-11-09T17:30:00'
    UNION ALL SELECT '2026-11-05T18:10:00', 'Coop del Quartiere', 'Rolled oats', 1, 'unit', 2.69, 0, '2026-11-05T18:10:00'
    UNION ALL SELECT '2026-11-05T18:10:00', 'Coop del Quartiere', 'Brown rice', 1, 'unit', 2.99, 0, '2026-11-05T18:10:00'
    UNION ALL SELECT '2026-11-05T18:10:00', 'Coop del Quartiere', 'Spinach', 2, 'unit', 1.49, 0, '2026-11-05T18:10:00'
) AS p
JOIN stores AS s ON s.name = p.store_name
JOIN foods AS f ON f.name = p.food_name
JOIN units AS u ON u.code = p.unit_code
JOIN grocery_bills AS b ON b.store_id = s.id
    AND b.purchased_at = p.bill_purchased_at;

COMMIT;