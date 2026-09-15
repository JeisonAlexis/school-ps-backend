from app.core.db import SessionDep
from app.modules.classroom.infrastructure.repository import PupitreRepositoryImpl
from app.modules.classroom.infrastructure.enrollment_adapter import (
    ClassroomEnrollmentAdapter,
)
from app.modules.classroom.domain.service import PupitreService
from app.modules.classroom.schemas.response import PupitreStudentOutSchema


class GetPupitresByGrade:
    def __init__(self, session: SessionDep):
        self.repository = PupitreRepositoryImpl(session=session)
        self.students_provider = ClassroomEnrollmentAdapter(session=session)
        self.service = PupitreService(
            repositorio=self.repository,
            enrollment_service=self.students_provider,
        )

    async def execute(self, grado_id: int) -> list[PupitreStudentOutSchema] | None:
        estudiantes = self.students_provider.get_students_by_grade(grado_id)

        if not estudiantes:
            return None

        estudiantes_map = {
            e.id: e for e in estudiantes
            if e.id is not None
        }

        estudiante_ids = list(estudiantes_map.keys())

        pupitres = await self.service.get_desks_by_students(estudiante_ids)

        pupitres_map = {
            pupitre.estudiante_id: pupitre
            for pupitre in (pupitres or [])
        }

        grado = self.students_provider.get_grade(grado_id)

        return [
            PupitreStudentOutSchema(
                id=(
                    pupitres_map[e.id].id
                    if e.id in pupitres_map
                    else None
                ),
                estudiante_id=e.id,
                nombre_estudiante=e.nombre,
                documento=e.documento,
                grado=grado.nombre if grado else "Sin grado",
                docente_titular=grado.docente_titular if grado else None,
                estado=(
                    pupitres_map[e.id].estado
                    if e.id in pupitres_map
                    else "sin_asignar"
                ),
                observacion=(
                    pupitres_map[e.id].observacion
                    if e.id in pupitres_map
                    else None
                ),
            )
            for e in estudiantes
        ]