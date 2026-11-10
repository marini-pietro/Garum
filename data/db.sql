-- Garum database overview
-- ========================
--
-- This SQLite database separates reusable food information from the events in
-- which food is eaten or purchased. 
-- Often in the tables there is already a valid candidate key but an additional id column
-- is added as a surrogate key to simplify foreign key relationships, allow for easier expansion in the future and have simpler indexes.
-- The central flow is:
--
--   brands/categories -> items -> food_nutrient_bases -> food_nutrients
--                              |
--                              +-> consumptions
--                              +-> recipe_ingredients <- recipes
--                              +-> inventory
--                              +-> consumptions
--                              +-> store_items <- stores
--                                                   |
--                                                   +-> price_history
--                                                   +-> grocery_bills <- purchases
--
-- Reference data
-- --------------
-- brands
--   One row per food brand. foods.brand_id optionally points to a brand.
--   Brands are separate so their names remain consistent and can later carry
--   metadata without duplicating it in every food row, saving memory and allowing for easier updates.
--
-- categories
--   One row per food category. food_categories links foods to one or more
--   categories, and suggested_frequencies uses categories to describe
--   recommended consumption patterns.
--   Categories are user-defined and can be used to group foods in the GUI,
--   for example by cuisine, meal type, or dietary preference.
--   One food may participate in multiple categories.
--   Because categories are user-defined, users can choose the level of detail
--   with which they classify foods. For example, a user may create a broad
--   category such as "Fish" and a more specific category such as "Swordfish",
--   then assign a swordfish food to both. This allows dietary intake to be
--   tracked at multiple levels of granularity. In this example, the user can
--   monitor fish consumption overall while also tracking swordfish specifically,
--   which is useful because swordfish is known to contain higher levels of
--   mercury than many other fish.
--
-- units
--   The controlled vocabulary for quantities such as grams, litres, units,
--   and servings. It is referenced by food nutrition bases, consumptions,
--   recipes, recommendations, purchases, and packages.
--
-- nutrition_recommendation_sources
--   The origin and version of nutrition or recommendation data. Food nutrition
--   bases, daily goals, and suggested frequencies can reference a source so displayed values remain
--   explainable and traceable to their origin.
--
-- Item and nutrition catalogue
-- ----------------------------
-- foods
--   The canonical catalogue of items. The is_food flag distinguishes food
--   items from non-food products. Every food is an item, but non-food items
--   cannot have nutrition profiles, servings, recipe uses, or food-log entries.
--   Food categories are stored in the food_categories junction table.
--   Both kinds of item can participate in inventory, store listings, purchases,
--   and price analytics.
--
-- food_nutrient_bases
--   Defines the quantity and unit against which a food's nutrition values are
--   reported, normally 100 g but also suitable for supplements and servings.
--   Each base belongs to one food and can reference a nutrition source.
--
-- nutrients
--   Defines nutrient identities and their display units (e.g. protein in grams, magnesium in milligrams).
--   Keeping this list separate allows new nutrients to be added without altering the schema.
--
-- food_nutrients
--   Stores the amount of each nutrient for a food nutrition base.
--
-- daily_nutrition_goals
--   Stores editable daily nutrient recommendations as an amount per kilogram
--   of body weight per day, with units and traceable recommendation sources.
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
--   One row per prepared dish with its serving count. Nutrition totals are
--   calculated from the current ingredient data when needed.
--
-- recipe_ingredients
--   The many-to-many bridge between recipes and foods. Each row records how
--   much of one food a recipe uses. Recipes can therefore be reused in many
--   food-log entries without copying their ingredients.
--
-- inventory
--   The current quantity snapshot for catalogue items or manually described
--   products. Manual descriptions can later be added to the catalogue.
--
-- consumptions
--   The historical food diary. Each row represents food consumed at a meal
--   and may reference either a food or a recipe, never both.
--
-- Shopping and prices
-- -------------------
-- stores
--   One row per shop or location where the user purchases items.
--
-- store_items
--   The many-to-many bridge table between stores and items. It represents an
--   item being sold at a store, including its current price and package size.
--   Its composite primary key prevents duplicate store-item listings.
--
-- price_history
--   Historical observations of a store item's price. Each row belongs to an
--   existing store_items row, allowing price trends without overwriting past
--   values.
--
-- purchases
--   The historical line-item shopping ledger. Each purchase identifies a
--   store-item combination, quantity, unit price, discount, and purchase time.
--   It references store_items to prevent recording a purchase from a store
--   that does not sell that food, and can belong to a grocery bill.
--
-- grocery_bills
--   A grocery receipt or bill that groups purchases made at one store. Its
--   total supports grocery-bill history alongside individual price records.
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

