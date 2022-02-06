# abSENT - Notifications for NPS students. 
Push notifications for NPS students, informing them of absent teachers. The solution to the absent list problem.

![abSENT Github Banner](https://github.com/absent-cc/branding/blob/main/assets/banner.png)

## What is it?
An SMS schoology bot that notifies NPS students when their teachers are absent. Supports both Newton high schools, [Newton South](https://www.newton.k12.ma.us/nshs) & [Newton North](https://www.newton.k12.ma.us/nnhs).
abSENT uses the [Schoolopy](https://github.com/ErikBoesen/schoolopy) API wrapper to grab teacher absences from Schoology, which are processed. Alerts are then sent through FCM (Firebase Cloud Messaging) to registered users.

## How does it work?
Students sign up in our app. Their schedule is then saved as an SQLite database using 3 tables:

- One table stores students and their characteristics (name, Google subject ID, FCM device details, etc)
- Another stores teachers and their characteristics (name)
- The third table is an array of classes that maps teacher & block -> student. 

Every school day, abSENT retrives the new absence list and parses it. It then queries the SQLite database by teacher ID and block to find students who have absent teachers. These students are then notifed that their teacher is absent.

## Why?
Refreshing Schoology 20 times every morning is somewhat draining.
## Contributors
- [Kevin Yang](https://github.com/bykevinyang)
- [Roshan Karim](https://github.com/karimroshan)

Frontend design by [Leah Vashevko](https://github.com/theaquarium)

## Disclaimer:
abSENT as a project is not affiliated with any of the entities whose students it serves. We are students and have written this project just for fun, as a minor QOL improvement in the morning.

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
