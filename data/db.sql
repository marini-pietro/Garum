-- Garum database overview
-- ========================
--
-- This SQLite database separates reusable food information from the events in
-- which food is eaten or purchased. 
-- Often in the tables there is already a valid candidate key but an additional id column
-- is added as a surrogate key to simplify foreign key relationships, allow for easier expansion in the future and have simpler indexes.
-- The central flow is:
--
--   brands/categories -> foods -> nutrient_profiles -> nutrient_values
--                              |
--                              +-> food_servings
--                              +-> recipe_ingredients <- recipes
--                              +-> food_entries
--                              +-> store_items <- stores
--                                                   |
--                                                   +-> price_history
--                                                   +-> purchases
--
-- Reference data
-- --------------
-- brands
--   One row per food brand. foods.brand_id optionally points to a brand.
--   Brands are separate so their names remain consistent and can later carry
--   metadata without duplicating it in every food row.
--
-- categories
--   One row per food category. foods.category_id optionally groups foods into
--   categories, and suggested_frequencies uses categories to describe
--   recommended consumption patterns.
--
-- units
--   The controlled vocabulary for quantities such as grams, litres, units,
--   and servings. It is referenced by nutrition profiles, food servings,
--   recipes, recommendations, purchases, and store packages.
--
-- nutrition_recommendation_sources
--   The origin and version of nutrition or recommendation data. Profiles and
--   suggested frequencies can reference a source so displayed values remain
--   explainable and reproducible.
--
-- Food and nutrition catalogue
-- ----------------------------
-- foods
--   The canonical catalogue of foods or products. It references an optional
--   brand and category, but does not contain consumption or purchase events.
--   A food can have one nutrient profile, many named servings, many recipe
--   uses, many food-log entries, and many store listings.
--
-- nutrient_profiles
--   Defines the basis for a food's nutrition data, such as 100 g, 100 ml, or
--   one serving. It belongs to one food and can reference measurement units
--   and a nutrition source.
--
-- nutrients
--   Defines nutrient identities and their display units, for example protein
--   in grams or calcium in milligrams. Keeping this list separate allows new
--   nutrients to be added without altering the schema.
--
-- nutrient_values
--   Stores the amount of each nutrient in a nutrient profile. It is the
--   many-to-many bridge between nutrient_profiles and nutrients, with one
--   value per profile/nutrient pair.
--
-- food_servings
--   Stores optional named household measures for a food, such as "one bowl"
--   or "one slice", and their base quantity. A food can have many servings;
--   each serving uses one unit from units.
--
-- suggested_frequencies
--   Stores category-level consumption recommendations, including frequency,
--   amount, unit, source, and optional validity dates. It is separate from
--   foods because recommendations apply to categories and may vary by source
--   or over time.
--
-- Recipes and consumption
-- -----------------------
-- recipes
--   One row per prepared dish. A recipe has a serving count and is composed
--   of foods through recipe_ingredients.
--
-- recipe_ingredients
--   The many-to-many bridge between recipes and foods. Each row records how
--   much of one food a recipe uses. Recipes can therefore be reused in many
--   food-log entries without copying their ingredients.
--
-- food_entries
--   The historical food diary. Each row represents food consumed at a meal
--   and may reference either a food or a recipe, never both. It stores the
--   consumed quantity and nutrition totals as snapshots so historical logs do
--   not silently change when a product label or recipe is edited. It can also
--   contain manually entered totals and notes.
--
-- Shopping and prices
-- -------------------
-- stores
--   One row per shop or location where the users purchases foods.
--
-- store_items
--   The many-to-many bridge table between stores and foods. It represents a food
--   being sold at a store, including its current price and package size.
--   Its composite primary key prevents duplicate store-food listings.
--
-- price_history
--   Historical observations of a store item's price. Each row belongs to an
--   existing store_items row, allowing price trends without overwriting past
--   values.
--
-- purchases
--   The historical shopping ledger. Each purchase identifies a store-food
--   combination, quantity, unit price, discount, and purchase time. It
--   references store_items to prevent recording a purchase from a store that
--   does not sell that food.
--
-- Relationship conventions
-- ------------------------
-- Foreign keys are enabled below. ON DELETE CASCADE is used for dependent
-- detail rows that have no meaning without their parent (for example recipe
-- ingredients). ON DELETE SET NULL is used where the historical row should
-- remain valid if optional catalogue metadata is removed (for example a
-- brand or a food).

