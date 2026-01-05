CREATE TABLE IF NOT EXISTS vendor (
    id          SERIAL PRIMARY KEY,
    name        TEXT        NOT NULL,
    country     TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS shop (
    id      SERIAL PRIMARY KEY,
    name    TEXT NOT NULL,
    address TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS roll (
    id                     SERIAL PRIMARY KEY,
    vendor_id              INTEGER NOT NULL REFERENCES vendor(id),
    collection             TEXT NOT NULL,
    uri                    TEXT NOT NULL,
    height                 DOUBLE PRECISION NOT NULL,
    width                  DOUBLE PRECISION NOT NULL,
    weight                 DOUBLE PRECISION NOT NULL,
    article                TEXT NOT NULL,
    base                   TEXT NOT NULL,
    cover                  TEXT NOT NULL,
    rapor                  TEXT,
    pattern                TEXT,
    moisture_resistance    TEXT,
    production_technology  TEXT,
    light_fastness         TEXT,
    glue_application       TEXT
);

CREATE TABLE IF NOT EXISTS asset (
    roll_id INTEGER NOT NULL REFERENCES roll(id) ON DELETE CASCADE,
    url     TEXT    PRIMARY KEY
);

-- временная таблица
CREATE TABLE IF NOT EXISTS tmp_fact (
    roll_id   INTEGER NOT NULL REFERENCES roll(id),
    shop_id   INTEGER NOT NULL REFERENCES shop(id),
    price     NUMERIC(12,2) NOT NULL,
    available INTEGER NOT NULL,
    PRIMARY KEY (roll_id, shop_id)
);

-- постоянная таблица
CREATE TABLE IF NOT EXISTS fact (
    roll_id   INTEGER NOT NULL REFERENCES roll(id),
    shop_id   INTEGER NOT NULL REFERENCES shop(id),
    price     NUMERIC(12,2) NOT NULL,
    available INTEGER NOT NULL,
    PRIMARY KEY (roll_id, shop_id)
);

-- таблица с разницей
CREATE TABLE IF NOT EXISTS diff (
    roll_id   INTEGER NOT NULL REFERENCES roll(id),
    shop_id   INTEGER NOT NULL REFERENCES shop(id),
    old_price NUMERIC(12,2),  -- если новое может не быть 
    old_count INTEGER,
    new_price NUMERIC(12,2) NOT NULL,
    new_count INTEGER NOT NULL,
    PRIMARY KEY (roll_id, shop_id)
);







-- Записываем справочные данные
-- 1. Магазины
INSERT INTO shop (id, name, address) VALUES
(401, '«Байконурская»', '197349, г. Санкт-Петербург, ул. Байконурская, 14,  лит. А'),
(1897, '«Гранд Каньон»', 'г. Санкт-Петербург, пр. Энгельса, 154А​'),
(1898, '«РИО»', 'г. Санкт-Петербург, ул. Фучика, д.2'),
(6614, '«Колпино»', 'г. Колпино, ул. Октябрьская, д. 8'),
(39758, '«Пулково»', 'г. Санкт-Петербург, Пулковское шоссе д. 17/2'),
(39760, '«Руставели»', 'г. Санкт-Петербург, ул. Руставели д. 43'),
(66877, '«Вилла»', 'г. Санкт-Петербург, ул. Савушкина, 119, корп. 3'),
(88203, '«Большевиков»', 'г. Санкт-Петербург, пр. Большевиков, д. 32/1'),
(88426, '«Мозаика»', '115193 Москва, 7-я Кожуховская ул., 9'),
(107461, '«Ладожская»', 'г. Санкт-Петербург, Заневский проспект, 65, к.1'),
(108045, 'ТРК MARi', '109469, Москва, ул. Поречная, 10'),
(108662, '«Ашан Алтуфьево»', 'посёлок Вешки, торгово-промышленная зона Алтуфьево, вл3с1'),
(141752, 'Victoria Stenova «Твой Дом Крокус Сити»', 'Москва, МКАД, 67-й километр, внешняя сторона, 67'),
(142316, 'Victoria Stenova «Твой Дом Мытищи»', '141031, Мытищи, Московская область, Осташковское шоссе, 2'),
(143716, 'Palitra «Твой Дом Мытищи»', '141031, Мытищи, Московская область, Осташковское шоссе, 2'),
(143717, '«Ашан Мытищи»', '141014, Москва, МКАД, 91-й километр, 1,'),
(143718, '«Петергофское»', 'г. Санкт-Петербург, просп. Будённого, 27, корп. 1'),
(162265, 'Loymina Expostroy', '117218 Москва, Нахимовский просп., 24, стр. 1 павильон 2 вход 1 этаж 1  стенд 18+19'),
(188226, '«Кингисепп»', 'г. Кингисепп, просп. Карла Маркса, 42, ТЦ «Ребус»'),
(169837, 'Victoria Stenova «Миллион Мелочей»', '127560 Москва, улица Пришвина, 26'),
(174390, 'Victoria Stenova «Небо»', 'г. Мурино, Романовская ул., 1/31'),
(185061, 'Хит «Балашиха»', 'Московская область, г. Балашиха, Микрорайон Саввино, ул. Пригородная, д.92'),
(116996, 'Victoria Stenova «Изобильный»', 'Изобильный, ул.Советская, д.82а'),
(180812, 'Victoria Stenova «Старомарьевское»', 'Ставрополь, Старомарьевское шоссе, д. 12А'),
(117869, 'Мир обоев на Кулакова', 'Ставрополь, просп. Кулакова, 10Е'),
(117868, 'Victoria Stenova «Михайловск»', 'Михайловск, ул. Гоголя, д. 207, корп. 1');


-- 2. Производители
INSERT INTO vendor (id, name) VALUES
(7, 'Grandeco'),
(12, 'Victoria Stenova'),
(13, 'Palitra Life'),
(14, 'Palitra Family'),
(15, 'Palitra Home'),
(33, 'Euro Decor'),
(39, 'Артекс'),
(45, 'Элизиум'),
(49, 'P+S '),
(61, 'OVK Design'),
(65, 'Solo'),
(68, 'Monte Solaro'),
(83, 'Erismann'),
(677, 'Palitra Trend'),
(683, 'Ateliero'),
(717, 'Ostima'),
(720, 'Freedom'),
(738, 'Аспект'),
(744, 'Ornamy'),
(756, 'Deco-Deco'),
(760, 'Wall Up'),
(769, 'Wall Decor'),
(772, 'Palitra Simple'),
(777, 'Diamond'),
(779, 'Rose'),
(781, 'Avisto'),
(782, 'WallSecret'),
(785, 'Accento'),
(789, 'Profi Deco'),
(798, 'New Age'),
(799, 'Palitra Style'),
(806, 'Ecoline'),
(865, 'Art&Style');
