# Generador de Hologramas en Pirámide 3D

## Descripción del Proyecto

Este proyecto implementa un generador de hologramas tridimensionales en forma de pirámide utilizando Python. El script principal `3DHologram.py` utiliza las bibliotecas OpenCV y NumPy para procesar imágenes y videos, creando efectos holográficos al combinar rotaciones de la imagen original en cuatro direcciones principales: arriba, abajo, izquierda y derecha.

El holograma resultante simula un efecto 3D piramidal que puede ser visualizado desde diferentes ángulos, creando una ilusión óptica fascinante.

## Funcionalidades Principales

- **Generación de hologramas estáticos**: Convierte una imagen 2D en un holograma 3D piramidal.
- **Procesamiento de videos**: Transforma videos completos en secuencias holográficas.
- **Personalización de parámetros**: Ajusta escala, distancia y otros parámetros para diferentes efectos.
- **Rotación automática**: Implementa rotaciones precisas de 90, 180 y 270 grados.

## Requisitos del Sistema

- **Sistema Operativo**: Compatible con Windows, macOS y Linux
- **Python**: Versión 3.x (recomendado Python 3.6 o superior)
- **Memoria RAM**: Mínimo 2GB, recomendado 4GB o más para procesamiento de videos
- **Espacio en disco**: Dependiendo del tamaño de los archivos de entrada y salida

## Dependencias

El proyecto requiere las siguientes bibliotecas de Python:

- **OpenCV (opencv-python)**: Para procesamiento de imágenes y videos
- **NumPy**: Para operaciones matemáticas con arrays

## Instalación

### Paso 1: Instalar Python

Si no tienes Python instalado, descárgalo desde el sitio oficial: https://www.python.org/downloads/

### Paso 2: Crear un entorno virtual (recomendado)

Para evitar conflictos con otras instalaciones de Python, crea un entorno virtual:

```bash
python -m venv hologram_env
```

Activa el entorno virtual:

- En Windows:
  ```bash
  hologram_env\Scripts\activate
  ```

- En macOS/Linux:
  ```bash
  source hologram_env/bin/activate
  ```

### Paso 3: Instalar las dependencias

Con el entorno virtual activado, instala las bibliotecas requeridas:

```bash
pip install opencv-python numpy
```

Si usas conda en lugar de pip:

```bash
conda install opencv numpy
```

### Paso 3: Verificar la instalación

Ejecuta Python e importa las bibliotecas para verificar:

```python
import cv2
import numpy as np
print("Instalación exitosa")
```

## Uso del Programa

### Preparación de archivos de entrada

- **Imágenes**: Usa imágenes cuadradas (ej: 640x640 píxeles) para mejores resultados. Formatos soportados: PNG, JPG, JPEG, BMP.
- **Videos**: Formatos comunes como AVI, MP4. El script procesa frame por frame.

### Ejecutar el script

#### Para generar un holograma desde una imagen:

```bash
python 3DHologram.py ruta/a/tu/imagen.png
```

Ejemplo:
```bash
python 3DHologram.py imagen_ejemplo.png
```

Esto creará un archivo `hologram.png` con el holograma generado.

#### Para procesar un video:

```bash
python 3DHologram.py ruta/a/tu/video.avi
```

Ejemplo:
```bash
python 3DHologram.py mi_video.avi
```

Esto procesará el video frame por frame y creará un archivo `hologram.avi` con el efecto holográfico aplicado.

#### Para procesar un video:

El script tiene una ruta de video hardcodeada. Para usarlo con tu propio video:

1. Abre `3DHologram.py`
2. Busca la línea: `process_video("/home/evan/Videos/test.avi")`
3. Cámbiala por: `process_video("ruta/a/tu/video.avi")`

Ejemplo:
```python
process_video("mi_video.avi")
```

Luego ejecuta el script normalmente. Esto generará un archivo `hologram.avi`.

### Parámetros de personalización

La función `makeHologram()` acepta los siguientes parámetros:

- `original`: Imagen de entrada (obligatorio)
- `scale`: Factor de escala de la imagen (por defecto: 0.5)
- `scaleR`: Factor de escala del holograma (por defecto: 4)
- `distance`: Distancia entre las imágenes rotadas (por defecto: 0)

Ejemplo de uso avanzado:

```python
import cv2
from 3DHologram import makeHologram

# Cargar imagen
img = cv2.imread('mi_imagen.png')

# Crear holograma con parámetros personalizados
holograma = makeHologram(img, scale=1.0, scaleR=5, distance=20)

# Guardar resultado
cv2.imwrite('mi_holograma.png', holograma)
```

