{
    "name": "Gestion de Materias",
    "summary": "modulo para la gestion de las materias",
    "description": "Este modulo permite gestionar las materias en un sistema de gestion estudiantil.",
    "version": "18.0.1.0.0",
    "author": "Kaazest",
    "depends": ["base", "gestion_profesorado"],
    "data": [
        "security/ir.model.access.csv",
        "views/materia_views.xml",
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
