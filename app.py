#!/usr/bin/env python3
"""
Breakfast Decision Web Application
- Draw random dishes with weighted probability based on rating
- View ingredients needed for tomorrow's meal
- Rate dishes to influence future selections
- Redraw until you find something you like
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sqlite3
import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'breakfast.db')


def get_db_connection():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_tomorrow_date():
    """Get tomorrow's date string."""
    return (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/api/recipes', methods=['GET'])
def get_all_recipes():
    """Get all recipes with their ratings."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT r.*, n.calories, n.protein, n.carbohydrate, n.fat, n.fiber
        FROM recipes r
        LEFT JOIN nutrition n ON r.id = n.recipe_id
        ORDER BY r.user_rating DESC
    ''')
    recipes = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(recipes)


@app.route('/api/draw', methods=['GET'])
def draw_dish():
    """Draw a random dish weighted by user rating."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all recipes with their ratings
    cursor.execute('''
        SELECT r.*, n.calories, n.protein, n.carbohydrate, n.fat, n.fiber
        FROM recipes r
        LEFT JOIN nutrition n ON r.id = n.recipe_id
    ''')
    recipes = [dict(row) for row in cursor.fetchall()]
    
    if not recipes:
        conn.close()
        return jsonify({'error': 'No recipes available'}), 404
    
    # Weighted random selection based on rating (rating^2 for stronger effect)
    weights = [(r['user_rating'] or 3.0) ** 2 for r in recipes]
    total_weight = sum(weights)
    weights = [w / total_weight for w in weights]
    
    selected = random.choices(recipes, weights=weights, k=1)[0]
    
    # Get ingredients for the selected recipe
    cursor.execute('''
        SELECT ingredient_name, quantity, unit, notes
        FROM ingredients
        WHERE recipe_id = ?
    ''', (selected['id'],))
    ingredients = [dict(row) for row in cursor.fetchall()]
    
    # Get instructions
    cursor.execute('''
        SELECT step_number, instruction
        FROM instructions
        WHERE recipe_id = ?
        ORDER BY step_number
    ''', (selected['id'],))
    instructions = [dict(row) for row in cursor.fetchall()]
    
    # Update times_drawn
    cursor.execute('''
        UPDATE recipes SET times_drawn = times_drawn + 1 WHERE id = ?
    ''', (selected['id'],))
    conn.commit()
    
    selected['ingredients'] = ingredients
    selected['instructions'] = instructions
    
    conn.close()
    return jsonify(selected)


@app.route('/api/draw/tomorrow', methods=['GET'])
def draw_for_tomorrow():
    """Draw a dish for tomorrow and save it."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    tomorrow = get_tomorrow_date()
    
    # Check if already have a confirmed dish for tomorrow
    cursor.execute('''
        SELECT r.*, n.calories, n.protein, n.carbohydrate, n.fat, n.fiber, dh.id as history_id
        FROM draw_history dh
        JOIN recipes r ON dh.recipe_id = r.id
        LEFT JOIN nutrition n ON r.id = n.recipe_id
        WHERE dh.draw_date = ? AND dh.confirmed = 1
    ''', (tomorrow,))
    
    existing = cursor.fetchone()
    if existing:
        result = dict(existing)
        # Get ingredients
        cursor.execute('''
            SELECT ingredient_name, quantity, unit, notes
            FROM ingredients WHERE recipe_id = ?
        ''', (result['id'],))
        result['ingredients'] = [dict(row) for row in cursor.fetchall()]
        
        # Get instructions
        cursor.execute('''
            SELECT step_number, instruction
            FROM instructions WHERE recipe_id = ?
            ORDER BY step_number
        ''', (result['id'],))
        result['instructions'] = [dict(row) for row in cursor.fetchall()]
        
        result['already_confirmed'] = True
        conn.close()
        return jsonify(result)
    
    # Draw a new dish
    cursor.execute('''
        SELECT r.*, n.calories, n.protein, n.carbohydrate, n.fat, n.fiber
        FROM recipes r
        LEFT JOIN nutrition n ON r.id = n.recipe_id
    ''')
    recipes = [dict(row) for row in cursor.fetchall()]
    
    if not recipes:
        conn.close()
        return jsonify({'error': 'No recipes available'}), 404
    
    # Weighted random selection
    weights = [(r['user_rating'] or 3.0) ** 2 for r in recipes]
    total_weight = sum(weights)
    weights = [w / total_weight for w in weights]
    
    selected = random.choices(recipes, weights=weights, k=1)[0]
    
    # Get ingredients
    cursor.execute('''
        SELECT ingredient_name, quantity, unit, notes
        FROM ingredients WHERE recipe_id = ?
    ''', (selected['id'],))
    selected['ingredients'] = [dict(row) for row in cursor.fetchall()]
    
    # Get instructions
    cursor.execute('''
        SELECT step_number, instruction
        FROM instructions WHERE recipe_id = ?
        ORDER BY step_number
    ''', (selected['id'],))
    selected['instructions'] = [dict(row) for row in cursor.fetchall()]
    
    selected['already_confirmed'] = False
    selected['draw_date'] = tomorrow
    
    conn.close()
    return jsonify(selected)


@app.route('/api/confirm/<int:recipe_id>', methods=['POST'])
def confirm_dish(recipe_id):
    """Confirm a dish for tomorrow."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    tomorrow = get_tomorrow_date()
    
    # Remove any existing unconfirmed draws for tomorrow
    cursor.execute('''
        DELETE FROM draw_history WHERE draw_date = ? AND confirmed = 0
    ''', (tomorrow,))
    
    # Insert the confirmed dish
    cursor.execute('''
        INSERT INTO draw_history (recipe_id, draw_date, confirmed)
        VALUES (?, ?, 1)
    ''', (recipe_id, tomorrow))
    
    # Update times_drawn
    cursor.execute('''
        UPDATE recipes SET times_drawn = times_drawn + 1 WHERE id = ?
    ''', (recipe_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Dish confirmed for tomorrow!'})


@app.route('/api/rate/<int:recipe_id>', methods=['POST'])
def rate_dish(recipe_id):
    """Rate a dish (1-5 stars)."""
    data = request.get_json()
    rating = data.get('rating', 3)
    
    # Validate rating
    rating = max(1, min(5, float(rating)))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get current rating and update with weighted average
    cursor.execute('SELECT user_rating, times_drawn FROM recipes WHERE id = ?', (recipe_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return jsonify({'error': 'Recipe not found'}), 404
    
    current_rating = result['user_rating'] or 3.0
    times_drawn = result['times_drawn'] or 1
    
    # Weighted average: give more weight to recent ratings
    new_rating = (current_rating * 0.7 + rating * 0.3)
    
    cursor.execute('''
        UPDATE recipes SET user_rating = ? WHERE id = ?
    ''', (round(new_rating, 2), recipe_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True, 
        'new_rating': round(new_rating, 2),
        'message': f'Rating updated to {round(new_rating, 2)}'
    })


@app.route('/api/recipe/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """Get a specific recipe with all details."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT r.*, n.calories, n.protein, n.carbohydrate, n.fat, n.fiber
        FROM recipes r
        LEFT JOIN nutrition n ON r.id = n.recipe_id
        WHERE r.id = ?
    ''', (recipe_id,))
    
    recipe = cursor.fetchone()
    if not recipe:
        conn.close()
        return jsonify({'error': 'Recipe not found'}), 404
    
    result = dict(recipe)
    
    # Get ingredients
    cursor.execute('''
        SELECT ingredient_name, quantity, unit, notes
        FROM ingredients WHERE recipe_id = ?
    ''', (recipe_id,))
    result['ingredients'] = [dict(row) for row in cursor.fetchall()]
    
    # Get instructions
    cursor.execute('''
        SELECT step_number, instruction
        FROM instructions WHERE recipe_id = ?
        ORDER BY step_number
    ''', (recipe_id,))
    result['instructions'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(result)


@app.route('/health')
def health_check():
    """Lightweight health check for deployment."""
    return jsonify({'status': 'healthy', 'time': datetime.now().isoformat()}), 200

@app.route('/api/tomorrow', methods=['GET'])
def get_tomorrow_meal():
    """Get the confirmed meal for tomorrow."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    tomorrow = get_tomorrow_date()
    
    cursor.execute('''
        SELECT r.*, n.calories, n.protein, n.carbohydrate, n.fat, n.fiber
        FROM draw_history dh
        JOIN recipes r ON dh.recipe_id = r.id
        LEFT JOIN nutrition n ON r.id = n.recipe_id
        WHERE dh.draw_date = ? AND dh.confirmed = 1
    ''', (tomorrow,))
    
    result = cursor.fetchone()
    if not result:
        conn.close()
        return jsonify({'confirmed': False, 'message': 'No meal confirmed for tomorrow yet'})
    
    meal = dict(result)
    
    # Get ingredients
    cursor.execute('''
        SELECT ingredient_name, quantity, unit, notes
        FROM ingredients WHERE recipe_id = ?
    ''', (meal['id'],))
    meal['ingredients'] = [dict(row) for row in cursor.fetchall()]
    
    # Get instructions
    cursor.execute('''
        SELECT step_number, instruction
        FROM instructions WHERE recipe_id = ?
        ORDER BY step_number
    ''', (meal['id'],))
    meal['instructions'] = [dict(row) for row in cursor.fetchall()]
    
    meal['confirmed'] = True
    
    conn.close()
    return jsonify(meal)


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get draw history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT dh.*, r.recipe_name, r.recipe_name_en, r.user_rating
        FROM draw_history dh
        JOIN recipes r ON dh.recipe_id = r.id
        ORDER BY dh.draw_date DESC
        LIMIT 30
    ''')
    
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(history)


# ======================
# AI Assistant Endpoints
# ======================

@app.route('/api/ai/help', methods=['POST'])
def ai_help():
    """Get AI help for cooking."""
    try:
        from ai_assistant import get_cooking_help
        
        data = request.get_json()
        recipe_name = data.get('recipe_name', '')
        recipe_steps = data.get('steps', [])
        question = data.get('question', '')
        ingredients = data.get('ingredients', [])
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        response = get_cooking_help(recipe_name, recipe_steps, question, ingredients)
        return jsonify({'response': response})
        
    except Exception as e:
        return jsonify({'error': str(e), 'response': '抱歉，AI助手暂时无法使用。请稍后再试。'}), 500


@app.route('/api/ai/step/<int:recipe_id>/<int:step_number>', methods=['GET'])
def ai_step_explanation(recipe_id, step_number):
    """Get detailed explanation for a cooking step."""
    try:
        from ai_assistant import get_step_explanation
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT recipe_name FROM recipes WHERE id = ?', (recipe_id,))
        recipe = cursor.fetchone()
        
        cursor.execute('''
            SELECT instruction FROM instructions 
            WHERE recipe_id = ? AND step_number = ?
        ''', (recipe_id, step_number))
        step = cursor.fetchone()
        
        conn.close()
        
        if not recipe or not step:
            return jsonify({'error': 'Recipe or step not found'}), 404
        
        explanation = get_step_explanation(
            recipe['recipe_name'], 
            step_number, 
            step['instruction']
        )
        return jsonify({'explanation': explanation})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/ingredient/<ingredient_name>', methods=['GET'])
def ai_ingredient_tips(ingredient_name):
    """Get tips for an ingredient."""
    try:
        from ai_assistant import get_ingredient_tips
        tips = get_ingredient_tips(ingredient_name)
        return jsonify({'tips': tips})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/upload-recipe', methods=['POST'])
def upload_recipe_image():
    """Upload an image and extract recipe data using AI."""
    try:
        from ai_assistant import extract_recipe_from_image, insert_recipe_to_db
        
        data = request.get_json()
        image_base64 = data.get('image')
        
        if not image_base64:
            return jsonify({'success': False, 'error': '未提供图片'}), 400
        
        # Remove data URL prefix if present
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]
        
        # Extract recipe from image
        recipe_data = extract_recipe_from_image(image_base64)
        
        if not recipe_data.get('success', False):
            return jsonify(recipe_data), 400
        
        # Insert into database
        insert_result = insert_recipe_to_db(recipe_data)
        
        if not insert_result.get('success', False):
            return jsonify(insert_result), 500
        
        # Get the full recipe data to return
        conn = get_db_connection()
        cursor = conn.cursor()
        
        recipe_id = insert_result['recipe_id']
        
        cursor.execute('''
            SELECT r.*, n.calories, n.protein, n.carbohydrate, n.fat, n.fiber
            FROM recipes r
            LEFT JOIN nutrition n ON r.id = n.recipe_id
            WHERE r.id = ?
        ''', (recipe_id,))
        
        recipe = dict(cursor.fetchone())
        
        cursor.execute('''
            SELECT ingredient_name, quantity, unit, notes
            FROM ingredients WHERE recipe_id = ?
        ''', (recipe_id,))
        recipe['ingredients'] = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute('''
            SELECT step_number, instruction
            FROM instructions WHERE recipe_id = ?
            ORDER BY step_number
        ''', (recipe_id,))
        recipe['instructions'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': insert_result['message'],
            'recipe': recipe
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai/generate-recipe', methods=['POST'])
def generate_recipe():
    """Generate a recipe from dish name using AI."""
    try:
        from ai_assistant import generate_recipe_from_name, insert_recipe_to_db
        
        data = request.get_json()
        dish_name = data.get('dish_name', '').strip()
        
        if not dish_name:
            return jsonify({'success': False, 'error': '请提供菜品名称'}), 400
        
        # Generate recipe
        recipe_data = generate_recipe_from_name(dish_name)
        
        if not recipe_data.get('success', False):
            return jsonify(recipe_data), 400
        
        # Insert into database
        insert_result = insert_recipe_to_db(recipe_data)
        
        if not insert_result.get('success', False):
            return jsonify(insert_result), 500
        
        # Get the full recipe data to return
        conn = get_db_connection()
        cursor = conn.cursor()
        
        recipe_id = insert_result['recipe_id']
        
        cursor.execute('''
            SELECT r.*, n.calories, n.protein, n.carbohydrate, n.fat, n.fiber
            FROM recipes r
            LEFT JOIN nutrition n ON r.id = n.recipe_id
            WHERE r.id = ?
        ''', (recipe_id,))
        
        recipe = dict(cursor.fetchone())
        
        cursor.execute('''
            SELECT ingredient_name, quantity, unit, notes
            FROM ingredients WHERE recipe_id = ?
        ''', (recipe_id,))
        recipe['ingredients'] = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute('''
            SELECT step_number, instruction
            FROM instructions WHERE recipe_id = ?
            ORDER BY step_number
        ''', (recipe_id,))
        recipe['instructions'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': insert_result['message'],
            'recipe': recipe
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print("⚠️  Database not found. Please run init_db.py first!")
        exit(1)
    
    print("🍳 Starting Breakfast Decision System...")
    print("📍 Open http://localhost:5000 in your browser")
    print("📱 Phone Access: http://<your-ip-address>:5000")
    # Host 0.0.0.0 is crucial for network access
    app.run(host='0.0.0.0', debug=True, port=5000)
