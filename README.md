# abSENT - Notifications for NPS students. 
Push notifications for NPS students, informing them of absent teachers. The solution to the absent list problem.

![abSENT Github Banner](https://github.com/absent-cc/branding/blob/main/assets/banner.svg)

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
