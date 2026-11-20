from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import List, Optional
from pydantic import BaseModel


SQLALCHEMY_DATABASE_URL = "sqlite:///./salon.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Master(Base):
    __tablename__ = "masters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    specialization = Column(String, index=True)


Base.metadata.create_all(bind=engine)


class MasterResponse(BaseModel):
    id: int
    name: str
    specialization: str

    class Config:
        from_attributes = True


def seed_database():
    db = SessionLocal()
    if db.query(Master).count() == 0:
        masters = [
            Master(id=1, name="Михаил", specialization="Парикмахер"),
            Master(id=2, name="Марина", specialization="Парикмахер"),
            Master(id=3, name="Сергей", specialization="Парикмахер"),
            Master(id=4, name="Светлана", specialization="Колорист"),
        ]
        db.add_all(masters)
        db.commit()
    db.close()


seed_database()


app = FastAPI()


@app.get("/masters", response_model=List[MasterResponse])
def get_masters(specialization: Optional[str] = None):
    db = SessionLocal()

    if specialization:
        masters = db.query(Master).filter(Master.specialization == specialization).all()
    else:
        masters = db.query(Master).all()

    db.close()
    return masters


@app.get("/masters/{master_id}", response_model=MasterResponse)
def get_master(master_id: int):
    db = SessionLocal()
    master = db.query(Master).filter(Master.id == master_id).first()
    db.close()

    if master is None:
        raise HTTPException(status_code=404, detail="Master not found")

    return master