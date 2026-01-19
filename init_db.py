#!/usr/bin/env python3
"""
Initialize the breakfast decision database with all recipe data.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'breakfast.db')

def create_tables(conn):
    """Create all required tables."""
    cursor = conn.cursor()
    
    # Recipes main table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_name TEXT NOT NULL,
            recipe_name_en TEXT,
            category TEXT,
            difficulty INTEGER,
            cooking_time INTEGER,
            source_article TEXT,
            source_author TEXT,
            source_link TEXT,
            thumbnail_url TEXT,
            publish_date TEXT,
            likes_count INTEGER,
            user_rating REAL DEFAULT 3.0,
            times_drawn INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Ingredients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            ingredient_name TEXT NOT NULL,
            quantity REAL,
            unit TEXT,
            notes TEXT,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id)
        )
    ''')
    
    # Instructions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS instructions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            step_number INTEGER,
            instruction TEXT,
            tips TEXT,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id)
        )
    ''')
    
    # Nutrition table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nutrition (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            calories INTEGER,
            protein REAL,
            carbohydrate REAL,
            fat REAL,
            fiber REAL,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id)
        )
    ''')
    
    # Draw history table (to track what was drawn for each day)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS draw_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            draw_date TEXT NOT NULL,
            confirmed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id)
        )
    ''')
    
    conn.commit()
    print("✅ All tables created successfully!")


def insert_recipes(conn):
    """Insert all recipe data."""
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM recipes")
    if cursor.fetchone()[0] > 0:
        print("⚠️  Data already exists, skipping insertion.")
        return
    
    # Recipe data extracted from the document
    recipes = [
        {
            "recipe_name": "清蒸鸡蛋",
            "recipe_name_en": "Steamed Egg",
            "category": "蛋白质",
            "difficulty": 1,
            "cooking_time": 10,
            "source_article": "合集3.0｜吃对早餐 把自己养的气血丰盈",
            "source_author": "养生的鹅er",
            "source_link": "https://www.xiaohongshu.com/explore/6691e8960000000025004f3f",
            "publish_date": "2025-01-07",
            "likes_count": 11000,
            "ingredients": [
                {"name": "鸡蛋", "quantity": 2, "unit": "个", "notes": ""},
                {"name": "温水", "quantity": 3, "unit": "汤匙", "notes": "约45ml"},
                {"name": "盐", "quantity": 0.5, "unit": "克", "notes": "少许"}
            ],
            "instructions": [
                {"step": 1, "description": "鸡蛋打入碗中，加温水搅拌均匀"},
                {"step": 2, "description": "过筛去泡沫"},
                {"step": 3, "description": "盖保鲜膜（戳几个小孔透气）"},
                {"step": 4, "description": "大火烧水后，中火蒸8-10分钟"}
            ],
            "nutrition": {"calories": 155, "protein": 12, "carbohydrate": 1.1, "fat": 11, "fiber": 0}
        },
        {
            "recipe_name": "水煮鸡蛋",
            "recipe_name_en": "Boiled Egg",
            "category": "蛋白质",
            "difficulty": 1,
            "cooking_time": 12,
            "source_article": "一人食早餐沙拉合集🥗健康美味一盘端🍽",
            "source_author": "奶茶味可可",
            "source_link": "https://www.xiaohongshu.com/explore/6612088e000000001a01717c",
            "publish_date": "2024-04-07",
            "likes_count": 14000,
            "ingredients": [
                {"name": "鸡蛋", "quantity": 2, "unit": "个", "notes": ""},
                {"name": "清水", "quantity": 500, "unit": "ml", "notes": ""}
            ],
            "instructions": [
                {"step": 1, "description": "冷水下锅放入鸡蛋"},
                {"step": 2, "description": "大火烧开后转中火"},
                {"step": 3, "description": "煮7-8分钟（溏心蛋）或10分钟（全熟）"},
                {"step": 4, "description": "冷水冰镇，剥壳"}
            ],
            "nutrition": {"calories": 155, "protein": 12, "carbohydrate": 1.1, "fat": 11, "fiber": 0}
        },
        {
            "recipe_name": "烤红薯",
            "recipe_name_en": "Baked Sweet Potato",
            "category": "粗粮谷物",
            "difficulty": 1,
            "cooking_time": 20,
            "source_article": "吃瘦不饿瘦｜一周低卡减脂早餐合集",
            "source_author": "其其轻食餐",
            "source_link": "https://www.xiaohongshu.com/explore/682c8ca0000000001101e744",
            "publish_date": "2025-05-20",
            "likes_count": 14000,
            "ingredients": [
                {"name": "红薯", "quantity": 200, "unit": "g", "notes": "中等大小1个"},
                {"name": "油", "quantity": 0.5, "unit": "汤匙", "notes": "可选"}
            ],
            "instructions": [
                {"step": 1, "description": "红薯洗净、沥干"},
                {"step": 2, "description": "高压锅蒸15分钟快速熟透 或 微波炉5分钟"},
                {"step": 3, "description": "烤箱180°烤8分钟至表面焦香"},
                {"step": 4, "description": "切块即可"}
            ],
            "nutrition": {"calories": 103, "protein": 1.6, "carbohydrate": 26, "fat": 0.1, "fiber": 3.6}
        },
        {
            "recipe_name": "清蒸玉米",
            "recipe_name_en": "Steamed Corn",
            "category": "粗粮谷物",
            "difficulty": 1,
            "cooking_time": 20,
            "source_article": "吃瘦不饿瘦｜一周低卡减脂早餐合集",
            "source_author": "其其轻食餐",
            "source_link": "https://www.xiaohongshu.com/explore/682c8ca0000000001101e744",
            "publish_date": "2025-05-20",
            "likes_count": 14000,
            "ingredients": [
                {"name": "玉米", "quantity": 1, "unit": "根", "notes": ""},
                {"name": "清水", "quantity": 800, "unit": "ml", "notes": ""}
            ],
            "instructions": [
                {"step": 1, "description": "玉米剥去外层叶子"},
                {"step": 2, "description": "放入蒸锅中"},
                {"step": 3, "description": "大火蒸15-20分钟 或 高压锅8分钟"}
            ],
            "nutrition": {"calories": 96, "protein": 3.3, "carbohydrate": 19, "fat": 1.3, "fiber": 2.4}
        },
        {
            "recipe_name": "虾仁沙拉",
            "recipe_name_en": "Shrimp Salad",
            "category": "蛋白质",
            "difficulty": 2,
            "cooking_time": 10,
            "source_article": "一人食早餐沙拉合集🥗健康美味一盘端🍽",
            "source_author": "奶茶味可可",
            "source_link": "https://www.xiaohongshu.com/explore/6612088e000000001a01717c",
            "publish_date": "2024-04-07",
            "likes_count": 14000,
            "ingredients": [
                {"name": "虾仁", "quantity": 150, "unit": "g", "notes": ""},
                {"name": "生菜", "quantity": 50, "unit": "g", "notes": ""},
                {"name": "番茄", "quantity": 100, "unit": "g", "notes": ""},
                {"name": "水煮蛋", "quantity": 2, "unit": "个", "notes": ""},
                {"name": "橄榄油", "quantity": 1, "unit": "汤匙", "notes": ""},
                {"name": "盐", "quantity": 0.5, "unit": "克", "notes": ""},
                {"name": "黑胡椒", "quantity": 0.3, "unit": "克", "notes": ""}
            ],
            "instructions": [
                {"step": 1, "description": "虾仁用盐腌制5分钟"},
                {"step": 2, "description": "热水煮1-2分钟至变色"},
                {"step": 3, "description": "生菜洗净、番茄切片"},
                {"step": 4, "description": "将所有食材拼盘"},
                {"step": 5, "description": "淋橄榄油，撒盐黑胡椒"}
            ],
            "nutrition": {"calories": 280, "protein": 25, "carbohydrate": 8, "fat": 14, "fiber": 2}
        },
        {
            "recipe_name": "香煎鸡胸肉",
            "recipe_name_en": "Pan-fried Chicken Breast",
            "category": "蛋白质",
            "difficulty": 2,
            "cooking_time": 12,
            "source_article": "一人食早餐沙拉合集🥗健康美味一盘端🍽",
            "source_author": "奶茶味可可",
            "source_link": "https://www.xiaohongshu.com/explore/6612088e000000001a01717c",
            "publish_date": "2024-04-07",
            "likes_count": 14000,
            "ingredients": [
                {"name": "鸡胸肉", "quantity": 150, "unit": "g", "notes": ""},
                {"name": "盐", "quantity": 0.5, "unit": "克", "notes": ""},
                {"name": "黑胡椒", "quantity": 0.3, "unit": "克", "notes": ""},
                {"name": "橄榄油", "quantity": 1, "unit": "汤匙", "notes": ""}
            ],
            "instructions": [
                {"step": 1, "description": "鸡胸肉用刀背拍松"},
                {"step": 2, "description": "用盐和黑胡椒腌制10分钟"},
                {"step": 3, "description": "平底锅加油，中火煎至两面金黄"},
                {"step": 4, "description": "切片装盘"}
            ],
            "nutrition": {"calories": 200, "protein": 35, "carbohydrate": 0, "fat": 6, "fiber": 0}
        },
        {
            "recipe_name": "牛油果吐司",
            "recipe_name_en": "Avocado Toast",
            "category": "粗粮谷物",
            "difficulty": 1,
            "cooking_time": 5,
            "source_article": "一人食早餐沙拉合集🥗健康美味一盘端🍽",
            "source_author": "奶茶味可可",
            "source_link": "https://www.xiaohongshu.com/explore/6612088e000000001a01717c",
            "publish_date": "2024-04-07",
            "likes_count": 14000,
            "ingredients": [
                {"name": "全麦吐司", "quantity": 2, "unit": "片", "notes": ""},
                {"name": "牛油果", "quantity": 1, "unit": "个", "notes": ""},
                {"name": "盐", "quantity": 0.3, "unit": "克", "notes": ""},
                {"name": "柠檬汁", "quantity": 1, "unit": "茶匙", "notes": ""}
            ],
            "instructions": [
                {"step": 1, "description": "吐司烤至金黄"},
                {"step": 2, "description": "牛油果切开去核，捣成泥"},
                {"step": 3, "description": "加盐和柠檬汁拌匀"},
                {"step": 4, "description": "涂在吐司上即可"}
            ],
            "nutrition": {"calories": 320, "protein": 8, "carbohydrate": 30, "fat": 20, "fiber": 8}
        },
        {
            "recipe_name": "燕麦粥",
            "recipe_name_en": "Oatmeal Porridge",
            "category": "粗粮谷物",
            "difficulty": 1,
            "cooking_time": 10,
            "source_article": "合集3.0｜吃对早餐 把自己养的气血丰盈",
            "source_author": "养生的鹅er",
            "source_link": "https://www.xiaohongshu.com/explore/6691e8960000000025004f3f",
            "publish_date": "2025-01-07",
            "likes_count": 11000,
            "ingredients": [
                {"name": "燕麦", "quantity": 50, "unit": "g", "notes": ""},
                {"name": "牛奶", "quantity": 200, "unit": "ml", "notes": ""},
                {"name": "蜂蜜", "quantity": 1, "unit": "汤匙", "notes": "可选"},
                {"name": "水果", "quantity": 50, "unit": "g", "notes": "蓝莓/香蕉等"}
            ],
            "instructions": [
                {"step": 1, "description": "燕麦加牛奶煮沸"},
                {"step": 2, "description": "小火煮5分钟至浓稠"},
                {"step": 3, "description": "加蜂蜜和水果装饰"}
            ],
            "nutrition": {"calories": 280, "protein": 10, "carbohydrate": 45, "fat": 8, "fiber": 5}
        },
        {
            "recipe_name": "酸奶水果杯",
            "recipe_name_en": "Yogurt Fruit Cup",
            "category": "蛋白质",
            "difficulty": 1,
            "cooking_time": 5,
            "source_article": "吃瘦不饿瘦｜一周低卡减脂早餐合集",
            "source_author": "其其轻食餐",
            "source_link": "https://www.xiaohongshu.com/explore/682c8ca0000000001101e744",
            "publish_date": "2025-05-20",
            "likes_count": 14000,
            "ingredients": [
                {"name": "希腊酸奶", "quantity": 150, "unit": "g", "notes": ""},
                {"name": "蓝莓", "quantity": 30, "unit": "g", "notes": ""},
                {"name": "草莓", "quantity": 50, "unit": "g", "notes": ""},
                {"name": "燕麦", "quantity": 20, "unit": "g", "notes": ""},
                {"name": "蜂蜜", "quantity": 1, "unit": "茶匙", "notes": ""}
            ],
            "instructions": [
                {"step": 1, "description": "酸奶倒入杯中"},
                {"step": 2, "description": "水果洗净切块"},
                {"step": 3, "description": "撒上燕麦和蜂蜜"}
            ],
            "nutrition": {"calories": 200, "protein": 15, "carbohydrate": 25, "fat": 5, "fiber": 3}
        },
        {
            "recipe_name": "蔬菜煎蛋",
            "recipe_name_en": "Vegetable Omelette",
            "category": "蛋白质",
            "difficulty": 2,
            "cooking_time": 10,
            "source_article": "合集3.0｜吃对早餐 把自己养的气血丰盈",
            "source_author": "养生的鹅er",
            "source_link": "https://www.xiaohongshu.com/explore/6691e8960000000025004f3f",
            "publish_date": "2025-01-07",
            "likes_count": 11000,
            "ingredients": [
                {"name": "鸡蛋", "quantity": 2, "unit": "个", "notes": ""},
                {"name": "番茄", "quantity": 50, "unit": "g", "notes": ""},
                {"name": "青椒", "quantity": 30, "unit": "g", "notes": ""},
                {"name": "洋葱", "quantity": 20, "unit": "g", "notes": ""},
                {"name": "盐", "quantity": 0.5, "unit": "克", "notes": ""},
                {"name": "油", "quantity": 1, "unit": "汤匙", "notes": ""}
            ],
            "instructions": [
                {"step": 1, "description": "蔬菜切丁"},
                {"step": 2, "description": "鸡蛋打散加盐"},
                {"step": 3, "description": "平底锅加油，倒入蛋液"},
                {"step": 4, "description": "撒上蔬菜丁，两面煎熟"}
            ],
            "nutrition": {"calories": 220, "protein": 14, "carbohydrate": 8, "fat": 15, "fiber": 2}
        },
        {
            "recipe_name": "豆浆",
            "recipe_name_en": "Soy Milk",
            "category": "饮品",
            "difficulty": 1,
            "cooking_time": 15,
            "source_article": "合集3.0｜吃对早餐 把自己养的气血丰盈",
            "source_author": "养生的鹅er",
            "source_link": "https://www.xiaohongshu.com/explore/6691e8960000000025004f3f",
            "publish_date": "2025-01-07",
            "likes_count": 11000,
            "ingredients": [
                {"name": "黄豆", "quantity": 50, "unit": "g", "notes": "提前泡8小时"},
                {"name": "水", "quantity": 500, "unit": "ml", "notes": ""},
                {"name": "糖", "quantity": 1, "unit": "汤匙", "notes": "可选"}
            ],
            "instructions": [
                {"step": 1, "description": "黄豆提前泡发"},
                {"step": 2, "description": "放入豆浆机加水"},
                {"step": 3, "description": "选择豆浆模式"},
                {"step": 4, "description": "过滤后加糖调味"}
            ],
            "nutrition": {"calories": 80, "protein": 7, "carbohydrate": 4, "fat": 4, "fiber": 1}
        },
        {
            "recipe_name": "小米粥",
            "recipe_name_en": "Millet Porridge",
            "category": "粗粮谷物",
            "difficulty": 1,
            "cooking_time": 30,
            "source_article": "合集3.0｜吃对早餐 把自己养的气血丰盈",
            "source_author": "养生的鹅er",
            "source_link": "https://www.xiaohongshu.com/explore/6691e8960000000025004f3f",
            "publish_date": "2025-01-07",
            "likes_count": 11000,
            "ingredients": [
                {"name": "小米", "quantity": 50, "unit": "g", "notes": ""},
                {"name": "水", "quantity": 500, "unit": "ml", "notes": ""},
                {"name": "红枣", "quantity": 3, "unit": "颗", "notes": "可选"},
                {"name": "枸杞", "quantity": 5, "unit": "g", "notes": "可选"}
            ],
            "instructions": [
                {"step": 1, "description": "小米洗净"},
                {"step": 2, "description": "水烧开后加入小米"},
                {"step": 3, "description": "小火煮25-30分钟至浓稠"},
                {"step": 4, "description": "加入红枣枸杞焖5分钟"}
            ],
            "nutrition": {"calories": 150, "protein": 4, "carbohydrate": 32, "fat": 1, "fiber": 2}
        },
        {
            "recipe_name": "煎蛋火腿豆腐米粉",
            "recipe_name_en": "Rice Noodles with Egg, Ham & Tofu",
            "category": "综合早餐",
            "difficulty": 2,
            "cooking_time": 20,
            "source_article": "用户自定义",
            "source_author": "User",
            "source_link": "",
            "publish_date": "2024-01-20",
            "likes_count": 0,
            "ingredients": [
                {"name": "米粉", "quantity": 1, "unit": "份", "notes": "干米粉需提前泡发"},
                {"name": "鸡蛋", "quantity": 2, "unit": "个", "notes": ""},
                {"name": "火腿肠", "quantity": 1, "unit": "根", "notes": ""},
                {"name": "老豆腐", "quantity": 100, "unit": "g", "notes": "切小方块"},
                {"name": "白菜", "quantity": 50, "unit": "g", "notes": "或娃娃菜"},
                {"name": "黑芝麻", "quantity": 1, "unit": "g", "notes": "点缀用"}
            ],
            "instructions": [
                {"step": 1, "description": "【准备】米粉泡软，白菜切段，豆腐切块，香肠改刀"},
                {"step": 2, "description": "【煮粉】水开下米粉，中火煮3-5分钟至软熟，捞出装盘"},
                {"step": 3, "description": "【焯菜】用煮粉水焯熟白菜，沥干摆盘"},
                {"step": 4, "description": "【煎豆腐】平底锅煎豆腐至四面金黄，撒盐调味"},
                {"step": 5, "description": "【煎肉蛋】煎香肠至微焦；煎荷包蛋至喜欢的熟度"},
                {"step": 6, "description": "【装盘】组合所有食材，撒黑芝麻，可淋少许生抽"}
            ],
            "nutrition": {"calories": 550, "protein": 25, "carbohydrate": 65, "fat": 22, "fiber": 6}
        }
    ]
    
    for recipe in recipes:
        # Insert recipe
        cursor.execute('''
            INSERT INTO recipes (recipe_name, recipe_name_en, category, difficulty, 
                cooking_time, source_article, source_author, source_link, 
                publish_date, likes_count, user_rating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            recipe['recipe_name'], recipe['recipe_name_en'], recipe['category'],
            recipe['difficulty'], recipe['cooking_time'], recipe['source_article'],
            recipe['source_author'], recipe['source_link'], recipe['publish_date'],
            recipe['likes_count'], 3.0
        ))
        recipe_id = cursor.lastrowid
        
        # Insert ingredients
        for ing in recipe['ingredients']:
            cursor.execute('''
                INSERT INTO ingredients (recipe_id, ingredient_name, quantity, unit, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (recipe_id, ing['name'], ing['quantity'], ing['unit'], ing.get('notes', '')))
        
        # Insert instructions
        for inst in recipe['instructions']:
            cursor.execute('''
                INSERT INTO instructions (recipe_id, step_number, instruction)
                VALUES (?, ?, ?)
            ''', (recipe_id, inst['step'], inst['description']))
        
        # Insert nutrition
        nutr = recipe['nutrition']
        cursor.execute('''
            INSERT INTO nutrition (recipe_id, calories, protein, carbohydrate, fat, fiber)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (recipe_id, nutr['calories'], nutr['protein'], nutr['carbohydrate'], 
              nutr['fat'], nutr['fiber']))
    
    conn.commit()
    print(f"✅ Inserted {len(recipes)} recipes with all related data!")


def main():
    """Main entry point."""
    # Remove existing database if exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🗑️  Removed existing database.")
    
    conn = sqlite3.connect(DB_PATH)
    try:
        create_tables(conn)
        insert_recipes(conn)
        
        # Verify data
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM recipes")
        recipe_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM ingredients")
        ingredient_count = cursor.fetchone()[0]
        
        print(f"\n📊 Database Summary:")
        print(f"   - Recipes: {recipe_count}")
        print(f"   - Ingredients: {ingredient_count}")
        print(f"\n✨ Database initialized successfully at: {DB_PATH}")
        
    finally:
        conn.close()


if __name__ == '__main__':
    main()
