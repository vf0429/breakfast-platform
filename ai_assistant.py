#!/usr/bin/env python3
"""
AI Cooking Assistant using Perplexity API (with OpenAI fallback).
Provides help with cooking steps, ingredient substitutions, and tips.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def get_perplexity_client():
    """
    Get Perplexity client.
    Note: Perplexity API is compatible with OpenAI SDK, so we use the 'openai' library.
    This does NOT require an OpenAI account, just the library.
    """
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key or api_key.startswith('pplx-your'):
        return None
    
    try:
        from openai import OpenAI
        return OpenAI(
            api_key=api_key,
            base_url="https://api.perplexity.ai"
        )
    except ImportError:
        print("❌ 错误: 未安装 'openai' 库。请运行: pip install openai")
        return None


def get_openai_client():
    """Get OpenAI client (for vision tasks)."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key.startswith('sk-your'):
        return None
    
    try:
        from openai import OpenAI
        return OpenAI(api_key=api_key)
    except ImportError:
        return None


def get_ai_client():
    """Get the best available AI client (Perplexity first, then OpenAI)."""
    client = get_perplexity_client()
    if client:
        return client, "perplexity"
    
    client = get_openai_client()
    if client:
        return client, "openai"
    
    return None, None


def get_cooking_help(recipe_name, recipe_steps, user_question, ingredients=None):
    """
    Get AI assistance for cooking.
    
    Args:
        recipe_name: Name of the dish
        recipe_steps: List of cooking steps
        user_question: User's question
        ingredients: Optional list of ingredients
    
    Returns:
        AI response string
    """
    client, provider = get_ai_client()
    
    if not client:
        return get_fallback_response(user_question)
    
    steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(recipe_steps)])
    ingredients_text = ", ".join(ingredients) if ingredients else "未提供"
    
    system_prompt = """你是一位专业的中式早餐烹饪助手，热情友好，擅长用简单易懂的语言解释复杂的烹饪技巧。

你的职责是:
1. 帮助用户理解烹饪步骤
2. 提供实用的烹饪技巧和窍门
3. 建议食材替代方案
4. 解答烹饪相关问题
5. 鼓励用户并给予信心

请用简洁、友好的中文回答，可以适当使用emoji让回复更生动。如果用户问的问题与烹饪无关，礼貌地引导回烹饪话题。"""

    user_prompt = f"""当前菜品: {recipe_name}

食材: {ingredients_text}

烹饪步骤:
{steps_text}

用户问题: {user_question}

请针对用户的问题提供帮助。"""

    try:
        # Choose model based on provider
        if provider == "perplexity":
            model = "sonar-pro"
        else:
            model = "gpt-4o-mini"
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"AI API error ({provider}): {e}")
        return get_fallback_response(user_question)


def get_fallback_response(question):
    """Provide fallback responses when AI is unavailable."""
    question_lower = question.lower()
    
    responses = {
        "火候": "🔥 一般来说:\n• 大火用于快速炒制和煮沸\n• 中火用于煎蛋和普通烹饪\n• 小火用于熬粥和慢炖\n\n如果不确定，从中火开始，根据情况调整。",
        
        "多久": "⏱️ 烹饪时间因食材和火力而异:\n• 煮蛋: 7-10分钟\n• 蒸蛋: 8-10分钟\n• 蒸玉米: 15-20分钟\n• 煮粥: 20-30分钟\n\n观察食物状态是最好的判断方式！",
        
        "替代": "🔄 常见替代:\n• 没有橄榄油 → 用植物油\n• 没有牛油果 → 用香蕉或鸡蛋\n• 没有燕麦 → 用小米或大米\n• 没有酸奶 → 用牛奶\n\n创意烹饪，灵活变通！",
        
        "熟": "✅ 判断熟度:\n• 鸡蛋: 蛋白凝固，蛋黄看个人喜好\n• 鸡肉: 切开无粉红色，肉汁清澈\n• 玉米: 颜色变深，有香气\n• 红薯: 筷子能轻松插入\n\n安全第一！",
        
        "失败": "💪 别灰心！烹饪是练习的过程:\n• 糊了 → 下次火小一点\n• 太淡 → 加点盐调味\n• 太咸 → 加点水或配着淡的食物吃\n\n每次失败都是进步的机会！",
    }
    
    for keyword, response in responses.items():
        if keyword in question_lower:
            return response
    
    return """🤔 这是个好问题！
    
一些通用建议:
1. 仔细阅读步骤，不着急
2. 提前准备好所有食材
3. 从简单的菜开始练习
4. 多尝试，不怕失败

如果有具体问题，欢迎继续问我！😊

提示: 配置 Perplexity 或 OpenAI API key 可以获得更智能的回答哦！"""


