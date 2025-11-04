from news_backend.database import engine, Base
from news_backend import models

# Create all tables
Base.metadata.create_all(bind=engine)

print("Database initialized!")
