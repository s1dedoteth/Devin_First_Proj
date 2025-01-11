from app.main import app, engine, SessionLocal
from app.models import Base

print('Recreating database...')
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print('Database recreated.')
