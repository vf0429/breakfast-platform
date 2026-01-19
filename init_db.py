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
        },
    {
        "recipe_name": "减脂早餐-葱油荞麦面配糖醋煎蛋",
        "recipe_name_en": "Light Scallion Buckwheat Noodles with Sweet-Sour Fried Eggs",
        "category": "综合早餐",
        "difficulty": 2,
        "cooking_time": 20,
        "source_article": "一周不重样中式减脂早餐",
        "source_author": "小红书博主（未署名）",
        "source_link": "",
        "publish_date": "2025-01-01",
        "likes_count": 0,
        "ingredients": [
        {"name": "荞麦葱油速食面", "quantity": 80, "unit": "g", "notes": "干面饼约1份"},
        {"name": "葱油酱包", "quantity": 15, "unit": "g", "notes": "只用2/3包"},
        {"name": "鸡蛋", "quantity": 2, "unit": "个", "notes": "全蛋煎"},
        {"name": "油", "quantity": 5, "unit": "g", "notes": "煎蛋用，约1小勺"},
        {"name": "蒜末", "quantity": 5, "unit": "g", "notes": ""},
        {"name": "生抽", "quantity": 10, "unit": "g", "notes": "糖醋汁"},
        {"name": "代糖", "quantity": 2, "unit": "g", "notes": "约1小勺"},
        {"name": "米醋", "quantity": 15, "unit": "g", "notes": ""},
        {"name": "水", "quantity": 30, "unit": "g", "notes": "调糖醋汁"},
        {"name": "青菜（小白菜或生菜）", "quantity": 80, "unit": "g", "notes": "焯水"},
        {"name": "葱花", "quantity": 5, "unit": "g", "notes": "面上点缀"}
        ],
        "instructions": [
        {"step": 1, "description": "荞麦面按说明煮熟沥干，与2/3葱油酱和少量葱花拌匀装碗。"},
        {"step": 2, "description": "青菜焯水至断生捞出摆盘。"},
        {"step": 3, "description": "平底锅加少量油煎2个鸡蛋至两面金黄盛出。"},
        {"step": 4, "description": "锅内下蒜末炒香，加入生抽、米醋、代糖和水煮沸收稍浓，淋在煎蛋上。"},
        {"step": 5, "description": "将葱油面、糖醋煎蛋和焯青菜一起装盘食用。"}
        ],
        "nutrition": {"calories": 560, "protein": 24, "carbohydrate": 65, "fat": 22, "fiber": 6}
    },
    {
        "recipe_name": "减脂早餐-全麦鸡蛋汉堡",
        "recipe_name_en": "Whole Wheat Egg Burger",
        "category": "综合早餐",
        "difficulty": 2,
        "cooking_time": 25,
        "source_article": "一周不重样中式减脂早餐",
        "source_author": "小红书博主（未署名）",
        "source_link": "",
        "publish_date": "2025-01-01",
        "likes_count": 0,
        "ingredients": [
        {"name": "全麦粉", "quantity": 50, "unit": "g", "notes": "面饼用"},
        {"name": "小麦粉", "quantity": 50, "unit": "g", "notes": "面饼用"},
        {"name": "清水", "quantity": 80, "unit": "g", "notes": "和面"},
        {"name": "鸡蛋", "quantity": 2, "unit": "个", "notes": "做夹心"},
        {"name": "牛肉末", "quantity": 100, "unit": "g", "notes": "与鸡蛋同煎"},
        {"name": "淀粉", "quantity": 10, "unit": "g", "notes": "汉堡肉定型"},
        {"name": "生抽", "quantity": 5, "unit": "g", "notes": "调牛肉"},
        {"name": "料酒", "quantity": 5, "unit": "g", "notes": ""},
        {"name": "盐", "quantity": 1, "unit": "g", "notes": ""},
        {"name": "葱花", "quantity": 5, "unit": "g", "notes": "加入蛋液"},
        {"name": "辣椒酱", "quantity": 15, "unit": "g", "notes": "抹在汉堡上"},
        {"name": "油", "quantity": 5, "unit": "g", "notes": "煎饼煎蛋用"},
        {"name": "炒菠菜", "quantity": 100, "unit": "g", "notes": "配菜"},
        {"name": "蔬菜汁/青汁", "quantity": 200, "unit": "g", "notes": "饮用"}
        ],
        "instructions": [
        {"step": 1, "description": "全麦粉和小麦粉加水和成面团，醒发后分成小剂子压成圆饼，小火两面煎熟备用。"},
        {"step": 2, "description": "牛肉末加淀粉、生抽、料酒和少量盐抓匀腌制20分钟。"},
        {"step": 3, "description": "鸡蛋打散加入葱花，倒入模具中铺底，上面铺一层腌好的牛肉末，小火煎熟成厚蛋肉饼。"},
        {"step": 4, "description": "将煎好的全麦饼横切，对夹厚蛋肉饼，表面抹上辣椒酱。"},
        {"step": 5, "description": "另起锅清炒菠菜，加少量盐调味，搭配青汁与汉堡一起食用。"}
        ],
        "nutrition": {"calories": 470, "protein": 30, "carbohydrate": 45, "fat": 15, "fiber": 7}
    },
    {
        "recipe_name": "早餐-大虾全麦蒸饺",
        "recipe_name_en": "Whole Wheat Shrimp Steamed Dumplings",
        "category": "综合早餐",
        "difficulty": 3,
        "cooking_time": 30,
        "source_article": "一周不重样中式减脂早餐",
        "source_author": "小红书博主（未署名）",
        "source_link": "",
        "publish_date": "2025-01-01",
        "likes_count": 0,
        "ingredients": [
        {"name": "虾仁带尾", "quantity": 8, "unit": "只", "notes": "去壳留尾"},
        {"name": "猪肉末或鸡肉末", "quantity": 150, "unit": "g", "notes": "馅料"},
        {"name": "胡萝卜", "quantity": 20, "unit": "g", "notes": "切碎"},
        {"name": "木耳", "quantity": 15, "unit": "g", "notes": "泡发切碎"},
        {"name": "芹菜", "quantity": 20, "unit": "g", "notes": "切碎"},
        {"name": "香菇", "quantity": 20, "unit": "g", "notes": "切碎"},
        {"name": "葱", "quantity": 10, "unit": "g", "notes": "切碎"},
        {"name": "全麦饺子皮", "quantity": 8, "unit": "张", "notes": "自制或成品"},
        {"name": "生抽", "quantity": 5, "unit": "g", "notes": "调馅"},
        {"name": "蚝油", "quantity": 5, "unit": "g", "notes": ""},
        {"name": "盐", "quantity": 1, "unit": "g", "notes": ""},
        {"name": "胡椒粉", "quantity": 0.5, "unit": "g", "notes": ""},
        {"name": "无糖豆浆粉", "quantity": 20, "unit": "g", "notes": "豆浆"},
        {"name": "糯小圆子", "quantity": 15, "unit": "g", "notes": "加入豆浆"},
        {"name": "水", "quantity": 250, "unit": "g", "notes": "冲豆浆粉"},
        {"name": "黄瓜", "quantity": 80, "unit": "g", "notes": "切薄片卷成黄瓜卷"},
        {"name": "茶叶蛋", "quantity": 1, "unit": "个", "notes": "配菜"}
        ],
        "instructions": [
        {"step": 1, "description": "将肉末与胡萝卜、木耳、芹菜、香菇和葱碎混合，加入生抽、蚝油、盐和胡椒粉搅拌成馅。"},
        {"step": 2, "description": "全麦饺子皮上先放少量馅，再放整只带尾虾仁，包成敞口蒸饺形状。"},
        {"step": 3, "description": "蒸锅水开后放入蒸饺，大火蒸约15分钟至熟。"},
        {"step": 4, "description": "无糖豆浆粉加水煮开，放入小圆子煮至浮起成豆浆小圆子汤。"},
        {"step": 5, "description": "黄瓜切薄片卷成黄瓜卷，搭配茶叶蛋、蒸饺和豆浆一起装盘食用。"}
        ],
        "nutrition": {"calories": 370, "protein": 28, "carbohydrate": 35, "fat": 10, "fiber": 5}
    },
    {
        "recipe_name": "早餐-低卡豆腐脑配饺子蔬菜蛋",
        "recipe_name_en": "Low-Calorie Tofu Pudding with Dumplings, Vegetables and Egg",
        "category": "综合早餐",
        "difficulty": 2,
        "cooking_time": 25,
        "source_article": "一周不重样中式减脂早餐",
        "source_author": "小红书博主（未署名）",
        "source_link": "",
        "publish_date": "2025-01-01",
        "likes_count": 0,
        "ingredients": [
        {"name": "嫩豆腐", "quantity": 200, "unit": "g", "notes": "整块冲热做豆腐脑"},
        {"name": "火腿丝", "quantity": 20, "unit": "g", "notes": ""},
        {"name": "木耳丝", "quantity": 15, "unit": "g", "notes": ""},
        {"name": "金针菇", "quantity": 20, "unit": "g", "notes": "切短"},
        {"name": "胡萝卜丝", "quantity": 15, "unit": "g", "notes": ""},
        {"name": "生抽", "quantity": 5, "unit": "g", "notes": ""},
        {"name": "蚝油", "quantity": 5, "unit": "g", "notes": ""},
        {"name": "醋", "quantity": 5, "unit": "g", "notes": ""},
        {"name": "胡椒粉", "quantity": 0.5, "unit": "g", "notes": ""},
        {"name": "水或高汤", "quantity": 250, "unit": "g", "notes": "煮豆腐脑汤底"},
        {"name": "鸡蛋", "quantity": 1, "unit": "个", "notes": "打入汤中成蛋花"},
        {"name": "香菜", "quantity": 5, "unit": "g", "notes": "出锅撒上"},
        {"name": "速冻饺子", "quantity": 3, "unit": "个", "notes": "水煮"},
        {"name": "西兰花", "quantity": 80, "unit": "g", "notes": "焯水"},
        {"name": "水煮蛋", "quantity": 1, "unit": "个", "notes": "对半切"}
        ],
        "instructions": [
        {"step": 1, "description": "嫩豆腐表面冲热水后切块放入碗中备用。"},
        {"step": 2, "description": "锅中加入水或高汤，下火腿丝、木耳丝、金针菇和胡萝卜丝煮至断生。"},
        {"step": 3, "description": "加入生抽、蚝油、醋和胡椒粉调味，倒入豆腐碗中。"},
        {"step": 4, "description": "再次烧开后打入蛋液搅动成蛋花，撒香菜即可成低卡豆腐脑。"},
        {"step": 5, "description": "同时煮熟饺子和西兰花，水煮蛋切片，与豆腐脑一起装盘。"}
        ],
        "nutrition": {"calories": 450, "protein": 28, "carbohydrate": 40, "fat": 16, "fiber": 6}
    },
    {
        "recipe_name": "早餐-鸡肉玉米蒸包配冬瓜口蘑汤",
        "recipe_name_en": "Chicken Corn Steamed Buns with Winter Melon Mushroom Soup",
        "category": "综合早餐",
        "difficulty": 3,
        "cooking_time": 35,
        "source_article": "一周不重样中式减脂早餐",
        "source_author": "小红书博主（未署名）",
        "source_link": "",
        "publish_date": "2025-01-01",
        "likes_count": 0,
        "ingredients": [
        {"name": "鸡胸肉末", "quantity": 150, "unit": "g", "notes": ""},
        {"name": "玉米粒", "quantity": 50, "unit": "g", "notes": ""},
        {"name": "胡萝卜丁", "quantity": 20, "unit": "g", "notes": ""},
        {"name": "香菇丁", "quantity": 30, "unit": "g", "notes": ""},
        {"name": "葱花", "quantity": 10, "unit": "g", "notes": ""},
        {"name": "生抽", "quantity": 5, "unit": "g", "notes": ""},
        {"name": "蚝油", "quantity": 5, "unit": "g", "notes": ""},
        {"name": "盐", "quantity": 1, "unit": "g", "notes": ""},
        {"name": "胡椒粉", "quantity": 0.5, "unit": "g", "notes": ""},
        {"name": "饺子皮或云吞皮", "quantity": 10, "unit": "张", "notes": "擀薄做蒸包皮"},
        {"name": "腌黄瓜", "quantity": 30, "unit": "g", "notes": "配菜"},
        {"name": "茶叶蛋", "quantity": 2, "unit": "个", "notes": ""},
        {"name": "冬瓜", "quantity": 150, "unit": "g", "notes": "切块"},
        {"name": "口蘑", "quantity": 80, "unit": "g", "notes": "切片"},
        {"name": "水", "quantity": 400, "unit": "g", "notes": "煮汤"},
        {"name": "盐（汤用）", "quantity": 1, "unit": "g", "notes": ""},
        {"name": "香菜或葱花（汤用）", "quantity": 5, "unit": "g", "notes": ""}
        ],
        "instructions": [
        {"step": 1, "description": "鸡肉末与玉米粒、胡萝卜丁、香菇丁和葱花混合，加入生抽、蚝油、盐和胡椒粉拌成馅。"},
        {"step": 2, "description": "每张饺子皮擀薄，包入适量鸡肉玉米馅，收口成小蒸包。"},
        {"step": 3, "description": "蒸锅水开后放入蒸包，大火蒸约15分钟至熟。"},
        {"step": 4, "description": "锅中下少量油炒香口蘑片，加水煮开后加入冬瓜块煮至透明软熟，调入盐并撒香菜或葱花。"},
        {"step": 5, "description": "蒸包配茶叶蛋和腌黄瓜装盘，配冬瓜口蘑汤一起食用。"}
        ],
        "nutrition": {"calories": 430, "protein": 30, "carbohydrate": 45, "fat": 10, "fiber": 5}
    },
    {
        "recipe_name": "早餐-燕皮三鲜馄饨配煎蛋和西柚",
        "recipe_name_en": "Three-Delicacy Wonton in Broth with Fried Egg and Grapefruit",
        "category": "综合早餐",
        "difficulty": 3,
        "cooking_time": 30,
        "source_article": "一周不重样中式减脂早餐",
        "source_author": "小红书博主（未署名）",
        "source_link": "",
        "publish_date": "2025-01-01",
        "likes_count": 0,
        "ingredients": [
        {"name": "燕皮馄饨皮", "quantity": 15, "unit": "张", "notes": "或薄云吞皮"},
        {"name": "虾仁碎", "quantity": 80, "unit": "g", "notes": ""},
        {"name": "猪瘦肉末", "quantity": 60, "unit": "g", "notes": ""},
        {"name": "木耳碎", "quantity": 15, "unit": "g", "notes": ""},
        {"name": "胡萝卜碎", "quantity": 20, "unit": "g", "notes": ""},
        {"name": "韭菜碎", "quantity": 20, "unit": "g", "notes": ""},
        {"name": "生抽", "quantity": 5, "unit": "g", "notes": ""},
        {"name": "蚝油", "quantity": 5, "unit": "g", "notes": ""},
        {"name": "盐", "quantity": 1, "unit": "g", "notes": ""},
        {"name": "胡椒粉", "quantity": 0.5, "unit": "g", "notes": ""},
        {"name": "香油", "quantity": 2, "unit": "g", "notes": ""},
        {"name": "清水或高汤", "quantity": 400, "unit": "g", "notes": "煮馄饨"},
        {"name": "枸杞、葱花", "quantity": 5, "unit": "g", "notes": "汤面点缀"},
        {"name": "鸡蛋", "quantity": 1, "unit": "个", "notes": "煎蛋"},
        {"name": "油", "quantity": 3, "unit": "g", "notes": "煎蛋用"},
        {"name": "无糖酱油", "quantity": 5, "unit": "g", "notes": "淋在煎蛋上"},
        {"name": "西柚", "quantity": 150, "unit": "g", "notes": "去皮分瓣"}
        ],
        "instructions": [
        {"step": 1, "description": "将虾仁碎、瘦肉末、木耳碎、胡萝卜碎和韭菜碎混合，加入生抽、蚝油、盐、胡椒粉和香油拌匀成三鲜馅。"},
        {"step": 2, "description": "每张燕皮包入少量三鲜馅，对折并收紧两角成馄饨。"},
        {"step": 3, "description": "锅中烧开清水或高汤，下馄饨煮至全部浮起再煮2分钟，出锅撒枸杞和葱花。"},
        {"step": 4, "description": "平底锅放少量油煎1个鸡蛋至八分熟，出锅后表面淋少量无糖酱油。"},
        {"step": 5, "description": "西柚去皮分瓣，与馄饨汤和煎蛋一起装盘食用。"}
        ],
        "nutrition": {"calories": 335, "protein": 24, "carbohydrate": 30, "fat": 10, "fiber": 4}
    },
    {
        "recipe_name": "减脂早餐-肉酱拌面配秋葵炒蛋",
        "recipe_name_en": "Minced Meat Sauce Noodles with Okra Scrambled Eggs",
        "category": "综合早餐",
        "difficulty": 2,
        "cooking_time": 25,
        "source_article": "一周不重样中式减脂早餐",
        "source_author": "小红书博主（未署名）",
        "source_link": "",
        "publish_date": "2025-01-01",
        "likes_count": 0,
        "ingredients": [
        {"name": "粗面或意面", "quantity": 80, "unit": "g", "notes": "干面"},
        {"name": "牛肉末", "quantity": 50, "unit": "g", "notes": ""},
        {"name": "小米辣", "quantity": 5, "unit": "g", "notes": "切圈"},
        {"name": "葱花", "quantity": 5, "unit": "g", "notes": ""},
        {"name": "生抽", "quantity": 15, "unit": "g", "notes": ""},
        {"name": "蚝油", "quantity": 5, "unit": "g", "notes": ""},
        {"name": "豆瓣酱/辣酱", "quantity": 5, "unit": "g", "notes": ""},
        {"name": "糖或代糖", "quantity": 2, "unit": "g", "notes": ""},
        {"name": "清水", "quantity": 50, "unit": "g", "notes": "调肉酱"},
        {"name": "油", "quantity": 5, "unit": "g", "notes": "炒肉用"},
        {"name": "鸡蛋", "quantity": 2, "unit": "个", "notes": "秋葵炒蛋"},
        {"name": "秋葵", "quantity": 80, "unit": "g", "notes": "切片"},
        {"name": "盐", "quantity": 0.5, "unit": "g", "notes": "炒蛋调味"},
        {"name": "玉米须茶/谷物茶饮", "quantity": 250, "unit": "g", "notes": "随餐饮品"}
        ],
        "instructions": [
        {"step": 1, "description": "面条煮熟沥干备用。"},
        {"step": 2, "description": "锅中放少量油炒香牛肉末，加入小米辣和葱花翻炒。"},
        {"step": 3, "description": "加入生抽、蚝油、豆瓣酱、糖和少量水，小火收成浓稠肉酱。"},
        {"step": 4, "description": "将肉酱浇在面条上拌匀。"},
        {"step": 5, "description": "另起锅少油炒熟秋葵片，倒入打散的鸡蛋加盐炒熟，配在一旁并搭配茶饮食用。"}
        ],
        "nutrition": {"calories": 510, "protein": 26, "carbohydrate": 60, "fat": 18, "fiber": 5}
    },
    {
        "recipe_name": "减脂早餐-桂花圆子红豆汤配蔬菜厚蛋烧",
        "recipe_name_en": "Osmanthus Glutinous Rice Ball Red Bean Soup with Veggie Thick Omelette",
        "category": "综合早餐",
        "difficulty": 2,
        "cooking_time": 30,
        "source_article": "一周不重样中式减脂早餐",
        "source_author": "小红书博主（未署名）",
        "source_link": "",
        "publish_date": "2025-01-01",
        "likes_count": 0,
        "ingredients": [
        {"name": "即食红豆片", "quantity": 50, "unit": "g", "notes": ""},
        {"name": "小圆子（糯米丸子）", "quantity": 20, "unit": "g", "notes": ""},
        {"name": "桂花", "quantity": 2, "unit": "g", "notes": "干桂花"},
        {"name": "水", "quantity": 500, "unit": "g", "notes": "煮红豆汤"},
        {"name": "代糖", "quantity": 3, "unit": "g", "notes": "按口味调整"},
        {"name": "鸡蛋", "quantity": 2, "unit": "个", "notes": "厚蛋烧用"},
        {"name": "蛋清", "quantity": 1, "unit": "个", "notes": "增加蛋白质"},
        {"name": "西兰花碎", "quantity": 50, "unit": "g", "notes": "焯熟切碎"},
        {"name": "全麦吐司片", "quantity": 20, "unit": "g", "notes": "切小丁加入蛋液"},
        {"name": "低脂芝士片", "quantity": 10, "unit": "g", "notes": "切碎"},
        {"name": "盐", "quantity": 0.5, "unit": "g", "notes": ""},
        {"name": "油", "quantity": 3, "unit": "g", "notes": "煎厚蛋烧用"}
        ],
        "instructions": [
        {"step": 1, "description": "锅中加入水和红豆片煮开，小火煮至汤汁浓稠，加入代糖调味。"},
        {"step": 2, "description": "放入小圆子煮至浮起，关火后撒入桂花即成桂花圆子红豆汤。"},
        {"step": 3, "description": "鸡蛋与蛋清打散，加入西兰花碎、全麦吐司丁、芝士碎和少量盐拌匀。"},
        {"step": 4, "description": "小火少油倒入蛋液慢慢卷起，重复卷动直至成厚蛋卷，切段装盘。"},
        {"step": 5, "description": "红豆汤装碗，与蔬菜厚蛋烧一起食用。"}
        ],
        "nutrition": {"calories": 460, "protein": 22, "carbohydrate": 55, "fat": 14, "fiber": 7}
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
