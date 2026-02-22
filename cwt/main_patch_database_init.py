from cwt.core.database import initialize_database

# Ensure persistent database is available before GUI or state logic
initialize_database()