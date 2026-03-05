CREATE TABLE traffic_stops (
    stop_id SERIAL PRIMARY KEY,
    stop_date DATE,
    stop_time TIME,
    country_name VARCHAR(50),
    driver_gender VARCHAR(10),
    driver_age INT,
    driver_race VARCHAR(50),
    violation VARCHAR(100),
    search_conducted BOOLEAN,
    search_type VARCHAR(100),
    stop_outcome VARCHAR(50),
    is_arrested BOOLEAN,
    stop_duration VARCHAR(20),
    drugs_related_stop BOOLEAN,
    vehicle_number VARCHAR(20)
);