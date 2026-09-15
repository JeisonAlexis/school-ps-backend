from app.core.db import SessionDep
from app.modules.classroom.infrastructure.repository import PupitreRepositoryImpl
from app.modules.classroom.infrastructure.enrollment_adapter import (
    ClassroomEnrollmentAdapter,
)
from app.modules.classroom.domain.service import PupitreService
from app.modules.classroom.schemas.response import PupitreStudentOutSchema


class GetPupitreByStudent:
    def __init__(self, session: SessionDep):
        self.repository = PupitreRepositoryImpl(session=session)
        self.student_provider = ClassroomEnrollmentAdapter(session=session)
        self.service = PupitreService(
            repositorio=self.repository,
            enrollment_service=self.student_provider,
        )

    async def execute(
        self, documento_estudiante: str
    ) -> PupitreStudentOutSchema | None:
        estudiante = self.student_provider.get_student_by_document(
            documento_estudiante
        )

        # El estudiante no existe
        if not estudiante:
            return None

        grado = self.student_provider.get_grade(estudiante.grado_id)

        pupitre = await self.service.get_desk_by_student(estudiante.id)

        # El estudiante existe, pero todavía no tiene pupitre asignado
        if not pupitre:
            return PupitreStudentOutSchema(
                id=None,
                estudiante_id=estudiante.id,
                nombre_estudiante=estudiante.nombre,
                documento=estudiante.documento,
                grado=grado.nombre if grado else "Sin grado",
                docente_titular=grado.docente_titular if grado else None,
                estado="sin_asignar",
                observacion=None,
            )

        # El estudiante sí tiene pupitre asignado
        return PupitreStudentOutSchema(
            id=pupitre.id,
            estudiante_id=estudiante.id,
            nombre_estudiante=estudiante.nombre,
            documento=estudiante.documento,
            grado=grado.nombre if grado else "Sin grado",
            docente_titular=grado.docente_titular if grado else None,
            estado=pupitre.estado,
            observacion=pupitre.observacion,
        )