-- Table that stores catalogue items. Every food is an item, but an item is not
-- necessarily food. Food-only relationships are enforced by triggers below.
CREATE TABLE IF NOT EXISTS foods (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    name TEXT NOT NULL, -- The name identifies the item, such as 'Apple' or 'Dish soap'.
    brand_id INTEGER, -- Optional brand shared by food and non-food items.
    is_food INTEGER NOT NULL DEFAULT 1 CHECK (is_food IN (0, 1)), -- 1 means the item is food and may have nutrition data; 0 means non-food and all food-only foreign keys must be absent.
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (brand_id) REFERENCES brands(id) ON DELETE SET NULL, -- If a brand is deleted, set the brand_id to NULL in the foods table.
    UNIQUE (brand_id, name) -- Composite unique constraint on brand_id and name to prevent duplicate foods with the same brand and name.
);

-- Junction table that assigns one food to multiple categories.
-- For example, a ham pizza can belong to both red meat and baked goods.
CREATE TABLE IF NOT EXISTS food_categories (
    food_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    PRIMARY KEY (food_id, category_id),
    FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- The quantity and unit against which a food's nutrient values are reported.
-- One basis is stored per food; 100 g is common, but supplements and serving
-- based products can use another quantity and unit.
CREATE TABLE IF NOT EXISTS food_nutrient_bases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_id INTEGER NOT NULL UNIQUE,
    basis_quantity REAL NOT NULL DEFAULT 100 CHECK (basis_quantity > 0),
    basis_unit_id INTEGER NOT NULL,
    source_id INTEGER,
    FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE CASCADE,
    FOREIGN KEY (basis_unit_id) REFERENCES units(id),
    FOREIGN KEY (source_id) REFERENCES nutrition_recommendation_sources(id) ON DELETE SET NULL
);

-- Table that stores the nutrient names, types, codes, and units.
CREATE TABLE IF NOT EXISTS nutrients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK (type IN ('macronutrient', 'vitamin', 'mineral', 'other')),
    code TEXT NOT NULL UNIQUE, -- The code is a short identifier for the nutrient, such as 'sat_fat' or 'calcium'.
    name TEXT NOT NULL, -- The name is a human-readable description of the nutrient, such as 'Saturated Fat' or 'Calcium'.
    unit TEXT NOT NULL
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

-- Nutrient amounts belonging to a food nutrient basis.
CREATE TABLE IF NOT EXISTS food_nutrients (
    food_id INTEGER NOT NULL,
    base_id INTEGER NOT NULL,
    nutrient_type_id INTEGER NOT NULL,
    amount REAL NOT NULL CHECK (amount >= 0),
    PRIMARY KEY (food_id, nutrient_type_id),
    FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE CASCADE,
    FOREIGN KEY (base_id) REFERENCES food_nutrient_bases(id) ON DELETE CASCADE,
    FOREIGN KEY (nutrient_type_id) REFERENCES nutrients(id) ON DELETE CASCADE
);

-- Editable daily nutrient recommendations, expressed per kilogram of body
-- weight per day. Units and sources make each recommendation traceable.
CREATE TABLE IF NOT EXISTS daily_nutrition_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nutrient_type_id INTEGER NOT NULL,
    amount_per_kg REAL NOT NULL CHECK (amount_per_kg >= 0),
    unit_id INTEGER NOT NULL,
    source_id INTEGER,
    FOREIGN KEY (nutrient_type_id) REFERENCES nutrients(id) ON DELETE CASCADE,
    FOREIGN KEY (unit_id) REFERENCES units(id),
    FOREIGN KEY (source_id) REFERENCES nutrition_recommendation_sources(id) ON DELETE SET NULL,
    UNIQUE (nutrient_type_id)
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
-- Each recipe has a name, serving count, and timestamp indicating when it was created.
-- Recipes are only intended as a quick way for the user to insert data.
-- Instead of inserting each ingredient separately, the user can create a recipe and then select the recipe to quickly insert all ingredients.
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE, -- The name is a required string that identifies the recipe.
    servings INTEGER NOT NULL DEFAULT 1 CHECK (servings > 0),
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
    FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE CASCADE, -- If a food is deleted, recipe ingredients using it are deleted.
    FOREIGN KEY (unit_id) REFERENCES units(id) -- Units remain required for recipe ingredients, so they cannot be deleted while referenced.
);

