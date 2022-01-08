from uuid import uuid4
import uvicorn
from dataStructs import *
from database.databaseHandler import DatabaseHandler

if __name__ == "__main__":
    uvicorn.run("api.absentapi:app", host="0.0.0.0", port=8081, reload=True)

