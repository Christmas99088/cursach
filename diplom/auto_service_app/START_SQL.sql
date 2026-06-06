-- ============================================================
-- ПОЛНЫЙ SQL СКРИПТ ДЛЯ СОЗДАНИЯ БАЗЫ ДАННЫХ АВТОСЕРВИСА
-- С ТЕСТОВЫМИ ДАННЫМИ (исправлен для ONLY_FULL_GROUP_BY и ошибки 1137)
-- Версия: 2.5
-- ============================================================

-- Удаляем базу, если она существует (ОСТОРОЖНО! Все данные будут удалены)
DROP DATABASE IF EXISTS auto_service_db;

-- Создаём базу данных с кодировкой UTF-8
CREATE DATABASE auto_service_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE auto_service_db;

-- Отключаем режим ONLY_FULL_GROUP_BY для этой сессии, чтобы избежать ошибок
SET SESSION sql_mode = '';

-- ============================================================
-- 1. СОЗДАНИЕ ТАБЛИЦ (структура)
-- ============================================================

-- 1.1 Пользователи (система авторизации)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'manager', 'master', 'cashier') NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1.2 Клиенты
CREATE TABLE clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1.3 Услуги
CREATE TABLE services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10,2),
    duration INT COMMENT 'Длительность в минутах',
    category VARCHAR(100)
);

-- 1.4 Права доступа
CREATE TABLE permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role VARCHAR(20) NOT NULL,
    permission VARCHAR(100) NOT NULL,
    UNIQUE KEY unique_role_permission (role, permission)
);

-- 1.5 Автомобили клиентов
CREATE TABLE client_cars (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    brand VARCHAR(50),
    model VARCHAR(50),
    year INT,
    license_plate VARCHAR(20),
    vin VARCHAR(50),
    color VARCHAR(30),
    engine_type VARCHAR(50),
    transmission VARCHAR(30),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
);

-- 1.6 Заказы
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT,
    service_id INT,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'В работе',
    total_amount DECIMAL(10,2),
    notes TEXT,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE SET NULL
);

-- 1.7 Финансовые транзакции
CREATE TABLE financial_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_date DATE NOT NULL,
    transaction_type ENUM('income', 'expense') NOT NULL,
    category VARCHAR(100),
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'cash',
    description TEXT,
    client_id INT,
    order_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL
);

-- 1.8 История обслуживания автомобилей
CREATE TABLE service_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    car_id INT NOT NULL,
    order_id INT NULL,
    service_date DATE NOT NULL,
    service_type VARCHAR(100),
    mileage INT,
    next_mileage INT DEFAULT NULL,
    next_service_date DATE DEFAULT NULL,
    parts_used TEXT,
    cost DECIMAL(10,2),
    master_name VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (car_id) REFERENCES client_cars(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL
);

-- 1.9 Напоминания о сервисе
CREATE TABLE service_reminders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    car_id INT NOT NULL,
    reminder_type VARCHAR(50),
    reminder_date DATE,
    mileage_target INT,
    is_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (car_id) REFERENCES client_cars(id) ON DELETE CASCADE
);

-- 1.10 Записи клиентов (appointments)
CREATE TABLE appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    car_id INT,
    service_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    master_name VARCHAR(100),
    status ENUM('pending', 'confirmed', 'completed', 'cancelled') DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
    FOREIGN KEY (car_id) REFERENCES client_cars(id) ON DELETE SET NULL,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
);

-- 1.11 Смены
CREATE TABLE shifts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    username VARCHAR(50),
    full_name VARCHAR(100),
    role VARCHAR(20),
    shift_start DATETIME NOT NULL,
    shift_end DATETIME,
    duration_minutes INT,
    status ENUM('active', 'closed') DEFAULT 'active',
    note TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 1.12 Активная смена
CREATE TABLE active_shift (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    shift_id INT,
    start_time DATETIME NOT NULL,
    note TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (shift_id) REFERENCES shifts(id) ON DELETE SET NULL
);

