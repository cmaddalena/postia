"""
Postia - Versión con diseño profesional restaurado
"""

from flask import Flask, request, jsonify, send_file, session, make_response
from flask_cors import CORS
import sqlite3
import hashlib
import os
import uuid
from datetime import datetime, timedelta
from openai import OpenAI

# Configurar OpenAI con cliente moderno
openai_client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Base de datos en memoria para simplicidad
DATABASE_PATH = 'postia_simple.db'

def init_db():
    """Inicializar base de datos simple"""
    conn = sqlite3.connect(DATABASE_PATH)
    
    # Crear tabla users
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE,
            password_hash TEXT,
            full_name TEXT,
            role TEXT,
            session_token TEXT
        )
    ''')
    
    # Crear tabla posts
    conn.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            title TEXT,
            content TEXT,
            platform TEXT,
            scheduled_date TEXT,
            status TEXT DEFAULT 'draft'
        )
    ''')
    
    # Crear usuarios si no existen
    users = [
        ('admin@maddalenamarketing.com', 'admin123', 'Charly Maddalena', 'admin'),
        ('cliente1@empresa.com', 'cliente123', 'Cliente Uno', 'client')
    ]
    
    for email, password, name, role in users:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        conn.execute('''
            INSERT OR IGNORE INTO users (email, password_hash, full_name, role)
            VALUES (?, ?, ?, ?)
        ''', (email, password_hash, name, role))
    
    conn.commit()
    conn.close()

def get_user_from_session():
    """Obtener usuario de la sesión"""
    token = request.cookies.get('session_token')
    if not token:
        return None
    
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT * FROM users WHERE session_token = ?', (token,)).fetchone()
    conn.close()
    return user

@app.route('/')
def index():
    """Página principal"""
    user = get_user_from_session()
    
    if user:
        # Dashboard profesional completo
        with open('dashboard_optimized.html', 'r', encoding='utf-8') as f:
            return f.read()
    
    # Login profesional
    with open('login_professional.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/login', methods=['POST'])
def login():
    """Login simple"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"success": False, "error": "Email y contraseña requeridos"}), 400
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        user = conn.execute(
            'SELECT * FROM users WHERE email = ? AND password_hash = ?', 
            (email, password_hash)
        ).fetchone()
        
        if not user:
            conn.close()
            return jsonify({"success": False, "error": "Credenciales incorrectas"}), 401
        
        # Crear sesión
        session_token = str(uuid.uuid4())
        conn.execute(
            'UPDATE users SET session_token = ? WHERE id = ?', 
            (session_token, user['id'])
        )
        conn.commit()
        conn.close()
        
        response = make_response(jsonify({"success": True, "message": "Login exitoso"}))
        response.set_cookie('session_token', session_token, max_age=7*24*60*60, httponly=True)
        
        return response
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout simple"""
    response = make_response(jsonify({"success": True}))
    response.set_cookie('session_token', '', expires=0)
    return response

