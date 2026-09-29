DROP DATABASE IF EXISTS tourism_db;
CREATE DATABASE tourism_db;
USE tourism_db;

-- Users table (with role)
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(256) NOT NULL, -- store hashed password (SHA2)
    role ENUM('admin','user') DEFAULT 'user'
);

-- Continents
CREATE TABLE continents (
    continent_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Countries
CREATE TABLE countries (
    country_id INT AUTO_INCREMENT PRIMARY KEY,
    continent_id INT,
    name VARCHAR(100) UNIQUE NOT NULL,
    FOREIGN KEY (continent_id) REFERENCES continents(continent_id) ON DELETE CASCADE
);

-- Destinations with approval workflow
CREATE TABLE destinations (
    dest_id INT AUTO_INCREMENT PRIMARY KEY,
    country_id INT,
    name VARCHAR(150) NOT NULL,
    best_time VARCHAR(100),
    climate VARCHAR(50),
    avg_budget INT,
    description TEXT,
    approved TINYINT(1) DEFAULT 1,        -- 1 = approved / visible, 0 = pending
    created_by INT DEFAULT NULL,          -- user_id who created it (NULL for seeded/admin)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    approved_by INT DEFAULT NULL,
    approved_at DATETIME DEFAULT NULL,
    FOREIGN KEY (country_id) REFERENCES countries(country_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    FOREIGN KEY (approved_by) REFERENCES users(user_id)
);

-- Attractions
CREATE TABLE attractions (
    attr_id INT AUTO_INCREMENT PRIMARY KEY,
    dest_id INT,
    attraction_type VARCHAR(100),
    details VARCHAR(255),
    FOREIGN KEY (dest_id) REFERENCES destinations(dest_id) ON DELETE CASCADE
);

-- To Visit list
CREATE TABLE to_visit (
    list_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    dest_id INT,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (dest_id) REFERENCES destinations(dest_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_dest (user_id, dest_id)
);

-- Seed continents
INSERT INTO continents (name) VALUES
('Asia'), ('Europe'), ('North America'), ('South America'), ('Africa'), ('Oceania');

-- Seed countries (using continent names)
INSERT INTO countries (continent_id, name)
VALUES
((SELECT continent_id FROM continents WHERE name='Asia'), 'India'),
((SELECT continent_id FROM continents WHERE name='Asia'), 'Japan'),
((SELECT continent_id FROM continents WHERE name='Asia'), 'Thailand'),
((SELECT continent_id FROM continents WHERE name='Asia'), 'Nepal'),
((SELECT continent_id FROM continents WHERE name='Asia'), 'China'),
((SELECT continent_id FROM continents WHERE name='Asia'), 'Singapore'),

((SELECT continent_id FROM continents WHERE name='Europe'), 'France'),
((SELECT continent_id FROM continents WHERE name='Europe'), 'Italy'),
((SELECT continent_id FROM continents WHERE name='Europe'), 'Germany'),
((SELECT continent_id FROM continents WHERE name='Europe'), 'Spain'),
((SELECT continent_id FROM continents WHERE name='Europe'), 'Switzerland'),
((SELECT continent_id FROM continents WHERE name='Europe'), 'Greece'),

((SELECT continent_id FROM continents WHERE name='North America'), 'USA'),
((SELECT continent_id FROM continents WHERE name='North America'), 'Canada'),
((SELECT continent_id FROM continents WHERE name='North America'), 'Mexico'),
((SELECT continent_id FROM continents WHERE name='North America'), 'Cuba'),

((SELECT continent_id FROM continents WHERE name='South America'), 'Brazil'),
((SELECT continent_id FROM continents WHERE name='South America'), 'Argentina'),
((SELECT continent_id FROM continents WHERE name='South America'), 'Peru'),

((SELECT continent_id FROM continents WHERE name='Africa'), 'South Africa'),
((SELECT continent_id FROM continents WHERE name='Africa'), 'Egypt'),
((SELECT continent_id FROM continents WHERE name='Africa'), 'Kenya'),

((SELECT continent_id FROM continents WHERE name='Oceania'), 'Australia'),
((SELECT continent_id FROM continents WHERE name='Oceania'), 'New Zealand');

-- Large set of sample destinations (50+). Many reference countries by subquery (name).
-- Asia (India, Japan, Thailand, Nepal, China, Singapore)
INSERT INTO destinations (country_id, name, best_time, climate, avg_budget, description)
VALUES
((SELECT country_id FROM countries WHERE name='India'), 'Taj Mahal (Agra)', 'Oct-Mar', 'Tropical', 500, 'Iconic mausoleum in Agra.'),
((SELECT country_id FROM countries WHERE name='India'), 'Goa', 'Nov-Feb', 'Tropical', 2000, 'Beaches and nightlife.'),
((SELECT country_id FROM countries WHERE name='India'), 'Manali', 'Apr-Jun', 'Cold', 2500, 'Hill station with snow and adventure.'),
((SELECT country_id FROM countries WHERE name='India'), 'Kerala Backwaters (Alleppey)', 'Sep-Mar', 'Tropical', 3000, 'Houseboats and tranquil backwaters.'),
((SELECT country_id FROM countries WHERE name='Japan'), 'Tokyo', 'Mar-May', 'Temperate', 1500, 'Modern city, temples, food.'),
((SELECT country_id FROM countries WHERE name='Japan'), 'Kyoto', 'Mar-May', 'Temperate', 1400, 'Historic temples and cherry blossoms.'),
((SELECT country_id FROM countries WHERE name='Thailand'), 'Bangkok', 'Nov-Feb', 'Tropical', 1200, 'Temples, markets, street food.'),
((SELECT country_id FROM countries WHERE name='Thailand'), 'Phuket', 'Nov-Feb', 'Tropical', 1300, 'Beaches and islands.'),
((SELECT country_id FROM countries WHERE name='Nepal'), 'Kathmandu', 'Sep-Nov', 'Cold', 800, 'Gateway to Himalayas and cultural sites.'),
((SELECT country_id FROM countries WHERE name='Nepal'), 'Pokhara', 'Mar-May', 'Cold', 900, 'Lakeside city, Annapurna views.'),
((SELECT country_id FROM countries WHERE name='China'), 'Beijing', 'Apr-May', 'Temperate', 1100, 'Great Wall and Forbidden City.'),
((SELECT country_id FROM countries WHERE name='China'), 'Shanghai', 'Sep-Nov', 'Temperate', 1200, 'Modern skyline and The Bund.'),
((SELECT country_id FROM countries WHERE name='Singapore'), 'Singapore City', 'Feb-Apr', 'Tropical', 2000, 'Marina Bay Sands, Gardens by the Bay.');

-- Europe
INSERT INTO destinations (country_id, name, best_time, climate, avg_budget, description)
VALUES
((SELECT country_id FROM countries WHERE name='France'), 'Paris', 'Apr-Jun', 'Temperate', 1800, 'Eiffel Tower and museums.'),
((SELECT country_id FROM countries WHERE name='Italy'), 'Rome', 'Apr-Jun', 'Mediterranean', 1600, 'Ancient ruins and cuisine.'),
((SELECT country_id FROM countries WHERE name='Germany'), 'Berlin', 'May-Sep', 'Temperate', 1300, 'History and nightlife.'),
((SELECT country_id FROM countries WHERE name='Germany'), 'Munich', 'Sep-Oct', 'Temperate', 1400, 'Oktoberfest and architecture.'),
((SELECT country_id FROM countries WHERE name='Spain'), 'Barcelona', 'May-Sep', 'Mediterranean', 1500, 'Sagrada Familia and beaches.'),
((SELECT country_id FROM countries WHERE name='Spain'), 'Madrid', 'Apr-Jun', 'Mediterranean', 1400, 'Royal Palace and museums.'),
((SELECT country_id FROM countries WHERE name='Switzerland'), 'Zurich', 'Jun-Sep', 'Cold', 2000, 'Lakes and Alps.'),
((SELECT country_id FROM countries WHERE name='Switzerland'), 'Interlaken', 'Jun-Sep', 'Cold', 2100, 'Adventure sports and Jungfrau.'),
((SELECT country_id FROM countries WHERE name='Greece'), 'Athens', 'Apr-Jun', 'Mediterranean', 1200, 'Acropolis and ancient sites.'),
((SELECT country_id FROM countries WHERE name='Greece'), 'Santorini', 'May-Sep', 'Mediterranean', 1900, 'Sunset vistas and cliffs.');

-- North America
INSERT INTO destinations (country_id, name, best_time, climate, avg_budget, description)
VALUES
((SELECT country_id FROM countries WHERE name='USA'), 'New York City', 'Sep-Nov', 'Temperate', 2200, 'Skyscrapers and Broadway.'),
((SELECT country_id FROM countries WHERE name='USA'), 'Grand Canyon', 'Mar-May', 'Desert', 900, 'Natural wonder with hiking.'),
((SELECT country_id FROM countries WHERE name='Canada'), 'Toronto', 'Jun-Aug', 'Cold', 1500, 'CN Tower and multicultural city.'),
((SELECT country_id FROM countries WHERE name='Canada'), 'Vancouver', 'Jun-Aug', 'Temperate', 1600, 'Nature meets city, mountains and sea.'),
((SELECT country_id FROM countries WHERE name='Mexico'), 'Cancun', 'Dec-Apr', 'Tropical', 1300, 'Beaches and resorts.'),
((SELECT country_id FROM countries WHERE name='Mexico'), 'Mexico City', 'Mar-May', 'Temperate', 1100, 'Historic center and museums.'),
((SELECT country_id FROM countries WHERE name='Cuba'), 'Havana', 'Dec-Mar', 'Tropical', 1000, 'Old Havana and classic cars.'),
((SELECT country_id FROM countries WHERE name='Cuba'), 'Varadero', 'Dec-Mar', 'Tropical', 1200, 'Beach resort town.');

-- South America
INSERT INTO destinations (country_id, name, best_time, climate, avg_budget, description)
VALUES
((SELECT country_id FROM countries WHERE name='Brazil'), 'Rio de Janeiro', 'Dec-Mar', 'Tropical', 1500, 'Carnival, Copacabana and Christ the Redeemer.'),
((SELECT country_id FROM countries WHERE name='Brazil'), 'Iguazu Falls', 'Mar-May', 'Tropical', 1400, 'Spectacular waterfalls shared with Argentina.'),
((SELECT country_id FROM countries WHERE name='Argentina'), 'Buenos Aires', 'Mar-May', 'Temperate', 1300, 'Tango and vibrant neighborhoods.'),
((SELECT country_id FROM countries WHERE name='Argentina'), 'Patagonia', 'Nov-Feb', 'Cold', 2200, 'Glaciers and dramatic landscapes.'),
((SELECT country_id FROM countries WHERE name='Peru'), 'Machu Picchu', 'Apr-Oct', 'Cold', 1700, 'Iconic Inca citadel.'),
((SELECT country_id FROM countries WHERE name='Peru'), 'Cusco', 'Apr-Oct', 'Cold', 1300, 'Historic capital of Inca Empire.');

-- Africa
INSERT INTO destinations (country_id, name, best_time, climate, avg_budget, description)
VALUES
((SELECT country_id FROM countries WHERE name='South Africa'), 'Cape Town', 'Nov-Mar', 'Mediterranean', 1600, 'Table Mountain and beaches.'),
((SELECT country_id FROM countries WHERE name='South Africa'), 'Kruger National Park', 'May-Sep', 'Tropical', 1800, 'Big Five safaris.'),
((SELECT country_id FROM countries WHERE name='Egypt'), 'Cairo (Pyramids)', 'Oct-Apr', 'Desert', 1200, 'Pyramids of Giza and Egyptian Museum.'),
((SELECT country_id FROM countries WHERE name='Egypt'), 'Luxor', 'Oct-Apr', 'Desert', 1100, 'Valley of the Kings and temples.'),
((SELECT country_id FROM countries WHERE name='Kenya'), 'Nairobi', 'Jun-Sep', 'Tropical', 1400, 'Gateway for safaris.'),
((SELECT country_id FROM countries WHERE name='Kenya'), 'Maasai Mara', 'Jul-Oct', 'Tropical', 2000, 'Great Migration safari.');

-- Oceania
INSERT INTO destinations (country_id, name, best_time, climate, avg_budget, description)
VALUES
((SELECT country_id FROM countries WHERE name='Australia'), 'Sydney Opera House', 'Sep-Nov', 'Temperate', 2000, 'Iconic harbour and opera house.'),
((SELECT country_id FROM countries WHERE name='Australia'), 'Great Barrier Reef', 'Jun-Oct', 'Tropical', 2300, 'World\'s largest coral reef.'),
((SELECT country_id FROM countries WHERE name='Australia'), 'Melbourne', 'Nov-Mar', 'Temperate', 1800, 'Culture and coffee scene.'),
((SELECT country_id FROM countries WHERE name='New Zealand'), 'Queenstown', 'Dec-Feb', 'Temperate', 2100, 'Adventure capital with lakes and mountains.'),
((SELECT country_id FROM countries WHERE name='New Zealand'), 'Milford Sound', 'Oct-Apr', 'Temperate', 2000, 'Dramatic fiords and cruises.');

-- Total inserted: 50+ destinations across many countries and continents.

-- Attractions (sample)
INSERT INTO attractions (dest_id, attraction_type, details)
VALUES
((SELECT dest_id FROM destinations WHERE name LIKE 'Taj Mahal%'), 'Historical', 'The mausoleum and gardens'),
((SELECT dest_id FROM destinations WHERE name='Goa'), 'Beach', 'Baga, Anjuna, Calangute'),
((SELECT dest_id FROM destinations WHERE name='Manali'), 'Adventure', 'Skiing, paragliding, river rafting'),
((SELECT dest_id FROM destinations WHERE name='Tokyo'), 'Modern', 'Skytree, Shinjuku, Akihabara'),
((SELECT dest_id FROM destinations WHERE name='Paris'), 'Historical', 'Eiffel Tower, Louvre'),
((SELECT dest_id FROM destinations WHERE name='New York City'), 'Modern', 'Statue of Liberty, Times Square'),
((SELECT dest_id FROM destinations WHERE name='Machu Picchu'), 'Historical', 'Inca citadel'),
((SELECT dest_id FROM destinations WHERE name='Great Barrier Reef'), 'Nature', 'Diving and snorkeling');

-- Create an admin user (username: admin, password: admin123)
-- We store SHA2(password,256)
INSERT INTO users (username, password, role)
VALUES ('admin', SHA2('admin', 256), 'admin');

-- Sample normal users
INSERT INTO users (username, password, role)
VALUES ('alice', SHA2('aliceinwonderland',256), 'user'), ('bob', SHA2('bobbybob',256), 'user');

-- A few approved_by / created_by are left NULL for seeded records; user-added will set created_by and approved=0.

-- Final: ensure some destinations are marked pending to test approval flow
-- Create two pending destinations (simulate user added)
INSERT INTO destinations (country_id, name, best_time, climate, avg_budget, description, approved, created_by)
VALUES
((SELECT country_id FROM countries WHERE name='India'), 'Zanskar Valley', 'Jun-Aug', 'Cold', 2600, 'Remote valley with trekking', 0, (SELECT user_id FROM users WHERE username='alice')),
((SELECT country_id FROM countries WHERE name='Peru'), 'Choquequirao', 'Apr-Oct', 'Cold', 1500, 'Inca ruins less-visited', 0, (SELECT user_id FROM users WHERE username='bob'));