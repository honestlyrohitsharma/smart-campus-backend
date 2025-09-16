from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- IMPORTANT: USE YOUR REAL POSTGRESQL CREDENTIALS ---
DATABASE_URL = 'postgresql://neondb_owner:npg_3ephGM8YKoFz@ep-mute-rain-a1asl195-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
# ----------------------------------------------------

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()