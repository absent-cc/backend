
# 🛠️ Get Started
## Requirements
- [Schoology](https://www.schoology.com/) API creds
- [PostgreSQL] 12+ installaton
- - Database setup (see below)
- [Python 3.8+](https://www.python.org/downloads/)

## Config Files
abSENT consists of 2 config files:
- [```config.ini```](
- [```testing_config.ini```](

We've included templates for both of these files. Fill them in with the appropriate values.
## Database Setup
- Install and Setup PostgresSQL 12+
- Create a new database called absent[^1]
- Install [alembic](https://alembic.sqlalchemy.org/en/latest/)
- Generate the tables using the following commands in shell:
    - Run ```alembic revision --autogenerate -m 'initial'```
    - Run ```alembic upgrade head```
- The database should now be setup now!

[^1]: You can call the database anything, but make sure to change the name in [```config.ini```](

Notes: 
- By default, abSENT uses a postgres DB caled absent, running on port 5432. If you encounter issues, try changing the server address and port in [```src/database/database.py```]()


## Running it
To run abSENT, run the following command in your terminal, in the root directry:

```python -m src.dev```