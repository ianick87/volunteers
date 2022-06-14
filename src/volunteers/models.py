from email.policy import default
from typing import Text
import uuid
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID

import sqlalchemy_aurora_data_api

sqlalchemy_aurora_data_api.register_dialects()

Base = declarative_base()


class Volunteers(Base):
    __tablename__ = "volunteers"
    id = Column(UUID(as_uuid=True),
                primary_key=True)
    name = Column(String(30))
    description = Column(String)
    img = Column(String(200))

    def __repr__(self):
        return f"Volunteer(id={self.id!r}, name={self.name!r})"
