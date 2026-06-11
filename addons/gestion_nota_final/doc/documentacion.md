# Documentación del Módulo `gestion_nota_final`

## Descripción General

Este módulo de Odoo calcula y muestra de forma automática la **nota final** de cada estudiante por materia y sección. No se puede editar manualmente desde la interfaz; se actualiza solo cuando el profesor registra o modifica calificaciones, asistencias o participaciones.

---

## Estructura de Archivos

```
gestion_nota_final/
├── models/
│   ├── __init__.py
│   ├── gestion_nota_final.py      → Modelo principal: Nota Final
│   ├── gestion_nota_final_line.py → Modelo de detalle: una fila por tipo de evaluación
│   └── grade_hook.py              → Ganchos (hooks) que escuchan cambios en otros módulos
├── views/
│   └── nota_final_views.xml       → Vistas de lista y formulario (solo lectura)
├── security/
│   └── ir.model.access.csv        → Permisos de acceso
└── data/
    └── gestion_nota_final_demo.xml → Datos de demostración
```

---

## Archivo: `gestion_nota_final.py`

### Clase `NotaFinal`
**Modelo:** `gestion.nota.final`

Representa el **reporte consolidado de notas** de un estudiante en una sección. Hay exactamente un registro por combinación de (estudiante + sección).

---

### Campos del modelo

| Campo | Tipo | Descripción |
|---|---|---|
| `student_id` | Many2one → `gestion.student` | El estudiante al que pertenece la nota |
| `section_id` | Many2one → `gestion.seccion` | La sección (aula/grupo) del estudiante |
| `subject_id` | Many2one → `gestion.materia` | La materia (se obtiene automáticamente de la sección) |
| `teacher_id` | Many2one → `gestion.teacher` | El profesor (se obtiene automáticamente de la sección) |
| `student_nombre` | Char | El nombre completo del estudiante (para búsquedas rápidas) |
| `detalle_ids` | One2many → `gestion.nota.final.detalle` | Lista de detalles, uno por tipo de evaluación |
| `nota_final` | Float (calculado) | Suma de todos los aportes ponderados → la nota final del estudiante |
| `promedio` | Float (calculado) | Promedio general ponderado entre todos los tipos |
| `recalc_trigger` | Integer | Contador interno que al cambiar fuerza el recálculo de todos los campos calculados |
| `active` | Boolean | Si está en falso, el registro se archiva y no aparece en listas |

> **Restricción:** No pueden existir dos registros con el mismo `student_id` + `section_id`.

---

### Métodos del modelo

#### `_search(domain, ...)`
Se ejecuta **cada vez que alguien busca o abre la lista** de notas finales.  
Antes de devolver resultados, llama a `_ensure_nota_final_records()` para crear automáticamente los registros de estudiantes que todavía no tengan su nota generada.

```
Usuario abre la vista de Notas Finales
  → _search se ejecuta
  → _ensure_nota_final_records crea los registros faltantes
  → Se muestran los resultados
```

---

#### `_ensure_nota_final_records()`
**Función de generación masiva.** Recorre todas las secciones activas (estado: "abierto" o "en progreso") y verifica que cada estudiante inscrito en ellas tenga su registro de nota final. Si falta alguno, lo crea automáticamente.

> Se ejecuta con privilegios de superusuario (`sudo`) para que funcione aunque el usuario actual tenga permisos limitados.

---

#### `trigger_recalculate(student_id, section_id)`
**Función de recálculo puntual.** Recibe el ID de un estudiante y una sección.
1. Busca si ya existe un registro de nota final para esa combinación.
2. Si no existe, lo crea.
3. Llama a `action_recalculate()` para actualizar los cálculos.

> Es llamada por los "ganchos" (hooks) del archivo `grade_hook.py`.

---

#### `search_read(domain, fields, ...)`
Se ejecuta cuando la interfaz web carga la lista de notas finales. Antes de mostrar los datos, **recalcula todas las notas** de los registros visibles para asegurar que estén actualizadas.

---

#### `action_recalculate()`
**Botón de "Sincronizar Notas"** visible en el formulario de cada estudiante. También es llamado internamente por los hooks.

Para cada registro:
1. Llama a `_populate_detalle()` para sincronizar las líneas de detalle.
2. Incrementa el campo `recalc_trigger` en 1, lo que dispara la recomputación automática de `nota_final` y `promedio`.

---

#### `create(vals_list)` *(sobrescrito)*
Al crear un nuevo registro de nota final, automáticamente llama a `_populate_detalle()` para generar las líneas de detalle correspondientes a los tipos de evaluación de la sección.

---

#### `_populate_detalle()`
**Sincroniza las líneas de detalle** (`detalle_ids`) de un registro:
- Elimina las líneas cuyo tipo de evaluación ya no exista en la sección.
- Crea líneas nuevas para los tipos de evaluación que falten.

