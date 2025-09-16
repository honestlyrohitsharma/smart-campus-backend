from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- IMPORTANT: USE YOUR LIVE NEON DATABASE URL ---
# This should be the full connection string you have set as an environment variable on Render.
# We will read it from the environment in the main.py, but this is a local fallback.
DATABASE_URL = "postgresql://neondb_owner:npg_3ephGM8YKoFz@ep-mute-rain-a1asl195-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# --- THE CRUCIAL FIX IS ADDED HERE ---
# pool_pre_ping=True tells SQLAlchemy to check if the connection is still alive before using it.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
# ------------------------------------

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

