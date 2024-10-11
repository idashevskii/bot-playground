from typing import List, Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text

from . import database


class BaseOrmModel(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)


class World(BaseOrmModel):
    __tablename__ = "world"

    title: Mapped[str] = mapped_column()
    plugin: Mapped[str] = mapped_column()
    config: Mapped[Optional[str]] = mapped_column(Text)
    stages: Mapped[List["Stage"]] = relationship(back_populates="world")


class Stage(BaseOrmModel):
    __tablename__ = "stage"

    title: Mapped[str] = mapped_column()
    world_id: Mapped[int] = mapped_column(ForeignKey("world.id"))
    code: Mapped[str] = mapped_column()
    steps: Mapped[List["Step"]] = relationship(back_populates="stage")
    world: Mapped["World"] = relationship(back_populates="stages")


class Step(BaseOrmModel):
    __tablename__ = "step"

    stage_id: Mapped[int] = mapped_column(ForeignKey("stage.id"))
    state: Mapped[str] = mapped_column(Text)
    actions: Mapped[str] = mapped_column(Text)
    logs: Mapped[str] = mapped_column(Text)
    interactions: Mapped[str] = mapped_column(Text)
    stage: Mapped["Stage"] = relationship(back_populates="steps")


def create_all_tables():
    BaseOrmModel.metadata.create_all(bind=database.engine)
