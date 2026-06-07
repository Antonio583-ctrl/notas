# ELECTIVA 4 - MÓDULO DE CONFIGURACIÓN Y TIPOS DE EVALUACIÓN

## 1. OBJETIVO GENERAL

Desarrollar un módulo independiente en Odoo que permita a los profesores configure de forma dinámica los tipos de evaluación y sus respectivos porcentajes por cada sección y período académico.

## 2. ARQUITECTURA DE DATOS (MODELOS)

Todo el desarrollo se centralizará en un único módulo técnico llamado gestion_evaluacion. A continuación, se detallan los modelos nuevos y las extensiones por herencia.

### A. Modelos Nuevos:

#### 1. gestion.tipo.evaluacion (Configuración de Categorías)

Este modelo define los criterios de evaluación y su peso dorado para una sección específica.
- name (Char, Required): Nombre de la categoría (Ej: "Proyecto Final", "Exámenes", "Asistencia", "Participación").
- porcentaje (Float): Peso de la evaluación. *Validación: La suma de los porcentajes de una misma sección debe dar 100% (1.0).*
- seccion_id (Many2one \rightarrow gestion.seccion, Required): Vincula la configuración a una sección específica.
- periodo_id (Many2one \rightarrow gestion.periodo, Dynamic): Filtro por el período académico activo.

### B. Modelos Heredados (Extensiones por código):

Nota: No se toca la carpeta de los otros módulos. Se usa _inherit en nuestros propios archivos Python.

#### 1. Extensión de Actividades (_inherit = 'gestion.activity')

- Se añade el campo tipo_evaluacion_id (Many2one \rightarrow gestion.tipo.evaluacion).
- Filtro (Domain): En la vista, este campo solo debe mostrar los tipos de evaluación que pertenezcan a la seccion_id seleccionada en la actividad.

#### 2. Extensión de Asistencias (_inherit = 'gestion.attendance')

- Se añade el campo tipo_evaluacion_id (Many2one \rightarrow gestion.tipo.evaluacion).
- Lógica Automática:  Mediante el método default_get o un onchange, al crear un registro de asistencia, este campo se auto-asigna a la categoría "Asistencia" de esa sección.

## 4. CRONOGRAMA DE EJECUCIÓN (ETAPAS)

Para avanzar con orden, dividiremos el trabajo en 4 fases consecutivas:

[Fase 1: Estructura] ──> [Fase 2: Modelos/Vistas] ──> [Fase 3: Herencias] ──> [Fase 4: Lógica]

### Fase 1: Esqueleto del Módulo e Integración Técnica:

- Crear la carpeta del módulo gestion_evaluacion.
- Configurar el archivo __manifest__.py declarando las dependencias obligatorias: los módulos de los compañeros que contienen a gestion.activity y el de asistencias. Esto asegura que nuestro módulo se cargue después que los de ellos.
- Estructurar las carpetas internas de Odoo: models/, views/, y security/.

### Fase 2: Configuración Dinámica y Modelo Propio:

- Escribir el modelo gestion.tipo.evaluacion.
- Crear la regla de validación (@api.constrains) para que los porcentajes por sección no excedan ni sean menores al 100%.
- Diseñar las vistas de formulario y lista exclusivamente para este modelo.

### Fase 3: Inyección por Herencia:

- Crear los archivos de herencia para gestion.activity y el módulo de asistencias.
- Escribir los archivos XML que heredan las vistas originales mediante inherit_id y usar <xpath> para inyectar el campo tipo_evaluacion_id de forma estética en los formularios que ya existen.

### Fase 4: Coordinación:

- Aquí sería ponernos de acuerdo los líderes para corroborar que todo esté correcto y coordinar lo que se vaya a realizar en conjunto.
