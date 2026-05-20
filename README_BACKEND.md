# Asistente Financiero - Backend

## 🚀 Quick Start

### 1️⃣ Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2️⃣ Asegurar que Ollama está corriendo
```bash
ollama serve
```
(En otra terminal)

### 3️⃣ Ejecutar el servidor
```bash
python main.py
```

El backend estará disponible en: **http://localhost:8000**

---

## 📡 Endpoints Disponibles

### ✅ Health Check
```
GET http://localhost:8000/
```

### 📊 Analizar Finanzas (PRINCIPAL)
```
POST http://localhost:8000/analizar
```

**Body:**
```json
{
  "salario": 5000000,
  "nivel_riesgo": "Medio",
  "objetivo_financiero": "Ahorrar para la educación",
  "horizonte": "Largo plazo",
  "fondo_emergencia": true
}
```

**Respuesta:**
```json
{
  "salario": 5000000,
  "nivel_riesgo": "Medio",
  "objetivo_financiero": "Ahorrar para la educación",
  "horizonte": "Largo plazo",
  "fondo_emergencia": true,
  "ahorro_inversion": 1000000,
  "necesidades": 2500000,
  "deseos": 1500000,
  "distribucion_objetivo": {...},
  "portafolio_optimo": [...],
  "valor_proyectado": 11200000,
  "fondo_emergencia_valor": 7500000,
  "recomendacion": "Basado en tu salario y perfil...",
  "mensaje": "Resumen breve y entendible..."
}
```

### 📚 Obtener Catálogo de Inversiones
```
GET http://localhost:8000/catalogo
```

### 🔗 Verificar conexión con Ollama
```
GET http://localhost:8000/health
```

---

## 🧪 Probar con cURL

```bash
# Probar salud
curl http://localhost:8000/

# Obtener análisis
curl -X POST http://localhost:8000/analizar \
  -H "Content-Type: application/json" \
  -d '{"salario": 5000000, "nivel_riesgo": "Medio"}'
```

---

## 🎨 Frontend (Próximo Paso)

Cuando tengas listo un frontend (React, Vue, etc.), apunta a:
```
http://localhost:8000/analizar
```

Los CORS ya están configurados para permitir peticiones desde cualquier origen.

---

## 📝 Notas

- La API usa **Ollama** localmente (no consume internet)
- Asegúrate de tener el modelo `llama3.2` descargado: `ollama pull llama3.2`
- El puerto por defecto es `8000` (puedes cambiarlo en `main.py`)
