from abc import ABC, abstractmethod

from app.modules.classroom.infrastructure.models import DetallePupitre


class PupitreRepository(ABC):

    @abstractmethod
    async def get_student_desk(
        self, estudiante_id: int, complementario_id: int
    ) -> DetallePupitre | None:
        pass

    @abstractmethod
    async def create_desk(
        self,
        estudiante_id: int,
        complementario_id: int,
        estado: str,
        observacion: str | None = None,
    ) -> DetallePupitre:
        pass

    @abstractmethod
    async def update_desk(
        self, pupitre: DetallePupitre
    ) -> DetallePupitre:
        pass

    async def list_desks_by_students(
        self, estudiante_ids: list[int]
    ) -> list[DetallePupitre]:
        pass

    @abstractmethod
    async def list_desks_by_grado_id(
        self, grado_id: int
    ) -> list[DetallePupitre]:
        pass

    @abstractmethod
    async def bulk_update_desk_states(
        self, pupitres: list[DetallePupitre]
    ) -> int:
        pass