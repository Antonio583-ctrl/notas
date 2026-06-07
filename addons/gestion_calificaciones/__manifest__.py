# -*- coding: utf-8 -*-
{
    'name': "Gestion Calificaciones",
    'summary': """
        Módulo simple para registro de calificaciones estudiantiles""",
    'description': """
        Módulo independiente para gestionar calificaciones.
        Incluye modelos para Estudiantes, Actividades, Entregas y Calificaciones.
    """,
    'author': "Kaazest",
    'category': 'Education',
    'version': '0.1',
    'depends': ['base', 'gestion_estudiantil', 'gestion_materia', 'gestion_profesorado', 'gestion_evaluacion'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/student_grade_views.xml',
        'views/grade_views.xml',
        'views/activity_inherit_views.xml'
    ],
}