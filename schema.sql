CREATE TABLE IF NOT EXISTS route (
    id INTEGER PRIMARY KEY,
    type TEXT,
    name TEXT NOT NULL,
    start_stop_id INTEGER NOT NULL,
    end_stop_id INTEGER NOT NULL,
    loop INTEGER NOT NULL,
    inverse_id INTEGER NOT NULL,
    company  TEXT,
    distance REAL NOT NULL,
    basic_price REAL NOT NULL,
    total_price REAL NOT NULL,
    polyline TEXT NOT NULL,
    FOREIGN KEY (start_stop_id) REFERENCES stop(id),
    FOREIGN KEY (end_stop_id) REFERENCES stop(id),
    FOREIGN KEY (inverse_id) REFERENCES route(id)
);
CREATE TABLE IF NOT EXISTS stop (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    lng REAL NOT NULL,
    lat REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS route_stop (
    route_id INTEGER NOT NULL,
    stop_seq INTEGER NOT NULL,
    stop_id  INTEGER NOT NULL,
    PRIMARY KEY (route_id, stop_seq),
    FOREIGN KEY (route_id) REFERENCES route(id),
    FOREIGN KEY (stop_id) REFERENCES stop(id)
);