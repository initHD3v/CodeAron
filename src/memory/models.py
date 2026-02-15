from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional
from src.core.config import settings

class CodeSymbol(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    type: str  # Class, Function, Variable
    file_path: str
    line_start: int
    line_end: int
    signature: str
    content: str  # Bagian kode terkait

engine = create_engine(f"sqlite:///{settings.DB_PATH}")

def init_db():
    SQLModel.metadata.create_all(engine)

def save_symbol(symbol: CodeSymbol):
    with Session(engine) as session:
        session.add(symbol)
        session.commit()
