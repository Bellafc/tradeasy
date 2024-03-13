USE Tradeasy_quotation;

CREATE TABLE Tradeasy_quotation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    productName VARCHAR(255),
    productTag VARCHAR(255),
    supplier VARCHAR(255),
    category ENUM('Beef', 'Pork', 'Chicken', 'Poultry', 'Lamb', 'Fish', 'Seafood', 'Shrimp', 'Meatballs', 'Premade', 'Vegetables', 'Retail', 'Others'),
    packing VARCHAR(255),
    origin VARCHAR(255),
    brand VARCHAR(255),
    effectiveDate DATE,
    spec1 VARCHAR(255),
    spec2 VARCHAR(255),
    spec3 VARCHAR(255),
    spec4 VARCHAR(255),
    spec5 VARCHAR(255),
    spec6 VARCHAR(255),
    price DECIMAL(10, 2),
    weightUnit ENUM('KG', 'LB', 'PC', 'CTN'),
    warehouse ENUM('嘉里温控貨倉1', '嘉里温控貨倉2', '沙田冷倉1倉', '沙田冷倉2倉', '其士冷藏倉庫', '光輝1倉', '光輝2倉', '威強凍倉', '亞洲生活冷倉', '嘉威倉', '百匯倉', '萬集倉', '萬安倉', '送貨'),
    notes TEXT
);