-- 1.13 Сессии пользователей
CREATE TABLE user_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_token VARCHAR(255) NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 1.14 Аудит действий (лог)
CREATE TABLE audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    username VARCHAR(50),
    user_role VARCHAR(20),
    action_type VARCHAR(50),
    entity_type VARCHAR(50),
    entity_id INT,
    details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 1.15 Действия пользователей (детальный аудит)
CREATE TABLE user_actions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action_type VARCHAR(50),
    entity_type VARCHAR(50),
    entity_id INT,
    details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================================
-- 2. ИНДЕКСЫ ДЛЯ ОПТИМИЗАЦИИ
-- ============================================================

CREATE INDEX idx_orders_client_id ON orders(client_id);
CREATE INDEX idx_orders_service_id ON orders(service_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_order_date ON orders(order_date);
CREATE INDEX idx_clients_phone ON clients(phone);
CREATE INDEX idx_clients_name ON clients(last_name, first_name);
CREATE INDEX idx_client_cars_client_id ON client_cars(client_id);
CREATE INDEX idx_client_cars_license_plate ON client_cars(license_plate);
CREATE INDEX idx_service_history_car_id ON service_history(car_id);
CREATE INDEX idx_service_history_service_date ON service_history(service_date);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_appointments_master ON appointments(master_name);
CREATE INDEX idx_financial_date ON financial_transactions(transaction_date);
CREATE INDEX idx_financial_type ON financial_transactions(transaction_type);
CREATE INDEX idx_shifts_user_id ON shifts(user_id);
CREATE INDEX idx_shifts_status ON shifts(status);
CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_action ON audit_log(action_type);
CREATE INDEX idx_audit_log_created ON audit_log(created_at);

-- ============================================================
-- 3. ВСПОМОГАТЕЛЬНЫЕ ТАБЛИЦЫ ДЛЯ ГЕНЕРАЦИИ ДАННЫХ (обычные, не временные)
-- ============================================================

DROP TABLE IF EXISTS numbers;
CREATE TABLE numbers (n INT PRIMARY KEY);
INSERT INTO numbers VALUES
(1),(2),(3),(4),(5),(6),(7),(8),(9),(10),
(11),(12),(13),(14),(15),(16),(17),(18),(19),(20),
(21),(22),(23),(24),(25),(26),(27),(28),(29),(30),
(31),(32),(33),(34),(35),(36),(37),(38),(39),(40),
(41),(42),(43),(44),(45),(46),(47),(48),(49),(50),
(51),(52),(53),(54),(55),(56),(57),(58),(59),(60),
(61),(62),(63),(64),(65),(66),(67),(68),(69),(70);

DROP TABLE IF EXISTS car_models;
CREATE TABLE car_models (
    brand VARCHAR(50),
    model VARCHAR(50)
);

INSERT INTO car_models (brand, model) VALUES
('Toyota', 'Camry'), ('Toyota', 'Corolla'), ('Toyota', 'RAV4'), ('Toyota', 'Land Cruiser'), ('Toyota', 'Prius'),
('Hyundai', 'Solaris'), ('Hyundai', 'Creta'), ('Hyundai', 'Santa Fe'), ('Hyundai', 'Tucson'), ('Hyundai', 'Elantra'),
('Kia', 'Rio'), ('Kia', 'Sportage'), ('Kia', 'Cerato'), ('Kia', 'Sorento'), ('Kia', 'Optima'),
('Renault', 'Logan'), ('Renault', 'Sandero'), ('Renault', 'Duster'), ('Renault', 'Kaptur'), ('Renault', 'Megane'),
('Volkswagen', 'Polo'), ('Volkswagen', 'Golf'), ('Volkswagen', 'Passat'), ('Volkswagen', 'Tiguan'), ('Volkswagen', 'Jetta'),
('Skoda', 'Octavia'), ('Skoda', 'Rapid'), ('Skoda', 'Kodiaq'), ('Skoda', 'Fabia'), ('Skoda', 'Superb'),
('Ford', 'Focus'), ('Ford', 'Mondeo'), ('Ford', 'Fusion'), ('Ford', 'Kuga'), ('Ford', 'Explorer'),
('Nissan', 'Almera'), ('Nissan', 'Qashqai'), ('Nissan', 'X-Trail'), ('Nissan', 'Juke'), ('Nissan', 'Teana'),
('BMW', '3 Series'), ('BMW', '5 Series'), ('BMW', 'X3'), ('BMW', 'X5'), ('BMW', '1 Series'),
('Mercedes-Benz', 'E-Class'), ('Mercedes-Benz', 'C-Class'), ('Mercedes-Benz', 'GLC'), ('Mercedes-Benz', 'S-Class'), ('Mercedes-Benz', 'GLE'),
('Audi', 'A4'), ('Audi', 'A6'), ('Audi', 'Q5'), ('Audi', 'Q7'), ('Audi', 'A3'),
('Mazda', '6'), ('Mazda', 'CX-5'), ('Mitsubishi', 'Outlander'), ('Subaru', 'Forester'), ('Lexus', 'RX'),
('Honda', 'CR-V'), ('Chevrolet', 'Cruze'), ('Geely', 'Atlas'), ('Chery', 'Tiggo'), ('Lada', 'Vesta');

-- ============================================================
-- 4. ЗАПОЛНЕНИЕ ТАБЛИЦ ТЕСТОВЫМИ ДАННЫМИ
-- ============================================================

-- 4.1 Пользователи (пароли захешированы SHA256)
INSERT INTO users (username, password_hash, role, full_name, email, phone, is_active) VALUES
('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin', 'Администратор Системы', 'admin@auto.ru', '+7 999 111-22-33', TRUE),
('manager', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'manager', 'Иван Петров', 'manager@auto.ru', '+7 999 222-33-44', TRUE),
('master1', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'master', 'Сергей Иванов', 'sergey@auto.ru', '+7 999 333-44-55', TRUE),
('master2', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'master', 'Алексей Смирнов', 'alexey@auto.ru', '+7 999 444-55-66', TRUE),
('cashier', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'cashier', 'Елена Кузнецова', 'elena@auto.ru', '+7 999 555-66-77', TRUE);

-- 4.2 Права доступа
INSERT INTO permissions (role, permission) VALUES
('admin', 'view_clients'), ('admin', 'edit_clients'), ('admin', 'delete_clients'),
('admin', 'view_services'), ('admin', 'edit_services'), ('admin', 'delete_services'),
('admin', 'view_orders'), ('admin', 'edit_orders'), ('admin', 'delete_orders'),
('admin', 'view_finance'), ('admin', 'edit_finance'),
('admin', 'view_reports'), ('admin', 'export_reports'),
('admin', 'manage_users'), ('admin', 'view_logs'),
('manager', 'view_clients'), ('manager', 'edit_clients'),
('manager', 'view_services'), ('manager', 'edit_services'),
('manager', 'view_orders'), ('manager', 'edit_orders'),
('manager', 'view_finance'), ('manager', 'view_reports'),
('manager', 'export_reports'),
('master', 'view_clients'), ('master', 'view_services'),
('master', 'view_orders'), ('master', 'edit_orders'),
('cashier', 'view_clients'), ('cashier', 'view_orders'),
('cashier', 'view_finance'), ('cashier', 'edit_finance');

-- 4.3 Клиенты (20 штук)
INSERT INTO clients (first_name, last_name, phone, email, address) VALUES
('Александр', 'Иванов', '+7 999 123-45-67', 'alex.ivanov@mail.ru', 'г. Москва, ул. Ленина, 10'),
('Дмитрий', 'Петров', '+7 999 234-56-78', 'dmitry.petrov@yandex.ru', 'г. Санкт-Петербург, пр. Невский, 25'),
('Максим', 'Сидоров', '+7 999 345-67-89', 'max.sidorov@gmail.com', 'г. Новосибирск, ул. Советская, 5'),
('Сергей', 'Смирнов', '+7 999 456-78-90', 'sergey.smirnov@bk.ru', 'г. Екатеринбург, ул. Мира, 15'),
('Андрей', 'Кузнецов', '+7 999 567-89-01', 'andrey.kuznetsov@mail.ru', 'г. Казань, ул. Гагарина, 8'),
('Алексей', 'Попов', '+7 999 678-90-12', 'alexey.popov@yandex.ru', 'г. Нижний Новгород, ул. Пушкина, 12'),
('Иван', 'Васильев', '+7 999 789-01-23', 'ivan.vasiliev@mail.ru', 'г. Челябинск, ул. Центральная, 20'),
('Михаил', 'Соколов', '+7 999 890-12-34', 'mikhail.sokolov@gmail.com', 'г. Самара, ул. Молодежная, 3'),
('Евгений', 'Михайлов', '+7 999 901-23-45', 'evgeny.mikhailov@bk.ru', 'г. Омск, ул. Строителей, 7'),
('Владимир', 'Новиков', '+7 999 012-34-56', 'vladimir.novikov@mail.ru', 'г. Ростов-на-Дону, ул. Заводская, 14'),
('Николай', 'Федоров', '+7 999 123-34-56', 'nikolay.fedorov@yandex.ru', 'г. Уфа, ул. Ленина, 22'),
('Павел', 'Морозов', '+7 999 234-45-67', 'pavel.morozov@gmail.com', 'г. Красноярск, ул. Мира, 9'),
('Роман', 'Волков', '+7 999 345-56-78', 'roman.volkov@bk.ru', 'г. Пермь, ул. Гагарина, 16'),
('Артем', 'Алексеев', '+7 999 456-67-89', 'artem.alekseev@mail.ru', 'г. Воронеж, ул. Пушкина, 30'),
('Даниил', 'Лебедев', '+7 999 567-78-90', 'daniil.lebedev@yandex.ru', 'г. Волгоград, ул. Центральная, 11'),
('Елена', 'Козлова', '+7 999 678-89-01', 'elena.kozlova@gmail.com', 'г. Краснодар, ул. Молодежная, 4'),
('Ольга', 'Егорова', '+7 999 789-90-12', 'olga.egorova@bk.ru', 'г. Саратов, ул. Строителей, 18'),
('Мария', 'Павлова', '+7 999 890-01-23', 'maria.pavlova@mail.ru', 'г. Тюмень, ул. Заводская, 6'),
('Анна', 'Семенова', '+7 999 901-12-34', 'anna.semenova@yandex.ru', 'г. Ижевск, ул. Ленина, 13'),
('Татьяна', 'Голубева', '+7 999 012-23-45', 'tatiana.golubeva@gmail.com', 'г. Барнаул, ул. Мира, 21');

-- 4.4 Услуги (30 видов)
INSERT INTO services (name, description, price, duration, category) VALUES
('Замена масла (двигатель)', 'Замена моторного масла и масляного фильтра', 2500, 45, 'Техобслуживание'),
('Замена масла (АКПП)', 'Замена масла в автоматической коробке передач', 4500, 90, 'Техобслуживание'),
('Замена масла (МКПП)', 'Замена масла в механической коробке передач', 3500, 60, 'Техобслуживание'),
('Замена воздушного фильтра', 'Замена воздушного фильтра двигателя', 800, 15, 'Техобслуживание'),
('Замена салонного фильтра', 'Замена салонного фильтра', 600, 10, 'Техобслуживание'),
('Замена топливного фильтра', 'Замена топливного фильтра', 1200, 30, 'Техобслуживание'),
('Комплексное ТО', 'Полное техническое обслуживание автомобиля', 12000, 240, 'Техобслуживание'),
('Замена тормозных колодок передних', 'Замена передних тормозных колодок', 3500, 60, 'Тормозная система'),
('Замена тормозных колодок задних', 'Замена задних тормозных колодок', 3200, 60, 'Тормозная система'),
('Замена тормозных дисков', 'Замена тормозных дисков', 6000, 90, 'Тормозная система'),
('Замена тормозной жидкости', 'Замена тормозной жидкости', 1800, 45, 'Тормозная система'),
('Замена ремня ГРМ', 'Замена ремня ГРМ с роликами', 8500, 180, 'Двигатель'),
('Замена ремня генератора', 'Замена ремня генератора', 2500, 45, 'Двигатель'),
('Замена свечей зажигания', 'Замена комплекта свечей зажигания', 1800, 30, 'Двигатель'),
('Чистка инжектора', 'Ультразвуковая чистка форсунок', 4000, 90, 'Двигатель'),
('Замена антифриза', 'Замена охлаждающей жидкости', 2500, 60, 'Двигатель'),
('Диагностика двигателя', 'Компьютерная диагностика двигателя', 2000, 45, 'Диагностика'),
('Диагностика подвески', 'Полная диагностика ходовой части', 1500, 45, 'Диагностика'),
('Диагностика электроники', 'Диагностика электронных систем автомобиля', 2500, 60, 'Диагностика'),
('Развал-схождение', 'Регулировка углов установки колес', 3500, 90, 'Подвеска'),
('Замена амортизаторов', 'Замена передних/задних амортизаторов', 7500, 150, 'Подвеска'),
('Замена шаровых опор', 'Замена шаровых опор', 4000, 90, 'Подвеска'),
('Замена рулевых наконечников', 'Замена рулевых наконечников', 3500, 90, 'Рулевое'),
('Замена аккумулятора', 'Замена автомобильного аккумулятора', 1500, 20, 'Электрика'),
('Замена генератора', 'Замена генератора', 5500, 120, 'Электрика'),
('Замена стартера', 'Замена стартера', 5000, 90, 'Электрика'),
('Ремонт кондиционера', 'Ремонт системы кондиционирования', 5000, 120, 'Климат'),
('Заправка кондиционера', 'Заправка кондиционера фреоном', 3000, 45, 'Климат'),
('Балансировка колес', 'Балансировка 4 колес', 2000, 45, 'Шиномонтаж'),
('Шиномонтаж (комплект)', 'Сезонная смена шин', 4000, 90, 'Шиномонтаж');

-- 4.5 Автомобили для каждого клиента (по 1-2 авто)
INSERT INTO client_cars (client_id, brand, model, year, license_plate, vin, color)
SELECT
    c.id,
    (SELECT brand FROM car_models ORDER BY RAND() LIMIT 1) AS brand,
    (SELECT model FROM car_models ORDER BY RAND() LIMIT 1) AS model,
    2008 + FLOOR(RAND() * 17) AS year,
    CONCAT(
        ELT(1 + FLOOR(RAND() * 12), 'А','В','Е','К','М','Н','О','Р','С','Т','У','Х'),
        FLOOR(100 + RAND() * 900),
        ELT(1 + FLOOR(RAND() * 12), 'А','В','Е','К','М','Н','О','Р','С','Т','У','Х'),
        ELT(1 + FLOOR(RAND() * 12), 'А','В','Е','К','М','Н','О','Р','С','Т','У','Х'),
        FLOOR(10 + RAND() * 90)
    ) AS license_plate,
    UPPER(CONCAT(
        CHAR(65 + FLOOR(RAND() * 26)),
        CHAR(65 + FLOOR(RAND() * 26)),
        FLOOR(RAND() * 10),
        CHAR(65 + FLOOR(RAND() * 26)),
        FLOOR(RAND() * 10),
        FLOOR(RAND() * 10),
        CHAR(65 + FLOOR(RAND() * 26)),
        FLOOR(RAND() * 10)
    )) AS vin,
    ELT(1 + FLOOR(RAND() * 8), 'Белый','Черный','Серебристый','Синий','Красный','Серый','Зеленый','Коричневый') AS color
FROM clients c
CROSS JOIN (SELECT 1 AS num UNION SELECT 2) nums
WHERE nums.num <= 1 + FLOOR(RAND() * 2)
ORDER BY c.id, nums.num;

-- 4.6 Заказы (70 заказов)
INSERT INTO orders (client_id, service_id, order_date, status, total_amount, notes)
SELECT
    c.id AS client_id,
    s.id AS service_id,
    DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 365) DAY) AS order_date,
    ELT(1 + FLOOR(RAND() * 4), 'Завершено', 'В работе', 'Новый', 'Отменено') AS status,
    s.price AS total_amount,
    ELT(1 + FLOOR(RAND() * 5), '', 'Предварительная запись', 'Срочный ремонт', 'Плановое ТО', 'Диагностика') AS notes
