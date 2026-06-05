## ELECTIVA 4 - MODULO DE NOTAS FINALES Y APARTADO DE PARTICIPACION EN CLASE

---

### Grupo: Participación en clase y notas finales

1. Implementación del Apartado de **Participación en Clase**
  - Agrega un nuevo registro paralelo a la asistencia para que el profesor marque si cada estudiante participó.
  - Permite crear sesiones por materia, sección y fecha.
  - Carga automáticamente los estudiantes de la sección seleccionada.
  - Registra un checkbox por estudiante para indicar participación.
  - Guarda el resultado como dato de participación para que pueda ser usado luego en el cálculo de notas.

2. Implementación del módulo de **Notas Finales**
  - Construye un reporte de notas por materia, sección y estudiante.
  - Consolida calificaciones de:
    - actividades del profesor,
    - asistencia,
    - participación en clase.
  - Muestra:
    - nota final ponderada,
    - promedio general,
    - detalle por tipo de evaluación.
  - El informe es de solo lectura, para evitar modificar resultados directamente desde el reporte.

### Alcance del trabajo del grupo

- Desarrollar el nuevo flujo de participación en clase dentro de gestion_estudiantil.
- Diseñar los modelos y vistas para almacenar sesiones y líneas de participación.
- Crear la estructura de datos necesaria para que el módulo de notas finales consuma esa información.
- Definir la arquitectura del módulo de notas finales como un reporte independiente que lea los datos de los demás módulos.

---

### Modelos Propuestos 

1. **Participación en clase**

**Modelo: `gestion.participacion.clase`**

- `name`                    : Descripción breve de la sesión (Char).                              Permite identificar la sesión en listados cuando hay muchas (ej. "Participación 2026-05-24 - Sección A").
- `date`                    : Fecha de la sesión (Date, default hoy).                             Necesaria para filtrar por periodo y ordenar sesiones cronológicamente.
- `subject_id`              : Materia (Many2one → `gestion.materia`).                             Permite relacionar la sesión con una materia concreta y obtener `periodo_academico`.
- `section_id`              : Sección (Many2one → `gestion.seccion`,                              domain por `subject_id`). Filtra los estudiantes y permite ver la sesión por sección.
- `teacher_id`              : Profesor (Many2one related → `section_id.teacher_id`, store=True).  Facilita filtros por docente y controla permisos (solo su profesor debe marcar).
- `state`                   : Estado (Selection: `draft`/`confirmed`).                            Repite el patrón de asistencia: evitar ediciones después de confirmar.
- `participation_line_ids`  : Líneas de participación (One2many → `gestion.participacion.line`).  Contiene las marcas por estudiante; necesario para la UI tipo lista editable y para agregar al cálculo de notas.

¿Por qué estos campos?
- Reproduce la UX de `gestion.attendance` (consistencia).
- `subject_id` + `section_id` permiten filtrar estudiantes y relacionar con `periodo_academico`.
- `state` protege la integridad de datos tras confirmar.

---

**Modelo: `gestion.participacion.line`**

- `participacion_id`        : Relación a la sesión (Many2one → `gestion.participacion.clase`, ondelete='cascade').  Mantiene integridad; si se borra la sesión, se borran las líneas.
- `student_id`              : Estudiante (Many2one → `gestion.student`, required).                                  Identifica a quién corresponde la línea.
- `participo`               : Checkbox (Boolean).                                                                   Entrada que marca si el estudiante participó.

---

2. **Notas Finales**

**Modelo: `gestion.nota.final`**

- `student_id`        : Estudiante (Many2one → `gestion.student`, required).                  Identifica la nota.
- `section_id`        : Sección (Many2one → `gestion.seccion`, required).                     Las notas son por sección.
- `subject_id`        : Materia (Many2one related → `section_id.subject_id`, store=True).     Para mostrar materia y periodos sin joins extra.
- `periodo_academico` : Período (Char related → `subject_id.periodo_academico`, store=True).  Usa la estructura existente del proyecto; evita crear un modelo nuevo si no es necesario.
- `nota_final`        : Nota total ponderada (Float, compute store).                          Suma de los `aporte` de los `detalle_ids`; valor final mostrado en listados.
- `promedio`          : Promedio simple o indicador (Float, compute store).                   Opcional: muestra promedio aritmético de los promedios por tipo (útil para análisis).
- `detalle_ids`       : Desglose (One2many → `gestion.nota.detalle`).                         Guarda cómo se compone la nota por cada tipo de evaluación.

¿Por qué estos campos?
- Mantener `periodo_academico` como related evita duplicar modelos y facilita filtros por periodo.
- Guardar `nota_final` permite búsquedas/ordenaciones y evita recálculos constantes en listados.
- `detalle_ids` permite trazabilidad y transparencia del cálculo.

---

**Modelo: `gestion.nota.detalle`**
- `nota_final_id`       : Relación al padre (Many2one → `gestion.nota.final`, required, ondelete='cascade').  Vincula el aporte con la nota final.
- `tipo_evaluacion_id`  : Tipo de evaluación (Many2one → `gestion.tipo.evaluacion`, optional).                Enlaza con el módulo del otro grupo que define porcentajes y categorías.
- `promedio_tipo`       : Promedio del estudiante en ese tipo (Float).                                        Ej.: promedio de todos los exámenes del tipo "Examen en clase".
- `peso`                : Porcentaje aplicable a ese tipo (Float).                                            Copia del porcentaje definido en `gestion.tipo.evaluacion` en el momento del cálculo (permite auditoría si el otro grupo cambia la configuración después).
- `aporte`              : Puntos aportados a la nota final (Float).                                           Resultado de `promedio_tipo * peso`.

¿Por qué estos campos?
- `peso` local copiado protege contra cambios futuros en la configuración global y permite reproducir cálculos históricos.
- `tipo_evaluacion_id` conecta con el módulo que define categorías/porcentajes.

--- 