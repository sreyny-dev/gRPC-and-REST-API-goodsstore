-- CREATE TABLE: https://www.postgresql.org/docs/17/ddl-basics.html
-- numeric types and SERIAL: https://www.postgresql.org/docs/current/datatype-numeric.html
-- CHECK (): https://www.postgresql.org/docs/17/ddl-constraints.html#DDL-CONSTRAINTS-CHECK-CONSTRAINTS
-- REFERENCES table_name(column_name) ON DELETE CASCADE: https://www.postgresql.org/docs/17/ddl-constraints.html#DDL-CONSTRAINTS-FK
-- Create the products table
CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  category VARCHAR(50),
  price DECIMAL(10, 2) NOT NULL,
  slogan VARCHAR(255),
  stock INT NOT NULL DEFAULT 500,
  created_at TIMESTAMP DEFAULT NOW()
);
-- Insert initial product data for limited SUSTech goods
INSERT INTO products (
    name,
    description,
    category,
    price,
    slogan,
    stock
  )
VALUES (
    'SUSTech Hoodie',
    'A cozy, stylish hoodie featuring the official SUSTech logo, perfect for showing school spirit.',
    'Apparel',
    49.99,
    'Stay warm, stay proud!',
    500
  ),
  (
    'SUSTech Water Bottle',
    'A high-quality, eco-friendly stainless steel water bottle with SUSTech branding.',
    'Drinkware',
    19.99,
    'Hydrate with pride!',
    500
  ),
  (
    'SUSTech Notebook',
    'A premium notebook with the SUSTech logo, ideal for jotting down ideas, notes, and memories.',
    'Stationery',
    9.99,
    'Write your future with SUSTech.',
    500
  );
-- Create the users table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  sid VARCHAR(15) UNIQUE NOT NULL,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  is_active BOOLEAN DEFAULT TRUE NOT NULL
);

-- Create the orders table
CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id) ON DELETE CASCADE,
  product_id INT REFERENCES products(id) ON DELETE CASCADE,
  quantity INT CHECK (
    quantity > 0
    AND quantity <= 3
  ),
  -- Limit order quantity to max 3 per product
  total_price DECIMAL(10, 2) NOT NULL,
  -- Total price calculated in application logic
  created_at TIMESTAMP DEFAULT NOW()
);
