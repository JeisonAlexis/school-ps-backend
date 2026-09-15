from app.modules.classroom.domain.repositories import PupitreRepository
from app.modules.classroom.domain.entities import (
    ComplementarioEntity,
    DetallePupitreEntity,
)
from app.modules.classroom.application.contracts import ClassroomEnrollmentService

ESTADO_PENDIENTE = "pendiente"
ESTADO_PAGADO = "pagado"


class PupitreService:
    def __init__(
        self,
        repositorio: PupitreRepository,
        enrollment_service: ClassroomEnrollmentService,
    ):
        self.repositorio = repositorio
        self.enrollment_service = enrollment_service

    # Obtiene el complementario de pupitre (valor parametrizado vigente)
    async def get_complementario_pupitre(
        self, nombre_complementario: str = "Pupitre"
    ) -> ComplementarioEntity | None:
        return await self.enrollment_service.get_complementary_by_name(
            nombre_complementario
        )

    def _map_to_entity(self, data) -> DetallePupitreEntity:
        return DetallePupitreEntity(
            id=data.id or 0,
            estudiante_id=data.estudiante_id,
            estado=data.estado,
            observacion=data.observacion,
        )

    async def update_payment_status(
        self,
        estudiante_id: int,
        observacion: str | None,
    ) -> DetallePupitreEntity | None:
        complementario = await self.get_complementario_pupitre()

        if not complementario:
            return None

        pupitre = await self.repositorio.get_student_desk(
            estudiante_id,
            complementario.id,
        )

        # Si el estudiante todavía no tiene pupitre,
        # el primer pago lo crea directamente como PAGADO.
        if not pupitre:
            pupitre_nuevo = await self.repositorio.create_desk(
                estudiante_id=estudiante_id,
                complementario_id=complementario.id,
                estado=ESTADO_PAGADO,
                observacion=observacion,
            )

            return self._map_to_entity(pupitre_nuevo)

        # Si ya existe, alterna el estado.
        pupitre.estado = (
            ESTADO_PENDIENTE
            if pupitre.estado == ESTADO_PAGADO
            else ESTADO_PAGADO
        )

        pupitre.observacion = observacion

        pupitre_actualizado = await self.repositorio.update_desk(pupitre)

        return self._map_to_entity(pupitre_actualizado)

    # Confirma el pago de varios pupitres de un mismo grado, retorna cantidad actualizados
    async def bulk_update_desk_states(
        self,
        grado_id: int,
        ids_estudiantes: list[int],
    ) -> dict | None:

        complementario = await self.get_complementario_pupitre()

        if not complementario:
         return None

        # Obtener todos los pupitres que ya existen para el grado
        pupitres_existentes = await self.repositorio.list_desks_by_grado_id(
            grado_id
        )

        pupitres_por_estudiante = {
            pupitre.estudiante_id: pupitre
            for pupitre in pupitres_existentes
        }

        total_actualizados = 0
        ids_no_encontrados = []

        for estudiante_id in ids_estudiantes:

            # Verificar que el estudiante pertenezca al grado
            estudiante = self.enrollment_service.get_student_by_id(
                estudiante_id
            )

            if not estudiante or estudiante.grado_id != grado_id:
                ids_no_encontrados.append(estudiante_id)
                continue

            pupitre = pupitres_por_estudiante.get(estudiante_id)

            if pupitre:
                # Ya existe → confirmar pago
                pupitre.estado = ESTADO_PAGADO

                await self.repositorio.update_desk(pupitre)

            else:
                # No existe → crear asignación y confirmar pago
                pupitre = await self.repositorio.create_desk(
                    estudiante_id=estudiante_id,
                    complementario_id=complementario.id,
                    estado=ESTADO_PAGADO,
                    observacion=None,
                )

            total_actualizados += 1

        return {
            "total_actualizados": total_actualizados,
            "ids_no_encontrados": ids_no_encontrados,
        }

    # Lista los pupitres de un grupo de estudiantes
    async def get_desks_by_students(
        self, estudiante_ids: list[int]
    ) -> list[DetallePupitreEntity] | None:
        pupitres = await self.repositorio.list_desks_by_students(estudiante_ids)

        if not pupitres:
            return None

        return [self._map_to_entity(p) for p in pupitres]

    # Obtiene el pupitre de un estudiante
    async def get_desk_by_student(
        self, estudiante_id: int
    ) -> DetallePupitreEntity | None:
        complementario = await self.get_complementario_pupitre()

        if not complementario:
            return None

        pupitre = await self.repositorio.get_student_desk(
            estudiante_id, complementario.id
        )

        return self._map_to_entity(pupitre) if pupitre else None
