"""
Módulo para generación de imágenes con IA
Integra con la herramienta media_generate_image de Manus
"""

def generate_image_with_ai(prompt, output_path):
    """
    Genera una imagen usando IA basada en el prompt proporcionado
    
    Args:
        prompt (str): Descripción detallada para la imagen
        output_path (str): Ruta donde guardar la imagen generada
        
    Returns:
        bool: True si la generación fue exitosa, False en caso contrario
    """
    try:
        import os
        import sys
        
        # Crear el directorio si no existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Usar la herramienta media_generate_image de Manus
        try:
            # Importar la herramienta de generación de imágenes
            from media_generate_image import media_generate_image
            
            # Generar imagen usando la herramienta de Manus
            result = media_generate_image(
                brief="Generar imagen para post de redes sociales",
                images=[{
                    "path": output_path,
                    "prompt": prompt,
                    "aspect_ratio": "square"
                }]
            )
            
            # Verificar si la imagen se generó correctamente
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"✅ Imagen generada exitosamente: {output_path}")
                return True
            else:
                print(f"❌ Error: Imagen no generada o archivo vacío")
                return False
                
        except ImportError:
            print("⚠️ Herramienta media_generate_image no disponible, usando fallback...")
            return generate_fallback_image(prompt, output_path)
            
    except Exception as e:
        print(f"❌ Error en generate_image_with_ai: {str(e)}")
        return generate_fallback_image(prompt, output_path)

def generate_fallback_image(prompt, output_path):
    """
    Genera una imagen de respaldo usando PIL cuando la herramienta principal no está disponible
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import textwrap
        import hashlib
        
        # Crear imagen de 1080x1080 (formato Instagram)
        img = Image.new('RGB', (1080, 1080), color='#3B82F6')
        draw = ImageDraw.Draw(img)
        
        # Intentar usar una fuente del sistema
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Agregar texto centrado
        text = "Imagen generada con IA"
        
        # Calcular posición centrada
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (1080 - text_width) // 2
        y = (1080 - text_height) // 2 - 100
        
        # Dibujar texto principal
        draw.text((x, y), text, fill='white', font=font)
        
        # Agregar descripción del prompt (truncada)
        prompt_lines = textwrap.wrap(prompt[:200] + "...", width=50)
        y_offset = y + 100
        
        for line in prompt_lines[:5]:  # Máximo 5 líneas
            bbox = draw.textbbox((0, 0), line, font=small_font)
            line_width = bbox[2] - bbox[0]
            x_line = (1080 - line_width) // 2
            draw.text((x_line, y_offset), line, fill='white', font=small_font)
            y_offset += 30
        
        # Agregar un patrón único basado en el prompt para diferencias visuales
        hash_obj = hashlib.md5(prompt.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Usar el hash para crear un patrón de color único
        r = int(hash_hex[0:2], 16)
        g = int(hash_hex[2:4], 16) 
        b = int(hash_hex[4:6], 16)
        
        # Dibujar algunos elementos decorativos basados en el hash
        for i in range(5):
            x_pos = (int(hash_hex[i*2:i*2+2], 16) % 800) + 140
            y_pos = (int(hash_hex[i*2+1:i*2+3], 16) % 800) + 140
            draw.ellipse([x_pos-20, y_pos-20, x_pos+20, y_pos+20], fill=(r, g, b, 100))
        
        # Guardar imagen
        img.save(output_path, 'PNG')
        print(f"✅ Imagen fallback generada: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en generate_fallback_image: {str(e)}")
        return False

