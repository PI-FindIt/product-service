from sqlmodel import create_engine, Session

# Pode ser MongoDB, ou PostgreSQL
DATABASE_URL = "TODO"
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