def get_step_explanation(recipe_name, step_number, step_text):
    """Get detailed explanation for a specific cooking step."""
    client, provider = get_ai_client()
    
    if not client:
        return f"📝 步骤 {step_number}: {step_text}\n\n💡 提示: 按照步骤操作，注意火候和时间。如需更详细帮助，请配置 API。"
    
    try:
        # Choose model based on provider
        if provider == "perplexity":
            model = "sonar-pro"
        else:
            model = "gpt-4o-mini"
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system", 
                    "content": "你是一位耐心的烹饪导师。请用简单易懂的语言详细解释烹饪步骤，包括具体操作、注意事项和常见错误。使用emoji让解释更生动。"
                },
                {
                    "role": "user", 
                    "content": f"请详细解释这个烹饪步骤:\n\n菜品: {recipe_name}\n步骤 {step_number}: {step_text}\n\n请包括: 具体怎么操作、要注意什么、常见问题及解决方法。"
                }
            ],
            max_tokens=400,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"📝 步骤 {step_number}: {step_text}\n\n抱歉，暂时无法获取详细解释。请按照步骤操作即可。"


def get_ingredient_tips(ingredient_name):
    """Get tips for selecting and preparing an ingredient."""
    client, provider = get_ai_client()
    
    tips = {
        "鸡蛋": "🥚 鸡蛋选购技巧:\n• 新鲜鸡蛋放水中会沉底\n• 壳面粗糙的更新鲜\n• 冷藏保存，大头朝上",
        "红薯": "🍠 红薯选购技巧:\n• 选择表皮光滑无斑点的\n• 中等大小的口感更好\n• 存放在阴凉通风处",
        "玉米": "🌽 玉米选购技巧:\n• 选择颗粒饱满的\n• 按压有弹性的更新鲜\n• 叶子青绿的更嫩",
    }
    
    if ingredient_name in tips:
        return tips[ingredient_name]
    
    if not client:
        return f"💡 {ingredient_name}: 选择新鲜的，储存在适当条件下。"
    
    try:
        # Choose model based on provider
        if provider == "perplexity":
            model = "sonar-pro"
        else:
            model = "gpt-4o-mini"
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system", 
                    "content": "你是食材专家。简洁地提供食材的选购和保存技巧，使用emoji。"
                },
                {
                    "role": "user", 
                    "content": f"请提供 {ingredient_name} 的选购和保存技巧（50字以内）"
                }
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"💡 {ingredient_name}: 选择新鲜的食材，注意保存条件。"


def extract_recipe_from_image(image_base64):
    """
    Extract recipe information from an image using OpenAI Vision.
    
    Args:
        image_base64: Base64 encoded image data
    
    Returns:
        Dictionary with recipe data or error message
    """
    # Vision requires OpenAI - Perplexity doesn't support image analysis
    client = get_openai_client()
    
    if not client:
        # Perplexity does not support vision/image analysis
        perplexity_client = get_perplexity_client()
        if perplexity_client:
            return {
                "success": False,
                "error": "图片识别需要 OpenAI API。\n\n💡 但您可以描述菜品名称，我会帮您生成食谱！\n\n请在对话框中输入菜品名称，例如：'帮我生成番茄炒蛋的食谱'"
            }
        return {
            "success": False,
            "error": "图片识别需要 OpenAI API。请在 .env 文件中设置 OPENAI_API_KEY。"
        }
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """你是一个专业的食谱识别助手。分析图片中的食谱信息，提取以下内容并以JSON格式返回：

{
    "recipe_name": "菜品中文名",
    "recipe_name_en": "English Name",
    "category": "分类（蛋白质/粗粮谷物/蔬菜/饮品）",
    "difficulty": 1-3的数字（1简单，2中等，3复杂）,
    "cooking_time": 烹饪时间（分钟，数字）,
    "ingredients": [
        {"name": "食材名", "quantity": 数量, "unit": "单位", "notes": "备注"}
    ],
    "instructions": [
        {"step": 1, "description": "步骤描述"}
    ],
    "nutrition": {
        "calories": 热量数字,
        "protein": 蛋白质克数,
        "carbohydrate": 碳水克数,
        "fat": 脂肪克数,
        "fiber": 纤维克数
    }
}

如果图片不包含食谱信息，返回：{"success": false, "error": "无法识别食谱信息"}
如果某些信息无法确定，使用合理的估计值。
只返回JSON，不要其他文字。"""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "请分析这张图片中的食谱信息，提取菜名、食材、步骤等，并以JSON格式返回。"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1500
        )
        
        result_text = response.choices[0].message.content
        
        # Clean up the response - remove markdown code blocks if present
        if result_text.startswith("```"):
            lines = result_text.split("\n")
            result_text = "\n".join(lines[1:-1])
        
        import json
        recipe_data = json.loads(result_text)
        
        if "error" in recipe_data:
            return {"success": False, "error": recipe_data["error"]}
        
        recipe_data["success"] = True
        return recipe_data
        
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"无法解析AI返回的数据: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"识别失败: {str(e)}"
        }


