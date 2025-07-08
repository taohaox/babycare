-- 宝宝成长记录系统数据库迁移脚本
-- 执行前请备份现有数据库

-- 1. 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 修改宝宝表，添加用户ID外键
-- 如果宝宝表已存在，先备份数据
CREATE TABLE IF NOT EXISTS babies_backup AS SELECT * FROM babies;

-- 删除现有宝宝表（如果存在）
DROP TABLE IF EXISTS babies;

-- 重新创建宝宝表，添加user_id字段
CREATE TABLE babies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    birth_date DATE NOT NULL,
    birth_time TIME,
    gender VARCHAR(10) NOT NULL,
    photo VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. 修改记录表，添加用户ID外键
-- 如果记录表已存在，先备份数据
CREATE TABLE IF NOT EXISTS baby_records_backup AS SELECT * FROM baby_records;

-- 删除现有记录表（如果存在）
DROP TABLE IF EXISTS baby_records;

-- 重新创建记录表，添加user_id字段
CREATE TABLE baby_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    baby_id INTEGER NOT NULL,
    date DATE NOT NULL,
    height DECIMAL(5,2),
    weight DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (baby_id) REFERENCES babies(id) ON DELETE CASCADE
);

-- 4. 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_babies_user_id ON babies(user_id);
CREATE INDEX IF NOT EXISTS idx_baby_records_user_id ON baby_records(user_id);
CREATE INDEX IF NOT EXISTS idx_baby_records_baby_id ON baby_records(baby_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);



-- 6. 数据迁移说明
-- 注意：如果之前有数据，需要手动迁移数据
-- 1. 为现有宝宝分配用户ID（例如使用演示用户ID）
-- 2. 为现有记录分配用户ID
-- 3. 删除备份表

-- 示例：为现有数据分配用户（如果有数据的话）
-- 注意：需要手动指定用户ID或创建新用户
-- UPDATE babies SET user_id = 1 WHERE user_id IS NULL;
-- UPDATE baby_records SET user_id = 1 WHERE user_id IS NULL;

-- 7. 清理备份表（确认数据迁移成功后执行）
-- DROP TABLE IF EXISTS babies_backup;
-- DROP TABLE IF EXISTS baby_records_backup;

PRAGMA foreign_keys = ON; 