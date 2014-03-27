CREATE TABLE search_term
    (id INTEGER PRIMARY KEY,
        term TEXT UNIQUE NOT NULL,
        female BOOL DEFAULT NULL,
        chamber CHAR DEFAULT NULL,
        winner BOOL DEFAULT NULL);
CREATE TABLE person
    (id INTEGER PRIMARY KEY,
        linkedin_id TEXT NOT NULL UNIQUE,
        first_name TEXT,
        last_name TEXT);
CREATE TABLE education
    (id INTEGER PRIMARY KEY,
        linkedin_id INTEGER NOT NULL UNIQUE,
        person_id INTEGER NOT NULL,
        degree TEXT,
        end_date TEXT,
        field_of_study TEXT,
        school_name TEXT);
CREATE TABLE position
    (id INTEGER PRIMARY KEY,
        linkedin_id INTEGER NOT NULL UNIQUE,
        person_id INTEGER NOT NULL,
        is_current INTEGER,
        industry TEXT,
        company_name TEXT,
        title TEXT,
        start_date DATE,
        end_date DATE);

CREATE TABLE search_term_person
    (search_term_id INTEGER NOT NULL, person_id INTEGER NOT NULL);
CREATE UNIQUE INDEX search_term_person_idx
    ON search_term_person (search_term_id, person_id);

