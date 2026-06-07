from odoo import api, fields, models


class NotaFinal(models.Model):
    _name = 'gestion.nota.final'
    _description = 'Nota final de un estudiante en una sección'
    _rec_name = 'student_full_name'
    _order = 'section_id asc, student_id asc'

    student_id = fields.Many2one(
        'gestion.student',
        string='Estudiante',
        required=True,
        ondelete='cascade',
    )
    section_id = fields.Many2one(
        'gestion.seccion',
        string='Sección',
        required=True,
        ondelete='cascade',
    )
    subject_id = fields.Many2one(
        'gestion.materia',
        string='Materia',
        related='section_id.subject_id',
        store=True,
        readonly=True,
    )
    periodo_academico = fields.Char(
        string='Período Académico',
        related='subject_id.periodo_academico',
        store=True,
        readonly=True,
    )
    teacher_id = fields.Many2one(
        'gestion.teacher',
        string='Profesor',
        related='section_id.teacher_id',
        store=True,
        readonly=True,
    )
    section_state = fields.Selection(
        related='section_id.state',
        store=True,
        readonly=True,
        string='Estado de la sección',
    )
    student_full_name = fields.Char(
        string='Nombre completo',
        compute='_compute_student_name',
        store=True,
        readonly=True,
    )
    student_nombre = fields.Char(
        string='Nombre',
        compute='_compute_student_name',
        store=True,
        readonly=True,
    )
    student_apellido = fields.Char(
        string='Apellido',
        compute='_compute_student_name',
        store=True,
        readonly=True,
    )
    nota_final = fields.Float(
        string='Nota Final',
        compute='_compute_nota_final',
        store=True,
    )
    promedio = fields.Float(
        string='Promedio',
        compute='_compute_promedio',
        store=True,
    )
    detalle_ids = fields.One2many(
        'gestion.nota.final.line',
        'nota_final_id',
        string='Detalle de evaluaciones',
    )
    _sql_constraints = [
        (
            'unique_student_section',
            'unique(student_id, section_id)',
            'Ya existe una nota final para este estudiante en esta sección.',
        ),
    ]

    @api.depends('student_id.name')
    def _compute_student_name(self):
        """Crea el nombre completo y separa nombre/apellido."""
        for rec in self:
            rec.student_full_name = ''
            rec.student_nombre = ''
            rec.student_apellido = ''
            if rec.student_id and rec.student_id.name:
                full_name = rec.student_id.name.strip()
                rec.student_full_name = full_name
                parts = full_name.split()
                rec.student_nombre = parts[0] if parts else ''
                rec.student_apellido = ' '.join(parts[1:]) if len(parts) > 1 else ''

    @api.depends('detalle_ids.aporte')
    def _compute_nota_final(self):
        """Suma los aportes de cada línea para obtener la nota final."""
        for rec in self:
            rec.nota_final = float(sum(rec.detalle_ids.mapped('aporte')) or 0.0)

    @api.depends('detalle_ids.promedio_tipo')
    def _compute_promedio(self):
        """Calcula el promedio de los tipos de evaluación disponibles."""
        for rec in self:
            lines = rec.detalle_ids
            rec.promedio = float(sum(lines.mapped('promedio_tipo')) / len(lines)) if lines else 0.0

    def _ensure_detalle_lines(self):
        """Asegura que existan líneas `gestion.nota.final.line` para cada `gestion.tipo.evaluacion`

        Busca los tipos de evaluación asociados a la `section_id` y crea una línea por tipo
        si no existe ya. Esto permite que los cálculos de `promedio` y `nota_final` funcionen.
        """
        Tipo = self.env['gestion.tipo.evaluacion']
        Line = self.env['gestion.nota.final.line']
        for rec in self:
            if not rec.section_id or not rec.student_id:
                continue
            tipos = Tipo.search([('seccion_id', '=', rec.section_id.id)])
            existing = rec.detalle_ids.mapped('tipo_evaluacion_id.id')
            for tipo in tipos:
                if tipo.id not in existing:
                    Line.create({
                        'nota_final_id': rec.id,
                        'tipo_evaluacion_id': tipo.id,
                    })

    @api.model_create_multi
    def create(self, vals_list):
        """Al crear notas finales, poblar automáticamente las líneas de detalle."""
        records = super().create(vals_list)
        for rec in records:
            rec._ensure_detalle_lines()
        return records

    def write(self, vals):
        """Al actualizar sección o estudiante, refrescar las líneas de detalle."""
        res = super().write(vals)
        if 'section_id' in vals or 'student_id' in vals:
            for rec in self:
                rec._ensure_detalle_lines()
        return res