PRAGMA foreign_keys = ON; -- Enable foreign key constraints in SQLite.

-- Table that stores the brands of foods. Each brand has a unique name.
-- Useful to keep a separate table for brands to avoid duplication and maintain consistency across the database.
CREATE TABLE IF NOT EXISTS brands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Table that stores the categories of foods. Each category has a unique name.
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Table that stores the units of measurement for food quantities. 
-- Each unit has a unique code and name, and a kind that indicates whether it is a mass, volume, count, or serving unit.
CREATE TABLE IF NOT EXISTS units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE, -- The code is a short identifier for the unit, such as 'g' for grams or 'ml' for millilitres.
    name TEXT NOT NULL, -- The name is a human-readable description of the unit, such as 'Gram' or 'Millilitre'.
    kind TEXT NOT NULL CHECK (kind IN ('mass', 'volume', 'count', 'serving'))
);
-- Insert initial data into the units table
INSERT OR IGNORE INTO units (code, name, kind) VALUES
    ('g', 'Gram', 'mass'),
    ('kg', 'Kilogram', 'mass'),
    ('ml', 'Millilitre', 'volume'),
    ('l', 'Litre', 'volume'),
    ('unit', 'Unit', 'count'),
    ('serving', 'Serving', 'serving');

-- Table that stores the sources of nutrition data.
-- Each source has a unique name and version, and may have a URL and a timestamp indicating when the data was retrieved.
CREATE TABLE IF NOT EXISTS nutrition_recommendation_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, -- The name is a required string that identifies the source, such as 'USDA FoodData Central' or 'WHO Nutrient Recommendations'.
    version TEXT, -- The version is an optional string that indicates the version of the source, such as '2021-01' or 'v2.0'.
    url TEXT, -- The URL is an optional link to the source's website or documentation.
    retrieved_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- The retrieved_at timestamp indicates when the source data was last retrieved or updated.
    UNIQUE (name, version) -- Composite unique constraint on name and version to prevent duplicate sources with the same name and version.
);

-- Table that stores the foods. Each food has a name, and may belong to a brand and a category.
CREATE TABLE IF NOT EXISTS foods (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    name TEXT NOT NULL, -- The name is a required string that identifies the food, such as 'Apple' or 'Chicken Breast'.
    brand_id INTEGER, -- The brand_id is an optional foreign key that references the brands table, indicating the brand of the food. It can be NULL if the food has no brand or the user doesn't want to track it.
    category_id INTEGER, -- The category_id is an optional foreign key that references the categories table, indicating the category of the food. It can be NULL if the food has no category or the user doesn't want to track it.
    is_food INTEGER NOT NULL DEFAULT 1 CHECK (is_food IN (0, 1)), -- SQLite does not have a boolean type, use INTEGER with 0/1 values.
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (brand_id) REFERENCES brands(id) ON DELETE SET NULL, -- If a brand is deleted, set the brand_id to NULL in the foods table.
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL, -- If a category is deleted, set the category_id to NULL in the foods table.
    UNIQUE (brand_id, name) -- Composite unique constraint on brand_id and name to prevent duplicate foods with the same brand and name.
);

-- A profile describes the quantity against which nutrition values are reported.
CREATE TABLE IF NOT EXISTS nutrient_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_id INTEGER NOT NULL UNIQUE,
    basis_quantity REAL NOT NULL DEFAULT 100 CHECK (basis_quantity > 0),
    basis_unit_id INTEGER NOT NULL,
    serving_name TEXT,
    serving_quantity REAL CHECK (serving_quantity IS NULL OR serving_quantity > 0),
    serving_unit_id INTEGER,
    source_id INTEGER,
    FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE CASCADE,
    FOREIGN KEY (basis_unit_id) REFERENCES units(id),
    FOREIGN KEY (serving_unit_id) REFERENCES units(id),
    FOREIGN KEY (source_id) REFERENCES nutrition_recommendation_sources(id) ON DELETE SET NULL
);

