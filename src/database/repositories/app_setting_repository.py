"""AppSetting repository — key/value settings store."""
from __future__ import annotations

from sqlalchemy.orm import Session

from src.database.models.app_setting import AppSetting
from src.database.repositories.base_repository import BaseRepository


class AppSettingRepository(BaseRepository[AppSetting]):
    def __init__(self, session: Session) -> None:
        super().__init__(AppSetting, session)

    def get(self, key: str) -> str | None:
        row = self.session.query(AppSetting).filter(AppSetting.key == key).first()
        return row.value if row else None

    def set(self, key: str, value: str | None) -> AppSetting:
        row = self.session.query(AppSetting).filter(AppSetting.key == key).first()
        if row is None:
            row = AppSetting(key=key, value=value)
            self.session.add(row)
        else:
            row.value = value
        self.session.flush()
        return row

    def get_all_as_dict(self) -> dict[str, str | None]:
        rows = self.session.query(AppSetting).all()
        return {r.key: r.value for r in rows}