FROM numbers n
CROSS JOIN clients c
CROSS JOIN services s
WHERE n.n <= 70
GROUP BY n.n, c.id, s.id;

-- 4.7 Финансовые транзакции (доходы от завершённых заказов + расходы)
-- Доходы от завершённых заказов
INSERT INTO financial_transactions (transaction_date, transaction_type, category, amount, client_id, order_id, description)
SELECT
    DATE(o.order_date) AS transaction_date,
    'income' AS transaction_type,
    'Ремонт автомобилей' AS category,
    o.total_amount AS amount,
    o.client_id,
    o.id,
    CONCAT('Оплата заказа #', o.id) AS description
FROM orders o
WHERE o.status = 'Завершено';

-- Расходы (различные категории) – 40 операций
INSERT INTO financial_transactions (transaction_date, transaction_type, category, amount, description)
SELECT
    DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 365) DAY) AS transaction_date,
    'expense' AS transaction_type,
    ELT(1 + FLOOR(RAND() * 8), 'Запчасти','Расходные материалы','Аренда помещения','Зарплата сотрудников','Коммунальные услуги','Реклама','Инструмент','Утилизация') AS category,
    CASE FLOOR(1 + RAND() * 8)
        WHEN 1 THEN 500 + FLOOR(RAND() * 50000)
        WHEN 2 THEN 1000 + FLOOR(RAND() * 15000)
        WHEN 3 THEN 30000 + FLOOR(RAND() * 30000)
        WHEN 4 THEN 80000 + FLOOR(RAND() * 70000)
        WHEN 5 THEN 5000 + FLOOR(RAND() * 10000)
        WHEN 6 THEN 5000 + FLOOR(RAND() * 25000)
        WHEN 7 THEN 10000 + FLOOR(RAND() * 40000)
        ELSE 2000 + FLOOR(RAND() * 6000)
    END AS amount,
    CONCAT(ELT(1 + FLOOR(RAND() * 4), 'Закупка', 'Оплата', 'Счёт №', 'Аванс'), ' ', FLOOR(100 + RAND() * 900)) AS description