## Ejemplos Prácticos

### Ejemplo 1: Holograma básico

```python
import cv2
import numpy as np
from 3DHologram import makeHologram

# Cargar una imagen de prueba
imagen = cv2.imread('flor.png')

# Generar holograma
holo = makeHologram(imagen)

# Mostrar resultado
cv2.imshow('Holograma', holo)
cv2.waitKey(0)
cv2.destroyAllWindows()
```

### Ejemplo 2: Procesamiento por lotes

```python
import os
import cv2
from 3DHologram import makeHologram

# Directorio con imágenes
directorio = 'imagenes/'

# Procesar todas las imágenes PNG
for archivo in os.listdir(directorio):
    if archivo.endswith('.png'):
        img = cv2.imread(os.path.join(directorio, archivo))
        holo = makeHologram(img, scale=0.8, scaleR=3)
        nombre_salida = 'holo_' + archivo
        cv2.imwrite(nombre_salida, holo)
        print(f"Procesado: {archivo} -> {nombre_salida}")
```

## Estructura del Código

### Funciones principales:

- `makeHologram(original, scale, scaleR, distance)`: Crea el holograma combinando rotaciones
- `process_video(video)`: Procesa un video frame por frame
- `rotate_bound(image, angle)`: Rota una imagen manteniendo sus dimensiones

### Flujo de trabajo:

1. Carga la imagen/video de entrada
2. Redimensiona según el parámetro `scale`
3. Crea copias rotadas (0°, 90°, 180°, 270°)
4. Combina las rotaciones en un canvas más grande
5. Ajusta posiciones según `distance` y `scaleR`
6. Guarda el resultado

## Solución de Problemas

### Error de importación de OpenCV

Si obtienes errores como `ModuleNotFoundError: No module named 'cv2'`:

```bash
pip uninstall opencv-python
pip install opencv-python
```

### Problemas con videos

**IMPORTANTE:** Si encuentras errores como "Processing 0 frames" o mensajes de corrupción de video, consulta la [Guía de Solución de Problemas Detallada](TROUBLESHOOTING.md) para soluciones completas.

**Solución Rápida para Videos Corruptos:**
```bash
# Reparar video con FFmpeg
ffmpeg -i video_corrupto.avi -c:v libx264 -preset medium -crf 23 video_reparado.mp4

# Procesar video reparado
python 3DHologram.py video_reparado.mp4
```

Otros problemas comunes:
- Asegúrate de que el archivo de video no esté corrupto
- Verifica que tengas permisos de escritura en el directorio
- Para videos grandes, aumenta la memoria RAM disponible
- El script mejorado ahora maneja automáticamente frames corruptos

### Imágenes distorsionadas

- Usa imágenes cuadradas para mejores resultados
- Ajusta el parámetro `scale` si la imagen es muy grande

## Notas Técnicas

- El script ha sido actualizado para usar la API moderna de OpenCV (`cv2.VideoWriter_fourcc()`).
- Incluye manejo robusto de errores para videos corruptos o con frames dañados.
- Soporta múltiples codecs de salida con fallback automático (mp4v, XVID, H264, MJPG).
- El procesamiento es CPU intensivo; considera usar GPU para videos largos.
- Los hologramas generados son simulaciones ópticas y requieren visualización especial para el efecto 3D completo.
- Para problemas detallados y soluciones, consulta [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

## Mejoras Recientes (v2.0)

### Características Nuevas:
- ✅ **Validación de video mejorada**: Detecta y reporta problemas antes de procesar
- ✅ **Manejo de frames corruptos**: Salta automáticamente frames dañados
- ✅ **Múltiples codecs de salida**: Prueba automáticamente diferentes codecs
- ✅ **Logging detallado**: Información clara sobre el progreso y errores
- ✅ **Conteo de frames robusto**: Funciona incluso con metadata incorrecta
- ✅ **Indicadores de progreso**: Muestra el avance del procesamiento
- ✅ **Mejor manejo de errores**: Mensajes claros y soluciones sugeridas

### Archivos de Salida:
- **Imágenes**: `hologram.png` (mismo nombre que antes)
- **Videos**: `hologram_output.mp4` o `hologram_output.avi` (según codec disponible)

## Contribución

¡Las contribuciones son bienvenidas! Para contribuir:

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Contacto

Si tienes preguntas o sugerencias, por favor abre un issue en el repositorio.

---

¡Disfruta creando hologramas fascinantes con este generador 3D!