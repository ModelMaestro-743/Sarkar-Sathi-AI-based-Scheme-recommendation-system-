# In-memory session store keyed by phone number.
# Sessions are lost on server restart — replace with Redis for production persistence.
user_sessions: dict = {}
