{
    "name": "Gestión Nota Final",
    "summary": "Notas finales por estudiante y sección",
    "description": "Calcula notas finales de estudiantes según tipos de evaluación, asistencia y actividades.",
    "version": "18.0.1.0.0",
    "author": "Equipo Backend",
    "category": "Education",
    "depends": [
        "base",
        "gestion_estudiantil",
        "gestion_profesorado",
        "gestion_secciones",
        "gestion_materia",
        "gestion_evaluacion",
        "gestion_calificaciones"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/nota_final_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