-- Table that stores the nutrients names, types, codes, and units.
CREATE TABLE IF NOT EXISTS nutrients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK (type IN ('macronutrient', 'vitamin', 'mineral', 'other')),
    code TEXT NOT NULL UNIQUE, -- The code is a short identifier for the nutrient, such as 'sat_fat' or 'calcium'.
    name TEXT NOT NULL, -- The name is a human-readable description of the nutrient, such as 'Saturated Fat' or 'Calcium'.
    unit TEXT NOT NULL -- The unit is a string that indicates the measurement unit for the nutrient, such as 'g' for grams or 'mg' for milligrams.
);
-- Insert initial data into the nutrients table.
INSERT OR IGNORE INTO nutrients (code, type, name, unit) VALUES
    ('kcals', 'macronutrient', 'Calories', 'kcal'),
    ('protein', 'macronutrient', 'Protein', 'g'),
    ('carbs', 'macronutrient', 'Carbohydrates', 'g'),
    ('sugar', 'macronutrient', 'Sugars', 'g'),
    ('fat', 'macronutrient', 'Total fat', 'g'),
    ('sat_fat', 'macronutrient', 'Saturated fat', 'g'),
    ('fiber', 'macronutrient', 'Fiber', 'g'),
    ('sodium', 'mineral', 'Sodium', 'mg'),
    ('calcium', 'mineral', 'Calcium', 'mg'),
    ('iron', 'mineral', 'Iron', 'mg'),
    ('magnesium', 'mineral', 'Magnesium', 'mg'),
    ('potassium', 'mineral', 'Potassium', 'mg'),
    ('vitamin_a', 'vitamin', 'Vitamin A', 'ug'),
    ('vitamin_c', 'vitamin', 'Vitamin C', 'mg'),
    ('vitamin_d', 'vitamin', 'Vitamin D', 'ug'),
    ('vitamin_b12', 'vitamin', 'Vitamin B12', 'ug'),
    ('folate', 'vitamin', 'Folate', 'ug');

-- Table that stores the nutrient values for each food's nutrient profile.
-- Each nutrient value is associated with a nutrient type and has an amount that must be non-negative.
CREATE TABLE IF NOT EXISTS nutrient_values (
    profile_id INTEGER NOT NULL, 
    nutrient_type_id INTEGER NOT NULL,
    amount REAL NOT NULL CHECK (amount >= 0),
    PRIMARY KEY (profile_id, nutrient_type_id),
    FOREIGN KEY (profile_id) REFERENCES nutrient_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (nutrient_type_id) REFERENCES nutrients(id) ON DELETE CASCADE
);

-- Optional alternate package or household measures for a food.
-- For example, a user may say that they ate "1 cup of rice" instead of "200 grams of rice".
-- This table allows for storing such alternate measures.
CREATE TABLE IF NOT EXISTS food_servings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    quantity REAL NOT NULL CHECK (quantity > 0),
    unit_id INTEGER NOT NULL,
    FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE CASCADE,
    FOREIGN KEY (unit_id) REFERENCES units(id),
    UNIQUE (food_id, name)
);

CREATE TABLE IF NOT EXISTS suggested_frequencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    frequency_per_week REAL NOT NULL CHECK (frequency_per_week >= 0),
    amount REAL NOT NULL CHECK (amount >= 0),
    unit_id INTEGER NOT NULL,
    source_id INTEGER,
    valid_from TEXT,
    valid_to TEXT,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    FOREIGN KEY (unit_id) REFERENCES units(id),
    FOREIGN KEY (source_id) REFERENCES nutrition_recommendation_sources(id) ON DELETE SET NULL,
    CHECK (valid_to IS NULL OR valid_from IS NULL OR valid_to >= valid_from)
);

-- Table that stores the recipes.
-- Each recipe has a name and a timestamp indicating when it was created.
-- Recipes are only intended as a quick way for the user to insert data.
-- Instead of inserting each ingredient separately, the user can create a recipe and then select the recipe to quickly insert all ingredients.
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE, -- The name is a required string that identifies the recipe.
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table that stores the ingredients of each recipe.
-- Each ingredient is associated with a food and has a quantity and unit of measurement.
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    recipe_id INTEGER NOT NULL, -- The recipe_id is a foreign key that references the recipes table, indicating which recipe the ingredient belongs to.
    food_id INTEGER NOT NULL, -- The food_id is a foreign key that references the foods table, indicating which food is used as an ingredient in the recipe.
    quantity REAL NOT NULL CHECK (quantity > 0), -- The quantity is a required positive number that indicates how much of the food is used in the recipe (e.g. 2 of a particular food that is a 400g can).
    unit_id INTEGER NOT NULL, -- The unit_id is a foreign key that references the units table, indicating the unit of measurement for the quantity (e.g. grams, millilitres, etc.).
    PRIMARY KEY (recipe_id, food_id), -- Composite primary key on recipe_id and food_id to prevent duplicate ingredients for the same recipe.
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE, -- If a recipe is deleted, all its ingredients are also deleted.
    FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE SET NULL, -- If a food is deleted, the ingredient remains but the food_id is set to NULL.
    FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE SET NULL -- If a unit is deleted, the ingredient remains but the unit_id is set to NULL.
);