---

#### `_compute_nota_final()` *(campo calculado)*
Suma todos los **aportes** (`aporte`) de las líneas de detalle para obtener la nota final total del estudiante.  
Se recalcula automáticamente cuando cambia `recalc_trigger` o cualquier `aporte` de las líneas.

---

#### `_compute_promedio()` *(campo calculado)*
Calcula el **promedio ponderado** general: suma de (`promedio_tipo × peso`) dividido entre la suma total de pesos.  
Se recalcula automáticamente cuando cambia `recalc_trigger` o el `promedio_tipo`/`peso` de alguna línea.

---

## Archivo: `gestion_nota_final_line.py`

### Clase `NotaFinalDetalle`
**Modelo:** `gestion.nota.final.detalle`

Representa **una fila de detalle** dentro de una nota final. Hay una fila por cada tipo de evaluación configurado en la sección (ej: Exámenes, Tareas, Asistencia, Participación).

---

### Campos del modelo

| Campo | Tipo | Descripción |
|---|---|---|
| `nota_final_id` | Many2one → `gestion.nota.final` | La nota final a la que pertenece este detalle |
| `tipo_evaluacion` | Many2one → `gestion.tipo.evaluacion` | El tipo de evaluación (ej: "Exámenes", "Asistencia") |
| `peso` | Float (relacionado) | El porcentaje asignado a ese tipo (se copia de `gestion.tipo.evaluacion`) |
| `promedio_tipo` | Float (calculado) | El promedio del estudiante en ese tipo específico (escala 0-10) |
| `aporte` | Float (calculado) | Cuántos puntos aporta este tipo a la nota final (`promedio_tipo × peso`) |

---

### Métodos del modelo

#### `_compute_promedio()` *(campo calculado principal)*
Es el **corazón del cálculo**. Se ejecuta automáticamente cuando cambia `recalc_trigger`. Determina qué tipo de evaluación es la línea y llama al método correcto:

- Si el nombre contiene **"asistencia"** → llama a `_calcular_desde_asistencia()`
- Si el nombre contiene **"participacion"** o **"participación"** → llama a `_calcular_desde_participacion()`
- En cualquier otro caso → llama a `_calcular_desde_calificaciones()`

---

#### `_calcular_desde_asistencia(student, section)`
Calcula el promedio de asistencia del estudiante en la sección.

1. Busca todas las sesiones de asistencia **confirmadas** de esa sección.
2. Cuenta cuántas sesiones marcó el estudiante como **presente**.
3. Formula: `(sesiones presentes / total de sesiones) × 10.0`
4. Guarda el resultado en `promedio_tipo` y calcula el `aporte`.

---

#### `_calcular_desde_participacion(student, section)`
Calcula el promedio de participación en clase.

1. Verifica que el módulo de participación exista en el sistema.
2. Busca todas las sesiones de participación de esa sección.
3. Cuenta cuántas veces el estudiante marcó `participo = True`.
4. Formula: `(veces que participó / total de sesiones) × 10.0`
5. Guarda el resultado en `promedio_tipo` y calcula el `aporte`.

---

#### `_calcular_desde_calificaciones()`
Calcula el promedio de calificaciones de actividades del estudiante para ese tipo de evaluación.

1. Busca en `grade.grade` las calificaciones del estudiante en actividades de esa sección y ese tipo de evaluación.
2. Calcula el promedio aritmético simple de todas las notas encontradas.
3. Guarda el resultado en `promedio_tipo` y calcula el `aporte`.

---

## Archivo: `grade_hook.py`

Este archivo contiene **ganchos (hooks)**: clases que heredan modelos de otros módulos para "escuchar" cambios y disparar el recálculo de notas finales automáticamente. El profesor no necesita hacer nada manual; el sistema reacciona solo.

> Todos los llamados a `trigger_recalculate` se hacen sin `sudo()` porque ese método ya lo aplica internamente.

---

### Clase `GradeHook` — hereda `grade.grade`
Escucha cambios en las **calificaciones** de actividades.

| Método | Cuándo se ejecuta | Qué hace |
|---|---|---|
| `create` | Al registrar una nueva nota | Recalcula la nota final del estudiante en esa sección |
| `write` | Al modificar una nota existente | Recalcula la nota del estudiante. Si cambió de estudiante o sección, también recalcula la combinación anterior |
| `unlink` | Al eliminar una nota | Guarda los datos del registro antes de borrarlo y luego recalcula |

---

### Clase `ActivityHook` — hereda `gestion.activity`
Escucha cambios en las **actividades académicas** (tareas, exámenes, etc.).

| Método | Cuándo se ejecuta | Qué hace |
|---|---|---|
| `write` | Al modificar una actividad | Si cambia el tipo de evaluación o la sección, recalcula las notas de todos los estudiantes afectados (tanto en la sección nueva como en la anterior) |