def insert_recipe_to_db(recipe_data):
    """
    Insert extracted recipe data into the database.
    
    Args:
        recipe_data: Dictionary with recipe information
    
    Returns:
        Dictionary with success status and recipe id
    """
    import sqlite3
    
    db_path = os.path.join(os.path.dirname(__file__), 'breakfast.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Insert recipe
        cursor.execute('''
            INSERT INTO recipes (recipe_name, recipe_name_en, category, difficulty, 
                cooking_time, user_rating)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            recipe_data.get('recipe_name', '未命名'),
            recipe_data.get('recipe_name_en', ''),
            recipe_data.get('category', '其他'),
            recipe_data.get('difficulty', 1),
            recipe_data.get('cooking_time', 10),
            3.0
        ))
        recipe_id = cursor.lastrowid
        
        # Insert ingredients
        for ing in recipe_data.get('ingredients', []):
            cursor.execute('''
                INSERT INTO ingredients (recipe_id, ingredient_name, quantity, unit, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                recipe_id,
                ing.get('name', ''),
                ing.get('quantity', 0),
                ing.get('unit', ''),
                ing.get('notes', '')
            ))
        
        # Insert instructions
        for inst in recipe_data.get('instructions', []):
            cursor.execute('''
                INSERT INTO instructions (recipe_id, step_number, instruction)
                VALUES (?, ?, ?)
            ''', (
                recipe_id,
                inst.get('step', 1),
                inst.get('description', '')
            ))
        
        # Insert nutrition
        nutr = recipe_data.get('nutrition', {})
        cursor.execute('''
            INSERT INTO nutrition (recipe_id, calories, protein, carbohydrate, fat, fiber)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            recipe_id,
            nutr.get('calories', 0),
            nutr.get('protein', 0),
            nutr.get('carbohydrate', 0),
            nutr.get('fat', 0),
            nutr.get('fiber', 0)
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "recipe_id": recipe_id,
            "message": f"✅ 成功添加食谱: {recipe_data.get('recipe_name', '未命名')}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"数据库插入失败: {str(e)}"
        }


def generate_recipe_from_name(dish_name):
    """
    Generate a complete recipe from just a dish name using AI.
    Works with both Perplexity and OpenAI.
    
    Args:
        dish_name: Name of the dish to generate recipe for
    
    Returns:
        Dictionary with recipe data or error message
    """
    client, provider = get_ai_client()
    
    if not client:
        return {
            "success": False,
            "error": "AI API 未配置。请在 .env 文件中设置 PERPLEXITY_API_KEY 或 OPENAI_API_KEY。"
        }
    
    system_prompt = """你是一个专业的食谱生成助手。根据用户提供的菜品名称，生成完整的食谱信息，以JSON格式返回：

{
    "recipe_name": "菜品中文名",
    "recipe_name_en": "English Name",
    "category": "分类（蛋白质/粗粮谷物/蔬菜/饮品）",
    "difficulty": 1-3的数字（1简单，2中等，3复杂）,
    "cooking_time": 烹饪时间（分钟，数字）,
    "ingredients": [
        {"name": "食材名", "quantity": 数量, "unit": "单位", "notes": "备注"}
    ],
    "instructions": [
        {"step": 1, "description": "步骤描述"}
    ],
    "nutrition": {
        "calories": 热量数字,
        "protein": 蛋白质克数,
        "carbohydrate": 碳水克数,
        "fat": 脂肪克数,
        "fiber": 纤维克数
    }
}

请生成适合早餐的健康食谱。只返回JSON，不要其他文字。"""

    try:
        # Choose model based on provider
        if provider == "perplexity":
            model = "sonar-pro"
        else:
            model = "gpt-4o-mini"
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f'请为"{dish_name}"生成完整的早餐食谱，包括食材、步骤和营养信息。'}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        result_text = response.choices[0].message.content
        
        # Clean up the response - remove markdown code blocks if present
        if "```" in result_text:
            import re
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', result_text)
            if json_match:
                result_text = json_match.group(1)
        
        try:
            import json
            recipe_data = json.loads(result_text.strip())
            recipe_data["success"] = True
            return recipe_data
        except json.JSONDecodeError as je:
            print(f"JSON Parse Error: {je}")
            print(f"Raw Text: {result_text}")
            return {
                "success": False,
                "error": f"生成食谱失败(JSON解析错误). 请重试。"
            }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"生成食谱失败: {str(e)}"
        }