-- Denormalized nutrition columns are snapshots: historical entries do not change
-- when a food label or nutrient profile is updated.
CREATE TABLE IF NOT EXISTS food_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    occurred_on TEXT NOT NULL, -- The date and time when the food was consumed, stored as a text string in ISO 8601 format.
    meal TEXT NOT NULL,
    food_id INTEGER,
    recipe_id INTEGER,
    quantity REAL CHECK (quantity IS NULL OR quantity > 0),
    unit_id INTEGER,
    calories_kcal REAL NOT NULL CHECK (calories_kcal >= 0),
    spend_usd REAL NOT NULL CHECK (spend_usd >= 0),
    protein_g REAL NOT NULL DEFAULT 0 CHECK (protein_g >= 0),
    carbs_g REAL NOT NULL DEFAULT 0 CHECK (carbs_g >= 0),
    sugar_g REAL NOT NULL DEFAULT 0 CHECK (sugar_g >= 0 AND sugar_g <= carbs_g),
    fat_g REAL NOT NULL DEFAULT 0 CHECK (fat_g >= 0),
    saturated_fat_g REAL NOT NULL DEFAULT 0 CHECK (saturated_fat_g >= 0 AND saturated_fat_g <= fat_g),
    fiber_g REAL NOT NULL DEFAULT 0 CHECK (fiber_g >= 0),
    sodium_mg REAL NOT NULL DEFAULT 0 CHECK (sodium_mg >= 0),
    calcium_mg REAL NOT NULL DEFAULT 0 CHECK (calcium_mg >= 0),
    iron_mg REAL NOT NULL DEFAULT 0 CHECK (iron_mg >= 0),
    magnesium_mg REAL NOT NULL DEFAULT 0 CHECK (magnesium_mg >= 0),
    potassium_mg REAL NOT NULL DEFAULT 0 CHECK (potassium_mg >= 0),
    vitamin_a_ug REAL NOT NULL DEFAULT 0 CHECK (vitamin_a_ug >= 0),
    vitamin_c_mg REAL NOT NULL DEFAULT 0 CHECK (vitamin_c_mg >= 0),
    vitamin_d_ug REAL NOT NULL DEFAULT 0 CHECK (vitamin_d_ug >= 0),
    vitamin_b12_ug REAL NOT NULL DEFAULT 0 CHECK (vitamin_b12_ug >= 0),
    folate_ug REAL NOT NULL DEFAULT 0 CHECK (folate_ug >= 0),
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE SET NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE SET NULL,
    FOREIGN KEY (unit_id) REFERENCES units(id),
    CHECK (food_id IS NULL OR recipe_id IS NULL)
);

-- Table that stores the stores where food items are sold.
--Each store has a name, location, and an optional link to a map.
CREATE TABLE IF NOT EXISTS stores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, -- The name is a required string that identifies the store, such as 'Conad' or 'Poli'.
    location TEXT, -- The location is an optional string that describes the store's address or area, such as 'Via Roma 10, Milano'.
    maps_link TEXT, -- The maps_link is an optional string that contains a URL to a map or navigation service for the store's location.
    UNIQUE (name, location) -- Composite unique constraint on name and location to prevent duplicate stores with the same name and location.
);

-- Table that stores the items sold in each store.
-- Enables various analyses, such as where the user gets the majority of their nutritional needs.
CREATE TABLE IF NOT EXISTS store_items (
    store_id INTEGER NOT NULL,
    food_id INTEGER NOT NULL,
    current_price REAL NOT NULL DEFAULT 0 CHECK (current_price >= 0),
    -- The package_quantity is an optional real number that represents the quantity of the food item in the package.
    package_quantity REAL CHECK (package_quantity IS NULL OR package_quantity > 0),
    package_unit_id INTEGER,
    PRIMARY KEY (store_id, food_id),
    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE CASCADE,
    FOREIGN KEY (package_unit_id) REFERENCES units(id)
);