-- Table that stores the current inventory snapshot.
-- A row can reference a catalogue product or keep a manual description until
-- the user decides to add that product to the catalogue.
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_id INTEGER,
    description TEXT NOT NULL DEFAULT '',
    quantity REAL NOT NULL CHECK (quantity >= 0),
    unit_id INTEGER NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE SET NULL,
    FOREIGN KEY (unit_id) REFERENCES units(id),
    CHECK (food_id IS NOT NULL OR length(trim(description)) > 0),
    UNIQUE (food_id, description, unit_id)
);

-- Historical food diary entries. Nutrient totals are resolved from the linked
-- food or recipe instead of being duplicated in each consumption row.
CREATE TABLE IF NOT EXISTS consumptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    occurred_on TEXT NOT NULL, -- The date and time when the food was consumed, stored as a text string in ISO 8601 format.
    meal TEXT NOT NULL,
    food_id INTEGER,
    recipe_id INTEGER,
    quantity REAL CHECK (quantity IS NULL OR quantity > 0),
    unit_id INTEGER,
    spend_usd REAL NOT NULL CHECK (spend_usd >= 0),
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
-- a unit price, and an optional discount percentage. Purchases may be grouped
-- under a grocery bill.
CREATE TABLE IF NOT EXISTS grocery_bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    store_id INTEGER NOT NULL,
    total_amount REAL NOT NULL CHECK (total_amount >= 0),
    purchased_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id INTEGER,
    store_id INTEGER NOT NULL,
    food_id INTEGER NOT NULL,
    quantity REAL NOT NULL CHECK (quantity > 0),
    unit_id INTEGER NOT NULL, --
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    discount_percent REAL NOT NULL DEFAULT 0 CHECK (discount_percent >= 0 AND discount_percent <= 100),
    purchased_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bill_id) REFERENCES grocery_bills(id) ON DELETE SET NULL,
    FOREIGN KEY (store_id, food_id) REFERENCES store_items(store_id, food_id),
    FOREIGN KEY (unit_id) REFERENCES units(id)
);

-- SQLite CHECK constraints cannot inspect another table, so these triggers
-- enforce the is_food flag across the food-only relationships. A non-food
-- item can still be referenced by inventory, stores, prices, and purchases.
CREATE TRIGGER IF NOT EXISTS foods_prevent_non_food_dependencies
BEFORE UPDATE OF is_food ON foods
WHEN NEW.is_food = 0
    AND (
        EXISTS (SELECT 1 FROM food_nutrient_bases WHERE food_id = NEW.id)
        OR EXISTS (SELECT 1 FROM food_categories WHERE food_id = NEW.id)
        OR EXISTS (SELECT 1 FROM recipe_ingredients WHERE food_id = NEW.id)
        OR EXISTS (SELECT 1 FROM consumptions WHERE food_id = NEW.id)
    )
BEGIN
    SELECT RAISE(ABORT, 'non-food items cannot have food-only dependencies');
END;

CREATE TRIGGER IF NOT EXISTS food_categories_require_food
BEFORE INSERT ON food_categories
WHEN NOT EXISTS (
    SELECT 1 FROM foods WHERE id = NEW.food_id AND is_food = 1
)
BEGIN
    SELECT RAISE(ABORT, 'categories require a food item');
END;

CREATE TRIGGER IF NOT EXISTS food_categories_update_require_food
BEFORE UPDATE OF food_id ON food_categories
WHEN NOT EXISTS (
    SELECT 1 FROM foods WHERE id = NEW.food_id AND is_food = 1
)
BEGIN
    SELECT RAISE(ABORT, 'categories require a food item');
END;

