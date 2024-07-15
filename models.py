from extensions import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

class Meme(Base):
    __tablename__ = "memes"

    id = Column(Integer, primary_key=True)
    text = Column(String(64))
    image_uuid = Column(String(128))