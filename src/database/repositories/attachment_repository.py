"""Attachment repository."""
from __future__ import annotations

from sqlalchemy.orm import Session

from src.database.models.attachment import Attachment
from src.database.repositories.base_repository import BaseRepository


class AttachmentRepository(BaseRepository[Attachment]):
    def __init__(self, session: Session) -> None:
        super().__init__(Attachment, session)

    def get_by_task(self, task_id: int) -> list[Attachment]:
        return (
            self.session.query(Attachment)
            .filter(Attachment.task_id == task_id)
            .order_by(Attachment.created_at.desc())
            .all()
        )