---

### Clase `AttendanceHook` — hereda `gestion.attendance`
Escucha cambios en las **sesiones de asistencia**.

| Método | Cuándo se ejecuta | Qué hace |
|---|---|---|
| `write` | Al modificar la sesión (ej: cambiar a "confirmado") | Recalcula las notas de todos los estudiantes de esa sección |
| `unlink` | Al eliminar una sesión de asistencia | Guarda la sección y recalcula tras el borrado |

---

### Clase `AttendanceLineHook` — hereda `gestion.attendance_line`
Escucha cambios en las **líneas individuales de asistencia** (las marcas de "presente/ausente" por estudiante).

| Método | Cuándo se ejecuta | Qué hace |
|---|---|---|
| `create` | Al agregar una línea en una sesión confirmada | Recalcula la nota del estudiante correspondiente |
| `write` | Al cambiar el estado "presente" de un estudiante | Recalcula la nota. Si cambió el estudiante, también recalcula el anterior |
| `unlink` | Al eliminar una línea de asistencia | Recalcula la nota del estudiante afectado |

> Solo actúa cuando la sesión de asistencia está en estado `confirmed`.

---

### Clase `ParticipacionHook` — hereda `gestion.participacion.clase`
Escucha cambios en las **sesiones de participación en clase**.

| Método | Cuándo se ejecuta | Qué hace |
|---|---|---|
| `write` | Al modificar la sesión (ej: cambiar de sección) | Recalcula notas de estudiantes en la sección nueva y en la anterior |
| `unlink` | Al eliminar una sesión de participación | Recalcula las notas de todos los estudiantes de esa sección |

---

### Clase `ParticipacionLineHook` — hereda `gestion.participacion.line`
Escucha cambios en las **marcas individuales de participación** por estudiante.

| Método | Cuándo se ejecuta | Qué hace |
|---|---|---|
| `create` | Al agregar una línea de participación | Recalcula la nota del estudiante |
| `write` | Al marcar/desmarcar "participó" | Recalcula la nota. Si cambió el estudiante, también recalcula el anterior |
| `unlink` | Al eliminar una línea | Recalcula la nota del estudiante |

---

### Clase `TipoEvaluacionHook` — hereda `gestion.tipo.evaluacion`
Escucha cambios en la **configuración de tipos de evaluación** (los porcentajes).

| Método | Cuándo se ejecuta | Qué hace |
|---|---|---|
| `create` | Al crear un nuevo tipo de evaluación | Recalcula notas de todos los estudiantes de esa sección |
| `write` | Al cambiar el porcentaje o la sección | Recalcula notas en la sección nueva y en la anterior |
| `unlink` | Al eliminar un tipo de evaluación | Recalcula las notas de la sección afectada |

---

### Clase `SeccionHook` — hereda `gestion.seccion`
Escucha cambios en la **lista de estudiantes de una sección**.

| Método | Cuándo se ejecuta | Qué hace |
|---|---|---|
| `write` | Al agregar o quitar estudiantes de una sección | Llama a `_ensure_nota_final_records()` para crear notas a los nuevos estudiantes. También elimina los registros de nota final de estudiantes que fueron retirados |

---

## Flujo General de Recálculo

```
Profesor hace un cambio (nota, asistencia, participación, etc.)
        ↓
Hook correspondiente detecta el cambio (create/write/unlink)
        ↓
Hook llama a trigger_recalculate(student_id, section_id)
        ↓
trigger_recalculate busca o crea gestion.nota.final
        ↓
action_recalculate() incrementa recalc_trigger
        ↓
Odoo detecta el cambio y recomputa automáticamente:
  - gestion.nota.final.detalle → promedio_tipo y aporte
  - gestion.nota.final         → nota_final y promedio
        ↓
Los datos se guardan en base de datos (store=True)
```

---

## Permisos de Acceso

| Grupo | Leer | Escribir | Crear | Eliminar |
|---|---|---|---|---|
| Administración (`base.group_system`) | ✅ | ✅ | ✅ | ✅ |
| Profesor (`gestion_profesorado.group_profesor`) | ✅ | ❌ | ❌ | ❌ |
| Usuario base (`base.group_user`) | ✅ | ❌ | ❌ | ❌ |

> Los profesores solo pueden **ver** las notas finales. No pueden crearlas, modificarlas ni eliminarlas desde la interfaz.
> Las operaciones internas del sistema (hooks, recálculos) se ejecutan con privilegios de superusuario (`sudo`) para no verse bloqueadas por estos permisos.

---

## Vista de la Interfaz

La interfaz de usuario es **completamente de solo lectura** para todos los usuarios:
- No aparece el botón "Nuevo".
- No se puede editar ningún campo desde la vista de lista ni de formulario.
- El único botón disponible en el formulario es **"Sincronizar Notas"**, que fuerza un recálculo manual.
