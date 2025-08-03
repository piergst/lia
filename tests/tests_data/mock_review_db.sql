CREATE TABLE IF NOT EXISTS review_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    group_index INTEGER NOT NULL,
    topic TEXT NOT NULL, 
    last_review_date DATETIME, 
    next_review_date DATETIME,
    reviews_count INTEGER NOT NULL DEFAULT 0
); 

DELETE FROM review_groups;

INSERT INTO review_groups (group_index, topic, last_review_date, next_review_date, reviews_count) VALUES
(0, 'ad', '2025-01-18', '2025-02-17', 3),
(1, 'ad', '2025-01-23', '2025-02-22', 2),
(2, 'ad', '2025-03-02', '2025-03-09', 1),
(0, 'bash', '2025-01-18', '2025-02-17', 3),
(1, 'bash', '2025-01-23', '2025-02-22', 1),
(2, 'bash', '2025-01-23', '2025-02-22', 2),
(3, 'bash', '2025-02-24', '2025-03-03', 2),
(4, 'bash', '2025-03-02', '2025-03-09', 1),
(5, 'bash', '2025-02-25', '2025-03-27', 2),
(0, 'curl', '2025-02-10', '2025-02-17', 2),
(1, 'curl', '2025-03-02', '2025-03-03', 1),
(2, 'curl', '2025-02-24', '2025-03-03', 2),
(3, 'curl', '2025-02-25', '2025-03-27', 2),
(0, 'python', '2025-02-10', '2025-02-17', 2),
(1, 'python', '2025-01-23', '2025-02-22', 1),
(2, 'python', '2025-03-02', '2025-03-03', 1); 