FROM numbers n
WHERE n.n <= 40;

-- 4.8 История обслуживания (для каждого автомобиля от 2 до 5 записей)
INSERT INTO service_history (car_id, order_id, service_date, service_type, mileage, next_mileage, cost, master_name, notes)
SELECT
    c.id AS car_id,
    o.id AS order_id,
    COALESCE(o.order_date, DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 730) DAY)) AS service_date,
    s.name AS service_type,
    FLOOR(10000 + RAND() * 140000) AS mileage,
    FLOOR(10000 + RAND() * 140000) + FLOOR(5000 + RAND() * 15000) AS next_mileage,
    s.price AS cost,
    ELT(1 + FLOOR(RAND() * 4), 'Сергей Иванов', 'Алексей Смирнов', 'Дмитрий Козлов', 'Иван Петров') AS master_name,
    ELT(1 + FLOOR(RAND() * 5), '', 'Замена по регламенту', 'По рекомендации', 'Срочная замена', 'Плановое ТО') AS notes
FROM client_cars c
CROSS JOIN services s
LEFT JOIN orders o ON o.client_id = c.client_id AND o.service_id = s.id
CROSS JOIN (SELECT 1 AS n UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) mult
WHERE RAND() < 0.2
LIMIT 150;

-- 4.9 Записи клиентов (appointments) на ближайшие 60 дней
INSERT INTO appointments (client_id, car_id, service_id, appointment_date, appointment_time, master_name, status, notes)
SELECT
    c.id AS client_id,
    car.id AS car_id,
    s.id AS service_id,
    DATE_ADD(CURDATE(), INTERVAL FLOOR(RAND() * 60) DAY) AS appointment_date,
    SEC_TO_TIME(FLOOR(9 + RAND() * 8) * 3600) AS appointment_time,
    ELT(1 + FLOOR(RAND() * 3), 'Сергей Иванов', 'Алексей Смирнов', 'Дмитрий Козлов') AS master_name,
    ELT(1 + FLOOR(RAND() * 4), 'pending', 'confirmed', 'completed', 'cancelled') AS status,
    ELT(1 + FLOOR(RAND() * 4), '', 'Просьба позвонить перед выездом', 'Нужна диагностика', 'Срочно') AS notes
