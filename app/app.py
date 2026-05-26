# =============================================================
# app.py — Aplicación principal Flask
# Proyecto Final Telemática — F1 Tech Hub
# Autor: Esteban Présiga Posada | UPB | Semestre 3
# =============================================================

from flask import Flask, render_template, jsonify
import datetime

# Inicialización de la aplicación Flask
app = Flask(__name__)

# -----------------------------------------------------------
# Datos de ejemplo: equipos y pilotos F1 2024
# En producción esto vendría de una base de datos o API externa
# -----------------------------------------------------------
TEAMS = [
    {
        "id": 1,
        "name": "Red Bull Racing",
        "country": "Austria",
        "color": "#3671C6",
        "accent": "#CC1E4A",
        "engine": "Honda RBPTH001",
        "championships": 6,
        "innovations": [
            "Suspensión pushrod trasera activa",
            "Gestión térmica avanzada del motor",
            "Diseño aerodinámico de underfloor"
        ],
        "drivers": ["Max Verstappen", "Sergio Pérez"]
    },
    {
        "id": 2,
        "name": "Ferrari",
        "country": "Italia",
        "color": "#E8002D",
        "accent": "#FFCC00",
        "engine": "Ferrari 066/10",
        "championships": 16,
        "innovations": [
            "Sidepods de concepto abierto",
            "Sistema de recuperación de energía MGU-K",
            "Difusor de doble plano"
        ],
        "drivers": ["Charles Leclerc", "Carlos Sainz"]
    },
    {
        "id": 3,
        "name": "Mercedes",
        "country": "Alemania",
        "color": "#27F4D2",
        "accent": "#000000",
        "engine": "Mercedes M15",
        "championships": 8,
        "innovations": [
            "DAS (Dual Axis Steering) — 2020",
            "Zero-pod concept aerodinámico",
            "F-duct de refrigeración activa"
        ],
        "drivers": ["Lewis Hamilton", "George Russell"]
    },
    {
        "id": 4,
        "name": "McLaren",
        "country": "Reino Unido",
        "color": "#FF8000",
        "accent": "#000000",
        "engine": "Mercedes M15",
        "championships": 8,
        "innovations": [
            "Papaya Rules aerodinámico 2023",
            "Gestión de neumáticos por telemetría IA",
            "Chasis de fibra de carbono ultra-ligero"
        ],
        "drivers": ["Lando Norris", "Oscar Piastri"]
    },
    {
        "id": 5,
        "name": "Aston Martin",
        "country": "Reino Unido",
        "color": "#358C75",
        "accent": "#CEDC00",
        "engine": "Mercedes M15",
        "championships": 0,
        "innovations": [
            "Túnel de viento de 60% escala",
            "Simulador de conducción con IA",
            "Sistema de suspensión adaptativa"
        ],
        "drivers": ["Fernando Alonso", "Lance Stroll"]
    }
]

TECHNOLOGIES = [
    {
        "title": "Motor Híbrido MGU-H",
        "category": "Propulsión",
        "icon": "⚡",
        "description": "El Motor Generator Unit-Heat recupera energía cinética del turbocompresor. Opera a 125.000 RPM y puede suministrar hasta 120 kW de potencia eléctrica instantánea.",
        "year": 2014,
        "impact": "Eficiencia térmica >50%"
    },
    {
        "title": "Fibra de Carbono T800",
        "category": "Materiales",
        "icon": "🔬",
        "description": "Monocasco de fibra de carbono capaz de soportar impactos de 60G. Más resistente que el acero pero 5 veces más liviano. Cada chasis toma 3 semanas fabricarlo.",
        "year": 1981,
        "impact": "Reducción 40% del peso estructural"
    },
    {
        "title": "Neumáticos Pirelli Activos",
        "category": "Neumáticos",
        "icon": "🔄",
        "description": "Compuestos termoplásticos diseñados para operar entre 80°C-110°C. Los ingenieros monitorizan temperatura en tiempo real vía 200+ sensores por vuelta.",
        "year": 2011,
        "impact": "Ventana operativa ±5°C"
    },
    {
        "title": "DRS (Drag Reduction System)",
        "category": "Aerodinámica",
        "icon": "🏎️",
        "description": "Alerón trasero ajustable que reduce la resistencia aerodinámica hasta un 15% en rectas. Se activa a más de 1 segundo del coche delante en zonas designadas.",
        "year": 2011,
        "impact": "Ganancia de velocidad: +12 km/h"
    },
    {
        "title": "Telemetría en Tiempo Real",
        "category": "Software",
        "icon": "📡",
        "description": "Cada monoplaza transmite +1.500 canales de datos simultáneamente al equipo. Los ingenieros de pista procesan 2GB de datos por vuelta para optimizar estrategias.",
        "year": 1993,
        "impact": "2GB de datos por vuelta"
    },
    {
        "title": "Simulación CFD",
        "category": "Software",
        "icon": "💻",
        "description": "Dinámica de Fluidos Computacional: los equipos ejecutan millones de simulaciones aerodinámicas por semana. La FIA limita su uso para equilibrar la competencia.",
        "year": 2000,
        "impact": "Reducción 30% en pruebas físicas"
    }
]

STATS = [
    {"label": "Velocidad Máxima", "value": "372", "unit": "km/h", "icon": "🚀"},
    {"label": "G en Curva", "value": "6.5", "unit": "G", "icon": "⭕"},
    {"label": "0–100 km/h", "value": "2.6", "unit": "seg", "icon": "⚡"},
    {"label": "RPM del Motor", "value": "18.000", "unit": "rpm", "icon": "🔧"},
    {"label": "Peso Mínimo", "value": "800", "unit": "kg", "icon": "⚖️"},
    {"label": "Potencia Total", "value": "1.000", "unit": "CV", "icon": "💪"}
]

# -----------------------------------------------------------
# Rutas de la aplicación
# -----------------------------------------------------------

@app.route("/")
def index():
    """Página principal — muestra estadísticas y resumen."""
    return render_template(
        "index.html",
        stats=STATS,
        teams_count=len(TEAMS),
        tech_count=len(TECHNOLOGIES),
        current_year=datetime.datetime.now().year
    )

@app.route("/teams")
def teams():
    """Página de equipos F1."""
    return render_template("teams.html", teams=TEAMS)

@app.route("/technology")
def technology():
    """Página de innovación tecnológica automotriz."""
    return render_template("technology.html", technologies=TECHNOLOGIES)

@app.route("/api/teams")
def api_teams():
    """API REST — devuelve equipos en formato JSON."""
    return jsonify({
        "status": "success",
        "count": len(TEAMS),
        "data": TEAMS
    })

@app.route("/api/technologies")
def api_technologies():
    """API REST — devuelve tecnologías en formato JSON."""
    return jsonify({
        "status": "success",
        "count": len(TECHNOLOGIES),
        "data": TECHNOLOGIES
    })

@app.route("/api/health")
def health_check():
    """
    Endpoint de salud para Docker/AWS health checks.
    Retorna 200 OK si el servicio está activo.
    """
    return jsonify({
        "status": "healthy",
        "service": "F1 Tech Hub",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }), 200

# -----------------------------------------------------------
# Punto de entrada
# -----------------------------------------------------------
if __name__ == "__main__":
    # En producción usa Gunicorn (ver Dockerfile)
    # Aquí solo para desarrollo local
    app.run(host="0.0.0.0", port=5000, debug=False)
