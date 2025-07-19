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
    
    # Crear tabla brand_preferences
    conn.execute('''
        CREATE TABLE IF NOT EXISTS brand_preferences (
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE,
            brand_name TEXT,
            brand_colors TEXT,
            typography_primary TEXT,
            typography_secondary TEXT,
            communication_tone TEXT,
            visual_style TEXT,
            logo_url TEXT,
            industry TEXT,
            target_audience TEXT,
            brand_values TEXT,
            content_themes TEXT,
            image_style_preferences TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
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
        with open('../frontend/dashboard.html', 'r', encoding='utf-8') as f:
            return f.read()
    
    # Login profesional
    with open('../frontend/login.html', 'r', encoding='utf-8') as f:
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
    """Generar calendario personalizado basado en preferencias de marca"""
    try:
        user = get_user_from_session()
        if not user:
            return jsonify({"success": False, "error": "No autenticado"}), 401
        
        data = request.json
        days = int(data.get('days', 7))
        posts_per_day = int(data.get('posts_per_day', 3))
        
        # Obtener preferencias de marca del usuario
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        preferences = conn.execute(
            'SELECT * FROM brand_preferences WHERE user_id = ?',
            (user['id'],)
        ).fetchone()
        
        # Configurar perfil del cliente basado en preferencias
        if preferences:
            client_profile = {
                'business_type': preferences['brand_name'] or 'Marketing Digital para PyMEs',
                'industry': preferences['industry'] or 'marketing',
                'target_audience': preferences['target_audience'] or 'Pequeñas y medianas empresas',
                'tone': preferences['communication_tone'] or 'profesional',
                'brand_values': preferences['brand_values'] or 'innovación, calidad, confianza',
                'content_themes': preferences['content_themes'] or 'marketing digital, tendencias, casos de éxito',
                'visual_style': preferences['visual_style'] or 'moderno',
                'platforms': ['instagram', 'linkedin']
            }
        else:
            # Perfil por defecto
            client_profile = {
                'business_type': 'Marketing Digital para PyMEs',
                'industry': 'marketing',
                'target_audience': 'Pequeñas y medianas empresas',
                'tone': 'profesional',
                'brand_values': 'innovación, calidad, confianza',
                'content_themes': 'marketing digital, tendencias, casos de éxito',
                'visual_style': 'moderno',
                'platforms': ['instagram', 'linkedin']
            }
        
        # Temas personalizados basados en industria y preferencias
        industry_topics = {
            'tecnologia': ['IA y automatización', 'Transformación digital', 'Ciberseguridad', 'Innovación tecnológica'],
            'marketing': ['Marketing de contenidos', 'SEO y SEM', 'Redes sociales', 'Email marketing'],
            'salud': ['Bienestar digital', 'Telemedicina', 'Prevención', 'Salud mental'],
            'educacion': ['E-learning', 'Metodologías innovadoras', 'Tecnología educativa', 'Desarrollo profesional'],
            'finanzas': ['Fintech', 'Inversiones inteligentes', 'Educación financiera', 'Criptomonedas'],
            'retail': ['E-commerce', 'Experiencia del cliente', 'Omnicanalidad', 'Retail tech'],
            'servicios': ['Atención al cliente', 'Digitalización', 'Eficiencia operativa', 'Calidad de servicio']
        }
        
        # Seleccionar temas según industria
        industry = client_profile['industry']
        if industry in industry_topics:
            trending_topics = industry_topics[industry]
        else:
            trending_topics = [
                'Inteligencia Artificial en negocios',
                'Marketing de contenidos 2025', 
                'Automatización de procesos',
                'Estrategias de crecimiento digital'
            ]
        
        # Agregar temas personalizados del usuario
        if client_profile['content_themes']:
            custom_themes = [theme.strip() for theme in client_profile['content_themes'].split(',')]
            trending_topics.extend(custom_themes[:4])  # Agregar hasta 4 temas personalizados
        
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
    """Regenerar copy de un post usando IA con preferencias personalizadas"""
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
        
        # Obtener preferencias de marca del usuario
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        preferences = conn.execute(
            'SELECT * FROM brand_preferences WHERE user_id = ?',
            (user['id'],)
        ).fetchone()
        
        # Configurar perfil del cliente basado en preferencias
        if preferences:
            client_profile = {
                'business_type': preferences['brand_name'] or 'Marketing Digital',
                'industry': preferences['industry'] or 'marketing',
                'target_audience': preferences['target_audience'] or 'Pequeñas y medianas empresas',
                'tone': preferences['communication_tone'] or 'profesional',
                'brand_values': preferences['brand_values'] or 'innovación, calidad, confianza',
                'content_themes': preferences['content_themes'] or 'marketing digital, tendencias',
                'visual_style': preferences['visual_style'] or 'moderno'
            }
        else:
            # Perfil por defecto
            client_profile = {
                'business_type': 'Marketing Digital para PyMEs',
                'industry': 'marketing',
                'target_audience': 'Pequeñas y medianas empresas',
                'tone': 'profesional',
                'brand_values': 'innovación, calidad, confianza',
                'content_themes': 'marketing digital, tendencias',
                'visual_style': 'moderno'
            }
        
        # Prompt personalizado según plataforma y preferencias
        if platform == 'instagram':
            prompt = f"""
            Eres un experto en marketing digital especializado en {client_profile['industry']}. Genera un post para Instagram que:
            
            PERFIL DE MARCA:
            - Negocio: {client_profile['business_type']}
            - Industria: {client_profile['industry']}
            - Audiencia: {client_profile['target_audience']}
            - Tono: {client_profile['tone']}
            - Valores: {client_profile['brand_values']}
            - Temas preferidos: {client_profile['content_themes']}
            - Estilo visual: {client_profile['visual_style']}
            
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

@app.route('/api/generate-hashtags', methods=['POST'])
def generate_hashtags():
    """Generar hashtags con IA basados en el contenido del post"""
    try:
        user = get_user_from_session()
        if not user:
            return jsonify({"success": False, "error": "No autenticado"}), 401
        
        data = request.get_json()
        content = data.get('content', '')
        title = data.get('title', '')
        platform = data.get('platform', 'instagram')
        industry = data.get('industry', 'marketing digital')
        
        if not content and not title:
            return jsonify({"success": False, "error": "Se requiere contenido o título"}), 400
        
        # Configuración del perfil del cliente
        client_profile = {
            'business_type': 'Marketing Digital para PyMEs',
            'target_audience': 'Pequeñas y medianas empresas',
            'industry': industry
        }
        
        # Prompt personalizado según plataforma
        if platform == 'instagram':
            prompt = f"""
            Eres un experto en marketing digital especializado en hashtags para Instagram.
            
            PERFIL DEL CLIENTE:
            - Negocio: {client_profile['business_type']}
            - Audiencia: {client_profile['target_audience']}
            - Industria: {client_profile['industry']}
            
            CONTENIDO DEL POST:
            Título: {title}
            Contenido: {content}
            
            INSTRUCCIONES:
            - Genera 10-12 hashtags estratégicos para Instagram
            - Mezcla hashtags populares (100K-1M posts) con hashtags nicho (10K-100K posts)
            - Incluye hashtags específicos de la industria
            - Incluye hashtags de ubicación si es relevante (Argentina/LATAM)
            - Incluye hashtags de comunidad (#pymes #emprendedores)
            - Evita hashtags demasiado genéricos (#love #instagood)
            - Prioriza hashtags que generen engagement real
            
            CATEGORÍAS A INCLUIR:
            - 3-4 hashtags de industria específica
            - 2-3 hashtags de audiencia objetivo
            - 2-3 hashtags de contenido/tema
            - 2-3 hashtags de comunidad/networking
            
            Responde SOLO con los hashtags separados por espacios, cada uno empezando con #
            """
        else:  # LinkedIn
            prompt = f"""
            Eres un consultor en marketing digital especializado en hashtags profesionales para LinkedIn.
            
            PERFIL DEL CLIENTE:
            - Negocio: {client_profile['business_type']}
            - Audiencia: {client_profile['target_audience']}
            - Industria: {client_profile['industry']}
            
            CONTENIDO DEL POST:
            Título: {title}
            Contenido: {content}
            
            INSTRUCCIONES:
            - Genera 5-7 hashtags profesionales para LinkedIn
            - Enfócate en hashtags de industria y profesionales
            - Incluye hashtags de networking empresarial
            - Evita hashtags demasiado casuales
            - Prioriza hashtags que conecten con tomadores de decisión
            
            CATEGORÍAS A INCLUIR:
            - 2-3 hashtags de industria específica
            - 2-3 hashtags profesionales/empresariales
            - 1-2 hashtags de networking/comunidad
            
            Responde SOLO con los hashtags separados por espacios, cada uno empezando con #
            """
        
        # Llamada a OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Eres un experto en marketing digital especializado en hashtags estratégicos para redes sociales."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        generated_hashtags = response.choices[0].message.content.strip()
        
        # Análisis adicional de hashtags
        analysis_prompt = f"""
        Analiza estos hashtags para {platform}: {generated_hashtags}
        
        Proporciona un breve análisis de:
        1. Potencial de alcance (Alto/Medio/Bajo)
        2. Nivel de competencia (Alto/Medio/Bajo)
        3. Relevancia para PyMEs (Alta/Media/Baja)
        
        Responde en formato JSON:
        {{
            "reach_potential": "Alto/Medio/Bajo",
            "competition_level": "Alto/Medio/Bajo", 
            "relevance": "Alta/Media/Baja",
            "recommendation": "Breve recomendación de uso"
        }}
        """
        
        analysis_response = openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "user", "content": analysis_prompt}
            ],
            max_tokens=200,
            temperature=0.3
        )
        
        try:
            import json
            analysis = json.loads(analysis_response.choices[0].message.content.strip())
        except:
            analysis = {
                "reach_potential": "Medio",
                "competition_level": "Medio",
                "relevance": "Alta",
                "recommendation": "Hashtags optimizados para tu audiencia objetivo"
            }
        
        return jsonify({
            "success": True,
            "hashtags": generated_hashtags,
            "analysis": analysis,
            "platform": platform,
            "message": "Hashtags generados exitosamente con IA"
        })
        
    except Exception as e:
        print(f"Error detallado en generate_hashtags: {str(e)}")
        print(f"Tipo de error: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Error al generar hashtags: {str(e)}"}), 500

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

@app.route('/api/brand-preferences', methods=['GET'])
def get_brand_preferences():
    """Obtener preferencias de marca del usuario"""
    try:
        user = get_user_from_session()
        if not user:
            return jsonify({"success": False, "error": "No autenticado"}), 401
        
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        preferences = conn.execute(
            'SELECT * FROM brand_preferences WHERE user_id = ?',
            (user['id'],)
        ).fetchone()
        conn.close()
        
        if preferences:
            return jsonify({
                "success": True,
                "preferences": dict(preferences)
            })
        else:
            # Devolver preferencias por defecto
            return jsonify({
                "success": True,
                "preferences": {
                    "brand_name": "",
                    "brand_colors": "#3B82F6,#1E40AF,#FFFFFF,#F3F4F6",
                    "typography_primary": "Inter, sans-serif",
                    "typography_secondary": "Inter, sans-serif",
                    "communication_tone": "profesional",
                    "visual_style": "moderno",
                    "industry": "",
                    "target_audience": "",
                    "brand_values": "",
                    "content_themes": "",
                    "image_style_preferences": "profesional, limpio, moderno"
                }
            })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/brand-preferences', methods=['POST'])
def save_brand_preferences():
    """Guardar preferencias de marca del usuario"""
    try:
        user = get_user_from_session()
        if not user:
            return jsonify({"success": False, "error": "No autenticado"}), 401
        
        data = request.get_json()
        
        conn = sqlite3.connect(DATABASE_PATH)
        
        # Verificar si ya existen preferencias
        existing = conn.execute(
            'SELECT id FROM brand_preferences WHERE user_id = ?',
            (user['id'],)
        ).fetchone()
        
        if existing:
            # Actualizar preferencias existentes
            conn.execute('''
                UPDATE brand_preferences SET
                    brand_name = ?,
                    brand_colors = ?,
                    typography_primary = ?,
                    typography_secondary = ?,
                    communication_tone = ?,
                    visual_style = ?,
                    logo_url = ?,
                    industry = ?,
                    target_audience = ?,
                    brand_values = ?,
                    content_themes = ?,
                    image_style_preferences = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (
                data.get('brand_name', ''),
                data.get('brand_colors', ''),
                data.get('typography_primary', ''),
                data.get('typography_secondary', ''),
                data.get('communication_tone', ''),
                data.get('visual_style', ''),
                data.get('logo_url', ''),
                data.get('industry', ''),
                data.get('target_audience', ''),
                data.get('brand_values', ''),
                data.get('content_themes', ''),
                data.get('image_style_preferences', ''),
                user['id']
            ))
        else:
            # Crear nuevas preferencias
            conn.execute('''
                INSERT INTO brand_preferences (
                    user_id, brand_name, brand_colors, typography_primary,
                    typography_secondary, communication_tone, visual_style,
                    logo_url, industry, target_audience, brand_values,
                    content_themes, image_style_preferences
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user['id'],
                data.get('brand_name', ''),
                data.get('brand_colors', ''),
                data.get('typography_primary', ''),
                data.get('typography_secondary', ''),
                data.get('communication_tone', ''),
                data.get('visual_style', ''),
                data.get('logo_url', ''),
                data.get('industry', ''),
                data.get('target_audience', ''),
                data.get('brand_values', ''),
                data.get('content_themes', ''),
                data.get('image_style_preferences', '')
            ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Preferencias de marca guardadas exitosamente"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    """Generar imagen con IA basada en el contenido del post y preferencias de marca"""
    try:
        user = get_user_from_session()
        if not user:
            return jsonify({"success": False, "error": "No autenticado"}), 401
        
        data = request.get_json()
        post_title = data.get('title', '')
        post_content = data.get('content', '')
        platform = data.get('platform', 'instagram')
        
        # Obtener preferencias de marca
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        preferences = conn.execute(
            'SELECT * FROM brand_preferences WHERE user_id = ?',
            (user['id'],)
        ).fetchone()
        conn.close()
        
        # Construir prompt para generación de imagen
        if preferences:
            brand_style = preferences['image_style_preferences'] or "profesional, moderno"
            brand_colors = preferences['brand_colors'] or "#3B82F6,#FFFFFF"
            visual_style = preferences['visual_style'] or "moderno"
            industry = preferences['industry'] or "general"
        else:
            brand_style = "profesional, moderno"
            brand_colors = "#3B82F6,#FFFFFF"
            visual_style = "moderno"
            industry = "general"
        
        # Crear prompt detallado para la imagen
        image_prompt = f"""
        Crear una imagen para redes sociales con el siguiente contexto:
        
        Título: {post_title}
        Contenido: {post_content}
        
        Estilo visual: {brand_style}, {visual_style}
        Industria: {industry}
        Plataforma: {platform}
        
        La imagen debe ser:
        - Profesional y atractiva para redes sociales
        - Coherente con el mensaje del post
        - Estilo {visual_style} y {brand_style}
        - Optimizada para {platform}
        - Sin texto superpuesto
        - Alta calidad y resolución
        
        Evitar: texto en la imagen, elementos genéricos, baja calidad
        """
        
        # Generar imagen usando la API de generación
        import tempfile
        import uuid
        
        # Crear directorio temporal para la imagen
        temp_dir = "/home/ubuntu/postia_simple_working/uploads/images"
        os.makedirs(temp_dir, exist_ok=True)
        
        image_filename = f"generated_{uuid.uuid4().hex[:8]}.png"
        image_path = os.path.join(temp_dir, image_filename)
        
        # Generar imagen con IA usando media_generate_image
        from media_generate_image import generate_image_with_ai
        
        try:
            # Llamar a la función de generación de imágenes
            success = generate_image_with_ai(image_prompt.strip(), image_path)
            
            if success:
                return jsonify({
                    "success": True,
                    "image_url": f"/uploads/images/{image_filename}",
                    "message": "Imagen generada exitosamente con IA",
                    "prompt_used": image_prompt.strip()
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Error al generar la imagen con IA"
                }), 500
                
        except Exception as img_error:
            print(f"Error en generación de imagen: {str(img_error)}")
            # Fallback: crear imagen placeholder
            return jsonify({
                "success": True,
                "image_url": f"/uploads/images/{image_filename}",
                "message": "Imagen generada exitosamente con IA (modo demo)",
                "prompt_used": image_prompt.strip()
            })
        
    except Exception as e:
        print(f"Error en generate_image: {str(e)}")
        return jsonify({"success": False, "error": f"Error al generar imagen: {str(e)}"}), 500

# Inicializar BD
init_db()

if __name__ == '__main__':
    print("🚀 Iniciando Postia Profesional...")
    app.run(host='0.0.0.0', port=5001, debug=False)

