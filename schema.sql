CREATE TABLE search_term (id INTEGER PRIMARY KEY, term TEXT UNIQUE NOT NULL);
CREATE TABLE person
    (id INTEGER PRIMARY KEY,
        linkedin_id TEXT NOT NULL UNIQUE,
        firstName TEXT,
        lastName TEXT);
CREATE TABLE education
    (id INTEGER PRIMARY KEY,
        linkedin_id INTEGER NOT NULL UNIQUE,
        person_id INTEGER NOT NULL,
        degree TEXT,
        endDate TEXT,
        fieldOfStudy TEXT,
        schoolName TEXT);
CREATE TABLE position
    (id INTEGER PRIMARY KEY,
        linkedin_id INTEGER NOT NULL UNIQUE,
        person_id INTEGER NOT NULL,
        is_current INTEGER,
        industry TEXT,
        company_name TEXT,
        title TEXT,
        startDate DATE,
        endDate DATE);

CREATE TABLE search_term_person
    (search_term_id INTEGER NOT NULL, person_id INTEGER NOT NULL);
CREATE UNIQUE INDEX search_term_person_idx
    ON search_term_person (search_term_id, person_id);