-- Table that stores the historical prices of food items in each store.
-- This allows for tracking price changes over time and analyzing trends.
CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    store_id INTEGER NOT NULL, -- The store_id is a foreign key that references the stores table, indicating which store the price observation belongs to.
    food_id INTEGER NOT NULL, -- The food_id is a foreign key that references the foods table, indicating which food item's price is being recorded.
    price REAL NOT NULL CHECK (price >= 0),
    observed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id, food_id) REFERENCES store_items(store_id, food_id) ON DELETE CASCADE
);

-- Table that stores the purchases made by the user.
-- Each purchase is associated with a store, a food item, a quantity, a unit of measurement, 
-- a unit price, and an optional discount percentage.
CREATE TABLE IF NOT EXISTS purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    store_id INTEGER NOT NULL,
    food_id INTEGER NOT NULL,
    quantity REAL NOT NULL CHECK (quantity > 0),
    unit_id INTEGER NOT NULL, --
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    discount_percent REAL NOT NULL DEFAULT 0 CHECK (discount_percent >= 0 AND discount_percent <= 100),
    purchased_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id, food_id) REFERENCES store_items(store_id, food_id),
    FOREIGN KEY (unit_id) REFERENCES units(id)
);

-- Create indexes to improve query performance on frequently queried columns.
CREATE INDEX IF NOT EXISTS idx_foods_category_id
    ON foods(category_id);

CREATE INDEX IF NOT EXISTS idx_nutrient_profiles_source_id
    ON nutrient_profiles(source_id);

CREATE INDEX IF NOT EXISTS idx_nutrient_profiles_basis_unit_id
    ON nutrient_profiles(basis_unit_id);

CREATE INDEX IF NOT EXISTS idx_nutrient_profiles_serving_unit_id
    ON nutrient_profiles(serving_unit_id);

CREATE INDEX IF NOT EXISTS idx_nutrient_values_nutrient_type_id
    ON nutrient_values(nutrient_type_id);

CREATE INDEX IF NOT EXISTS idx_food_servings_unit_id
    ON food_servings(unit_id);

CREATE INDEX IF NOT EXISTS idx_suggested_frequencies_category_validity
    ON suggested_frequencies(category_id, valid_from, valid_to);

CREATE INDEX IF NOT EXISTS idx_suggested_frequencies_source_id
    ON suggested_frequencies(source_id);

CREATE INDEX IF NOT EXISTS idx_suggested_frequencies_unit_id
    ON suggested_frequencies(unit_id);

CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_food_id
    ON recipe_ingredients(food_id);

CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_unit_id
    ON recipe_ingredients(unit_id);

CREATE INDEX IF NOT EXISTS idx_food_entries_occurred_on
    ON food_entries(occurred_on);

CREATE INDEX IF NOT EXISTS idx_food_entries_food_occurred_on
    ON food_entries(food_id, occurred_on);

CREATE INDEX IF NOT EXISTS idx_food_entries_recipe_occurred_on
    ON food_entries(recipe_id, occurred_on);

CREATE INDEX IF NOT EXISTS idx_food_entries_unit_id
    ON food_entries(unit_id);

CREATE INDEX IF NOT EXISTS idx_stores_name
    ON stores(name);

CREATE INDEX IF NOT EXISTS idx_store_items_food_id
    ON store_items(food_id);

CREATE INDEX IF NOT EXISTS idx_store_items_package_unit_id
    ON store_items(package_unit_id);

CREATE INDEX IF NOT EXISTS idx_price_history_store_food_observed_at
    ON price_history(store_id, food_id, observed_at);

CREATE INDEX IF NOT EXISTS idx_price_history_food_observed_at
    ON price_history(food_id, observed_at);

CREATE INDEX IF NOT EXISTS idx_purchases_store_food_purchased_at
    ON purchases(store_id, food_id, purchased_at);

CREATE INDEX IF NOT EXISTS idx_purchases_food_purchased_at
    ON purchases(food_id, purchased_at);

CREATE INDEX IF NOT EXISTS idx_purchases_purchased_at
    ON purchases(purchased_at);

CREATE INDEX IF NOT EXISTS idx_purchases_unit_id
    ON purchases(unit_id);