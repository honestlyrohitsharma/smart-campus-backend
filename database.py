import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- Smart Database Connection ---
# This code automatically switches between your live and local databases.

# 1. LIVE DATABASE (when deployed on Render):
# Your code will read the secret DATABASE_URL you set up in the Render environment variables.
# Based on your screenshot, that URL is:
# "postgresql://neondb_owner:npg_3ephGM8YKoFz...tech/neondb?sslmode=require"

# 2. LOCAL DATABASE (when running on your PC):
# If the code is not on Render, it will use this local fallback URL.
# IMPORTANT: Replace 'YOUR_LOCAL_PASSWORD' with your actual local PostgreSQL password.
LOCAL_DATABASE_URL = "postgresql://neondb_owner:npg_3ephGM8YKoFz@ep-mute-rain-a1asl195-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# This line gets the live URL from Render, or uses the local one if it's not found.
DATABASE_URL = os.environ.get("DATABASE_URL", LOCAL_DATABASE_URL)


# The 'pool_pre_ping=True' setting is essential for stable connections to cloud databases like Neon.
# It prevents the "SSL connection has been closed unexpectedly" error.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