CREATE TRIGGER IF NOT EXISTS food_nutrient_bases_require_food
BEFORE INSERT ON food_nutrient_bases
WHEN NOT EXISTS (
    SELECT 1 FROM foods WHERE id = NEW.food_id AND is_food = 1
)
BEGIN
    SELECT RAISE(ABORT, 'food nutrient bases require a food item');
END;

CREATE TRIGGER IF NOT EXISTS food_nutrient_bases_update_require_food
BEFORE UPDATE OF food_id ON food_nutrient_bases
WHEN NOT EXISTS (
    SELECT 1 FROM foods WHERE id = NEW.food_id AND is_food = 1
)
BEGIN
    SELECT RAISE(ABORT, 'food nutrient bases require a food item');
END;

CREATE TRIGGER IF NOT EXISTS recipe_ingredients_require_food
BEFORE INSERT ON recipe_ingredients
WHEN NOT EXISTS (
    SELECT 1 FROM foods WHERE id = NEW.food_id AND is_food = 1
)
BEGIN
    SELECT RAISE(ABORT, 'recipe ingredients require a food item');
END;

CREATE TRIGGER IF NOT EXISTS recipe_ingredients_update_require_food
BEFORE UPDATE OF food_id ON recipe_ingredients
WHEN NOT EXISTS (
    SELECT 1 FROM foods WHERE id = NEW.food_id AND is_food = 1
)
BEGIN
    SELECT RAISE(ABORT, 'recipe ingredients require a food item');
END;

CREATE TRIGGER IF NOT EXISTS consumptions_require_food
BEFORE INSERT ON consumptions
WHEN NEW.food_id IS NOT NULL
    AND NOT EXISTS (
        SELECT 1 FROM foods WHERE id = NEW.food_id AND is_food = 1
    )
BEGIN
    SELECT RAISE(ABORT, 'consumptions require a food item');
END;

CREATE TRIGGER IF NOT EXISTS consumptions_update_require_food
BEFORE UPDATE OF food_id ON consumptions
WHEN NEW.food_id IS NOT NULL
    AND NOT EXISTS (
        SELECT 1 FROM foods WHERE id = NEW.food_id AND is_food = 1
    )
BEGIN
    SELECT RAISE(ABORT, 'consumptions require a food item');
END;

-- Create indexes to improve query performance on frequently queried columns.
CREATE INDEX IF NOT EXISTS idx_food_categories_category_id
    ON food_categories(category_id);

CREATE INDEX IF NOT EXISTS idx_food_nutrient_bases_source_id
    ON food_nutrient_bases(source_id);

CREATE INDEX IF NOT EXISTS idx_food_nutrient_bases_basis_unit_id
    ON food_nutrient_bases(basis_unit_id);

CREATE INDEX IF NOT EXISTS idx_food_nutrients_nutrient_type_id
    ON food_nutrients(nutrient_type_id);

CREATE INDEX IF NOT EXISTS idx_daily_nutrition_goals_source_id
    ON daily_nutrition_goals(source_id);

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

CREATE INDEX IF NOT EXISTS idx_inventory_food_id
    ON inventory(food_id);

CREATE INDEX IF NOT EXISTS idx_inventory_updated_at
    ON inventory(updated_at);

CREATE UNIQUE INDEX IF NOT EXISTS idx_inventory_food_unit
    ON inventory(food_id, unit_id)
    WHERE food_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_inventory_manual_description_unit
    ON inventory(description, unit_id)
    WHERE food_id IS NULL;

CREATE INDEX IF NOT EXISTS idx_consumptions_occurred_on
    ON consumptions(occurred_on);

CREATE INDEX IF NOT EXISTS idx_consumptions_food_occurred_on
    ON consumptions(food_id, occurred_on);

CREATE INDEX IF NOT EXISTS idx_consumptions_recipe_occurred_on
    ON consumptions(recipe_id, occurred_on);

CREATE INDEX IF NOT EXISTS idx_consumptions_unit_id
    ON consumptions(unit_id);

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

CREATE INDEX IF NOT EXISTS idx_purchases_bill_id
    ON purchases(bill_id);

CREATE INDEX IF NOT EXISTS idx_grocery_bills_store_purchased_at
    ON grocery_bills(store_id, purchased_at);