FROM numbers n
CROSS JOIN clients c
CROSS JOIN client_cars car ON car.client_id = c.id
CROSS JOIN services s
WHERE n.n <= 50
GROUP BY n.n, c.id, car.id, s.id
LIMIT 50;

-- 4.10 Смены для мастеров (за последние 30 дней)
INSERT INTO shifts (user_id, username, full_name, role, shift_start, shift_end, duration_minutes, status)
SELECT
    u.id,
    u.username,
    u.full_name,
    u.role,
    DATE_SUB(NOW(), INTERVAL (day_num * 24 + FLOOR(RAND() * 8)) HOUR) AS shift_start,
    DATE_SUB(NOW(), INTERVAL (day_num * 24 + FLOOR(RAND() * 8) - (4 + FLOOR(RAND() * 6))) HOUR) AS shift_end,
    60 * (4 + FLOOR(RAND() * 6)) AS duration_minutes,
    'closed' AS status
FROM users u
CROSS JOIN (SELECT 1 AS day_num UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
            UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10
            UNION SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14 UNION SELECT 15
            UNION SELECT 16 UNION SELECT 17 UNION SELECT 18 UNION SELECT 19 UNION SELECT 20) days
WHERE u.role = 'master'
  AND DATE_SUB(NOW(), INTERVAL (day_num * 24 + FLOOR(RAND() * 8) - (4 + FLOOR(RAND() * 6))) HOUR) > DATE_SUB(NOW(), INTERVAL (day_num * 24 + FLOOR(RAND() * 8)) HOUR)
