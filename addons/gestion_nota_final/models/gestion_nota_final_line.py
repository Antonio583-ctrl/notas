from odoo import models, fields, api


class NotaFinalDetalle(models.Model):
    _name = 'nota.final.detalle'
    _description = 'Detalle de Nota Final'

    nota_final_id = fields.Many2one(
        'nota.final',
        string='Nota Final',
        ondelete="cascade",
        required=True,
    )

    tipo_evaluacion = fields.Many2one(
        'gestion.tipo.evaluacion',
        string='Tipo de Evaluación',
        ondelete="cascade",
        required=True,
    )

    peso = fields.Float(
        string='Peso',
        related='tipo_evaluacion.porcentaje',
        store=True,
        readonly=True,
    )

    promedio_tipo = fields.Float(
        string='Promedio Tipo',
        compute='_compute_promedio',
        store=True,
    )

    aporte = fields.Float(
        string='Aporte',
        compute='_compute_promedio',
        store=True,
    )

    @api.depends('tipo_evaluacion', 'nota_final_id.student_id', 'nota_final_id.section_id')
    def _compute_promedio(self):
        Grade = self.env['grade.grade']
        for rec in self:
            # Inicializa los valores en cero.
            # Si no hay datos válidos, la línea quedará en 0.
            rec.promedio_tipo = 0.0
            rec.aporte = 0.0
            
            #Si la línea no tiene nota final asociada o no tiene tipo de evaluación, no hace más nada.
            #Se salta esa línea.
            if not rec.nota_final_id or not rec.tipo_evaluacion:
                continue
            
            # Toma el estudiante y la sección desde la nota final.    
            # Si falta alguno, tampoco sigue.
            student = rec.nota_final_id.student_id
            section = rec.nota_final_id.section_id
            if not student or not section:
                continue
            
            grades = Grade.search([
                ('student_id', '=', student.id),
                ('activity_id.section_id', '=', section.id),
                ('activity_id.tipo_evaluacion_id', '=', rec.tipo_evaluacion.id),
            ])
            
            # Si no encontró ninguna nota, no calcula nada y deja los valores en 0.
            if not grades:
                continue
            
            score_list = grades.mapped('score')
            promedio = sum(score_list) / len(score_list) if score_list else 0.0
            rec.promedio_tipo = promedio
            rec.aporte = promedio * (rec.peso or 0.0)