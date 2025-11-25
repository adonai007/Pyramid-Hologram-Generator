# HoloCone - Setup & Installation

## Requirements

### requirements.txt
```txt
kivy==2.3.0
kivymd==1.2.0
numpy==1.24.3
pillow==10.0.0
ffpyplayer==4.5.1
screeninfo==0.8.1
```

### Installation Steps

#### 1. Desktop (Windows/Mac/Linux)
```bash
# Create virtual environment
python -m venv holocone_env

# Activate (Windows)
holocone_env\Scripts\activate

# Activate (Mac/Linux)
source holocone_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

#### 2. Android Build (usando Buildozer)

**buildozer.spec:**
```ini
[app]
title = HoloCone
package.name = holocone
package.domain = com.yourcompany

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp4

version = 0.1
requirements = python3,kivy,numpy,pillow,ffpyplayer

[buildozer]
log_level = 2
```

**Build Android APK:**
```bash
# Install buildozer
pip install buildozer

# Initialize (solo primera vez)
buildozer init

# Build debug APK
buildozer android debug

# Build release APK
buildozer android release
```

## Estructura de Proyecto Completa

```
holocone/
├── main.py                 # Código principal (artifact anterior)
├── requirements.txt        # Dependencias
├── buildozer.spec         # Config Android
├── README.md              # Documentación
├── assets/
│   ├── videos/
│   │   ├── sample_jellyfish.mp4
│   │   ├── particles.mp4
│   │   └── logo_rotate.mp4
│   └── icons/
│       └── icon.png       # Icono de la app
└── tests/
    └── test_calibration.py
```

## Videos de Ejemplo

Para testing, puedes usar estos videos (fondos negros):

1. **Jellyfish**: Buscar "jellyfish black background video"
2. **Particles**: Buscar "particles black background loop"
3. **Logo**: Crear con After Effects o Blender

## Próximos Pasos para Mejorar

### Versión 1.1 - Mejoras Core
```python
# 1. Soporte multi-display real
import screeninfo

def get_all_monitors():
    monitors = screeninfo.get_monitors()
    return [
        {
            'name': m.name,
            'width': m.width,
            'height': m.height,
            'x': m.x,
            'y': m.y,
            'is_primary': m.is_primary
        }
        for m in monitors
    ]

# 2. Shader para mejor performance
vertex_shader = '''
$HEADER$
attribute vec2 vPosition;
attribute vec2 vTexCoords0;
varying vec2 tex_coord;

void main() {
    tex_coord = vTexCoords0;
    gl_Position = vec4(vPosition, 0.0, 1.0);
}
'''

fragment_shader = '''
$HEADER$
uniform sampler2D texture0;
varying vec2 tex_coord;

void main() {
    vec4 color = texture2D(texture0, tex_coord);
    // Apply transformations for 4 views
    gl_FragColor = color;
}
'''

# 3. Biblioteca de videos
class VideoLibrary:
    def __init__(self):
        self.videos = self.scan_videos()
    
    def scan_videos(self):
        video_dir = Path('assets/videos')
        return list(video_dir.glob('*.mp4'))
    
    def get_thumbnail(self, video_path):
        # Extract first frame as thumbnail
        pass
```

### Versión 1.2 - Features Avanzados
```python
# 1. Generador de contenido
class ContentGenerator:
    def create_text_animation(self, text, style='neon'):
        # Generate animated text with effects
        pass
    
    def create_logo_spin(self, logo_path):
        # Create rotating logo animation
        pass

# 2. Control remoto web
from flask import Flask, render_template
from flask_socketio import SocketIO

class RemoteControl:
    def __init__(self, app):
        self.flask = Flask(__name__)
        self.socketio = SocketIO(self.flask)
        self.setup_routes()
    
    def setup_routes(self):
        @self.flask.route('/')
        def remote():
            return render_template('remote.html')

# 3. Sincronización con música
class AudioSync:
    def analyze_beat(self, audio_file):
        # Beat detection for sync
        pass
```

## Testing con HDMI

### Setup para Testing
1. **Laptop → TV:**
   - Conectar HDMI
   - Windows: Win+P → Extender
   - Mac: System Preferences → Displays
   - Linux: xrandr o arandr

2. **Android → TV:**
   - USB-C to HDMI adapter
   - O usar Samsung DeX / dispositivos compatibles

3. **Calibración Rápida:**
   - TV 55": projection_size ≈ 800px en FHD
   - TV 42": projection_size ≈ 600px en FHD
   - Monitor 27": projection_size ≈ 400px en FHD

## Troubleshooting

### Problema: Video no se ve en 4 vistas
```python
# Verificar que el video tenga fondo negro
# Verificar calibración:
print(f"Projection: {profile.projection_x}, {profile.projection_y}")
print(f"Size: {profile.projection_size}")
```

### Problema: No detecta HDMI
```python
# Linux: verificar con xrandr
import subprocess
result = subprocess.run(['xrandr'], capture_output=True, text=True)
print(result.stdout)

# Windows: usar win32api
import win32api
monitors = win32api.EnumDisplayMonitors()
```

### Problema: Performance bajo
```python
# Reducir resolución del video
# Usar hardware acceleration
os.environ['KIVY_WINDOW'] = 'sdl2'  # Better performance
```

## Optimizaciones de Performance

```python
# 1. Cache de texturas
texture_cache = {}

def get_cached_texture(video_path):
    if video_path not in texture_cache:
        texture_cache[video_path] = load_texture(video_path)
    return texture_cache[video_path]

# 2. Frame skipping adaptativo
class AdaptivePlayer:
    def __init__(self):
        self.target_fps = 30
        self.last_frame_time = 0
    
    def should_update(self):
        current_time = time.time()
        if current_time - self.last_frame_time > 1/self.target_fps:
            self.last_frame_time = current_time
            return True
        return False

# 3. Pre-renderizado
def prerender_views(video_texture, profile):
    # Render all 4 views to FBO once
    # Then just blit the FBO
    pass
```

## Recursos Útiles

- **Kivy Documentation**: https://kivy.org/doc/stable/
- **OpenGL with Python**: https://www.opengl.org/wiki/Python
- **FFmpeg Python**: https://github.com/kkroening/ffmpeg-python
- **Android USB Display**: https://developer.android.com/training/multiple-display

## Licencia
MIT License - Libre para uso comercial y personal