LIMIT 40;

-- 4.11 Несколько записей в audit_log (для демонстрации)
INSERT INTO audit_log (user_id, username, user_role, action_type, entity_type, entity_id, details, created_at)
SELECT
    u.id,
    u.username,
    u.role,
    ELT(1 + FLOOR(RAND() * 5), 'LOGIN_SUCCESS', 'CREATE', 'UPDATE', 'DELETE', 'STATUS_CHANGE') AS action_type,
    ELT(1 + FLOOR(RAND() * 4), 'order', 'client', 'service', 'appointment') AS entity_type,
    FLOOR(1 + RAND() * 100) AS entity_id,
    CONCAT('Действие пользователя ', u.username) AS details,
    DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 30) DAY) AS created_at
FROM users u
CROSS JOIN (SELECT 1 AS n UNION SELECT 2 UNION SELECT 3) nums
LIMIT 50;

-- ============================================================
-- 5. ОЧИСТКА ВСПОМОГАТЕЛЬНЫХ ТАБЛИЦ
-- ============================================================
DROP TABLE IF EXISTS numbers;
DROP TABLE IF EXISTS car_models;

-- ============================================================
-- 6. ИТОГОВАЯ ИНФОРМАЦИЯ
-- ============================================================
SELECT '✅ База данных успешно создана и заполнена тестовыми данными!' AS Status;
SELECT COUNT(*) AS clients_count FROM clients;
SELECT COUNT(*) AS services_count FROM services;
SELECT COUNT(*) AS cars_count FROM client_cars;
SELECT COUNT(*) AS orders_count FROM orders;
SELECT COUNT(*) AS financial_transactions_count FROM financial_transactions;
SELECT COUNT(*) AS service_history_count FROM service_history;
SELECT COUNT(*) AS appointments_count FROM appointments;
SELECT COUNT(*) AS shifts_count FROM shifts;

-- Вывод информации для входа
SELECT '🔐 Данные для входа:' AS Info;
SELECT 'admin / admin123' AS AdminLogin;
SELECT 'manager / manager123' AS ManagerLogin;
SELECT 'master1 / master123' AS MasterLogin;
SELECT 'cashier / cashier123' AS CashierLogin;