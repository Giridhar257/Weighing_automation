from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# DATABASE_URL = "postgresql://postgres:Qwert585@localhost:5432/weight_tracking"
DATABASE_URL = "postgresql://neondb_owner:npg_vkGDa7Uj0uIN@ep-calm-snow-ap6t9z63-pooler.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()