@app.route('/api/generate-calendar', methods=['POST'])
def generate_calendar():
    """Generar calendario simple"""
    try:
        user = get_user_from_session()
        if not user:
            return jsonify({"success": False, "error": "No autenticado"}), 401
        
        data = request.json
        days = int(data.get('days', 7))
        posts_per_day = int(data.get('posts_per_day', 3))
        
        # Templates simples
        # Perfil del cliente personalizado
        client_profile = {
            'business_type': 'Marketing Digital para PyMEs',
            'target_audience': 'Pequeñas y medianas empresas',
            'tone': 'Profesional pero cercano',
            'topics': ['emprendimiento', 'marketing digital', 'productividad', 'crecimiento empresarial'],
            'platforms': ['instagram', 'linkedin']
        }
        
        # Temas trending y personalizados
        trending_topics = [
            'Inteligencia Artificial en negocios',
            'Marketing de contenidos 2025', 
            'Automatización de procesos',
            'Estrategias de crecimiento digital',
            'Productividad empresarial',
            'Tendencias de redes sociales',
            'E-commerce y ventas online',
            'Branding personal'
        ]
        
        content_types = ['image', 'carousel', 'video', 'text']
        optimal_times = {
            'instagram': ['09:00', '12:00', '18:00', '20:00'],
            'linkedin': ['08:00', '12:00', '17:00', '19:00']
        }
        
        conn = sqlite3.connect(DATABASE_PATH)
        
        # Limpiar posts anteriores
        conn.execute('DELETE FROM posts WHERE user_id = ?', (user['id'],))
        
        # Generar nuevos posts personalizados
        for day in range(days):
            for post_num in range(posts_per_day):
                current_date = datetime.now() + timedelta(days=day)
                date_str = current_date.strftime('%Y-%m-%d')
                
                # Seleccionar tema y plataforma
                topic = trending_topics[((day * posts_per_day) + post_num) % len(trending_topics)]
                platform = client_profile['platforms'][post_num % len(client_profile['platforms'])]
                content_type = content_types[post_num % len(content_types)]
                
                # Generar contenido personalizado
                if platform == 'instagram':
                    if 'marketing' in topic.lower():
                        title = f"💡 {topic}: Tips para PyMEs"
                        content = f"🚀 ¿Sabías que el {topic.lower()} puede transformar tu negocio?\n\n✅ Estrategias probadas para empresas como la tuya\n✅ Resultados medibles en 30 días\n✅ Sin complicaciones técnicas\n\n¿Cuál es tu mayor desafío en marketing digital? 👇"
                        hashtags = f"#pymes #marketing #emprendimiento #{topic.lower().replace(' ', '')}"
                    else:
                        title = f"🎯 {topic} para tu empresa"
                        content = f"📈 {topic} es clave para el crecimiento de tu PyME\n\n💪 Implementa estos cambios HOY:\n• Automatiza procesos repetitivos\n• Analiza tus métricas\n• Optimiza tu tiempo\n\n¿Qué herramienta usas para ser más productivo? 🤔"
                        hashtags = f"#productividad #negocios #pymes #{topic.lower().replace(' ', '')}"
                else:  # LinkedIn
                    title = f"{topic}: Estrategias para el crecimiento empresarial"
                    content = f"En el panorama empresarial actual, {topic.lower()} se ha convertido en un factor diferenciador para las PyMEs que buscan escalar.\n\nBasado en nuestra experiencia:\n\n🔹 Las empresas que implementan estas estrategias ven un crecimiento promedio del 40%\n🔹 El ROI se evidencia en los primeros 3 meses\n🔹 La implementación no requiere grandes inversiones\n\n¿Qué estrategias está implementando tu empresa?\n\n#Emprendimiento #Marketing #PyMEs"
                    hashtags = f"#emprendimiento #marketing #pymes #{topic.lower().replace(' ', '')}"
                
                # Horario óptimo
                time_slot = optimal_times[platform][post_num % len(optimal_times[platform])]
                
                conn.execute('''
                    INSERT INTO posts (user_id, title, content, platform, content_type, 
                                     scheduled_date, scheduled_time, hashtags, platforms, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user['id'], title, content, platform, content_type, date_str, time_slot, hashtags, platform, 'draft'))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Se generaron {days * posts_per_day} posts exitosamente"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Obtener posts"""
    try:
        user = get_user_from_session()
        if not user:
            return jsonify({"success": False, "error": "No autenticado"}), 401
        
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        posts = conn.execute(
            'SELECT * FROM posts WHERE user_id = ? ORDER BY scheduled_date DESC', 
            (user['id'],)
        ).fetchall()
        conn.close()
        
        posts_list = [dict(post) for post in posts]
        
        return jsonify({
            "success": True,
            "posts": posts_list
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """Actualizar un post específico"""
    try:
        user = get_user_from_session()
        if not user:
            return jsonify({"success": False, "error": "No autenticado"}), 401
        
        data = request.get_json()
        
        conn = sqlite3.connect(DATABASE_PATH)
        
        # Verificar que el post pertenece al usuario
        post = conn.execute(
            'SELECT * FROM posts WHERE id = ? AND user_id = ?',
            (post_id, user['id'])
        ).fetchone()
        
        if not post:
            conn.close()
            return jsonify({"success": False, "error": "Post no encontrado"}), 404
        
        # Actualizar el post
        conn.execute('''
            UPDATE posts SET 
                title = ?, content = ?, content_type = ?, hashtags = ?,
                scheduled_date = ?, scheduled_time = ?, platform = ?, media_files = ?
            WHERE id = ? AND user_id = ?
        ''', (
            data.get('title', ''),
            data.get('content', ''),
            data.get('content_type', 'image'),
            data.get('hashtags', ''),
            data.get('scheduled_date', ''),
            data.get('scheduled_time', ''),
            data.get('platforms', ['instagram'])[0] if data.get('platforms') else 'instagram',
            ','.join(data.get('media_files', [])) if data.get('media_files') else '',
            post_id,
            user['id']
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Post actualizado exitosamente"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Eliminar un post específico"""
    try:
        user = get_user_from_session()
        if not user:
            return jsonify({"success": False, "error": "No autenticado"}), 401
        
        conn = sqlite3.connect(DATABASE_PATH)
        
        # Verificar que el post pertenece al usuario
        post = conn.execute(
            'SELECT * FROM posts WHERE id = ? AND user_id = ?',
            (post_id, user['id'])
        ).fetchone()
        
        if not post:
            conn.close()
            return jsonify({"success": False, "error": "Post no encontrado"}), 404
        
        # Eliminar el post
        conn.execute('DELETE FROM posts WHERE id = ? AND user_id = ?', (post_id, user['id']))
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Post eliminado exitosamente"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/upload-image', methods=['POST'])
@app.route('/upload-image', methods=['POST'])
def upload_image():
    """Subir imagen al servidor"""
    try:
        user = get_user_from_session()
        if not user:
            return jsonify({"success": False, "error": "No autenticado"}), 401
        
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No se encontró archivo"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "No se seleccionó archivo"}), 400
        
        # Validar tipo de archivo
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
        file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_extension not in allowed_extensions:
            return jsonify({"success": False, "error": "Tipo de archivo no permitido"}), 400
        
        # Generar nombre único
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Crear directorio si no existe
        upload_dir = os.path.join(os.getcwd(), 'uploads', 'images')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Guardar archivo
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # URL relativa para el frontend
        file_url = f"/uploads/images/{unique_filename}"
        
        return jsonify({
            "success": True,
            "file_url": file_url,
            "filename": unique_filename,
            "original_name": file.filename
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/uploads/images/<filename>')
def serve_uploaded_file(filename):
    """Servir archivos subidos"""
    try:
        upload_dir = os.path.join(os.getcwd(), 'uploads', 'images')
        return send_file(os.path.join(upload_dir, filename))
    except Exception as e:
        return jsonify({"error": "Archivo no encontrado"}), 404

@app.route('/api/regenerate-copy', methods=['POST'])
def regenerate_copy():
    """Regenerar copy de un post usando IA real"""
    try:
        user = get_user_from_session()
        if not user:
            return jsonify({"success": False, "error": "No autenticado"}), 401
        
        data = request.get_json()
        post_id = data.get('post_id')
        platform = data.get('platform', 'instagram')
        content_type = data.get('content_type', 'image')
        current_content = data.get('current_content', '')
        current_title = data.get('current_title', '')
        
        # Configuración del perfil del cliente
        client_profile = {
            'business_type': 'Marketing Digital para PyMEs',
            'target_audience': 'Pequeñas y medianas empresas',
            'tone': 'Profesional pero cercano',
            'industry': 'Marketing y consultoría'
        }
        
        # Prompt personalizado según plataforma
        if platform == 'instagram':
            prompt = f"""
            Eres un experto en marketing digital especializado en PyMEs. Genera un post para Instagram que:
            
            PERFIL DEL CLIENTE:
            - Negocio: {client_profile['business_type']}
            - Audiencia: {client_profile['target_audience']}
            - Tono: {client_profile['tone']}
            
            TÍTULO DEL POST: {current_title}
            CONTENIDO ACTUAL: {current_content}
            
            INSTRUCCIONES:
            - Mejora el contenido manteniendo el tema del título
            - Usa emojis estratégicamente (máximo 5)
            - Incluye una pregunta para generar engagement
            - Máximo 150 palabras
            - Tono profesional pero cercano
            - Enfócate en valor para PyMEs
            - Mantén coherencia con el título proporcionado
            
            Genera SOLO el texto del post, sin hashtags ni explicaciones adicionales.
            """
        else:  # LinkedIn
            prompt = f"""
            Eres un consultor en marketing digital para PyMEs. Genera un post profesional para LinkedIn que:
            
            PERFIL DEL CLIENTE:
            - Negocio: {client_profile['business_type']}
            - Audiencia: {client_profile['target_audience']}
            - Tono: {client_profile['tone']}
            
            TÍTULO DEL POST: {current_title}
            CONTENIDO ACTUAL: {current_content}
            
            INSTRUCCIONES:
            - Mejora el contenido con un enfoque más profesional
            - Mantén coherencia con el título proporcionado
            - Incluye insights o estadísticas relevantes
            - Termina con una pregunta para fomentar networking
            - Máximo 200 palabras
            - Sin emojis o muy pocos
            - Enfócate en crecimiento empresarial
            
            Genera SOLO el texto del post, sin hashtags ni explicaciones adicionales.
            """
        
        # Llamada a OpenAI con cliente moderno
        response = openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Eres un experto en marketing digital especializado en crear contenido para PyMEs."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        new_content = response.choices[0].message.content.strip()
        
        # Generar hashtags personalizados
        hashtag_prompt = f"""
        Basándote en este contenido para {platform}: "{new_content}"
        
        Genera hashtags relevantes para una empresa de marketing digital que atiende PyMEs:
        - Para Instagram: 8-10 hashtags mezclando populares y nicho
        - Para LinkedIn: 3-5 hashtags profesionales
        
        Responde SOLO con los hashtags separados por espacios, empezando cada uno con #
        """
        
        hashtag_response = openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "user", "content": hashtag_prompt}
            ],
            max_tokens=100,
            temperature=0.5
        )
        
        new_hashtags = hashtag_response.choices[0].message.content.strip()
        
        return jsonify({
            "success": True,
            "new_content": new_content,
            "new_hashtags": new_hashtags,
            "message": "Copy regenerado con IA exitosamente"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error al regenerar copy: {str(e)}"}), 500

@app.route('/api/approve-all', methods=['POST'])
def approve_all():
    """Aprobar todos los posts"""
    try:
        user = get_user_from_session()
        if not user:
            return jsonify({"success": False, "error": "No autenticado"}), 401
        
        conn = sqlite3.connect(DATABASE_PATH)
        result = conn.execute(
            'UPDATE posts SET status = "approved" WHERE user_id = ? AND status = "draft"',
            (user['id'],)
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Se aprobaron {result.rowcount} posts"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Inicializar BD
init_db()

if __name__ == '__main__':
    print("🚀 Iniciando Postia Profesional...")
    app.run(host='0.0.0.0', port=5000, debug=False)

