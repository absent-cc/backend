import uvicorn
from database.databaseHandler import DatabaseHandler
from dataStructs import *
database = DatabaseHandler()

if __name__ == "__main__":
    uvicorn.run("api.v1:absent", host="0.0.0.0", port=8081, reload=True)

"""
eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJodHRwczovL2FwaS5hYnNlbnQuY2MiLCJzdWIiOiI1N2Q4M2ZjOTcwM2E4YzVhLjMwZGQxNDNjLTgzMmMtNDNhNy1iOTY2LWY4NDg4M2NkYjJmYiIsImF1ZCI6Imh0dHBzOi8vYXBpLmFic2VudC5jYyIsImV4cCI6MTY0NDU0OTUzNSwiaWF0IjoxNjQxOTU3NTM1fQ.gXvalpYjY2WQrUzbMpA4wleQij0HxRo0Y7NjPDcMWp0fLGegVVZymtxCUD0-eegwatID-nHd_Ygy08HCRipDRGb1DBQkshDZplc-5rmdWU2LowPXLJ7qzxDj2j1YAAi4ON4fsaFypqIojNRBJCdlwePp2lnk8E9BvnBafJQ_Wfye9fZTnrbq1sar6eiUCumpYzuQ2lU_GO_3C8vr_CeDWQ2_x9XVz3owrrqcUoZmA9TdGgyNFIaty8emHsAo7D2KwXRuNuJbBfyPHmuEgU68RdEwhfRcRB3wJraeWZ05aGYDESiwGCANHQ8fJofOo-D86kAFIP_nI75ys-H1jjH8w2ACy1wsA2PuIy8qUWio3mSB0-NJ3Mu15CcQpLqeMjG6LB-q8GN-wyR71N7fClnzsC0s7YyNZFvTIHw3T2DewXO7V0oMTRCfYOUtEzCYnoUiV3GzIdQczqoyy0DHUgA84ogzU4ifvmhHrOUJM-fWSnI9_GHevnEidQaN9FyTcgvm
"""

"""
{
  "first": "Roshan",
  "last": "Karim",
  "school": "NNHS",
  "grade": 10,
  "schedule": {
    "A": [
      {
        "first": "Daniel",
        "last": "Fabrizio",
        "school": "NNHS"
      }
    ],
    "ADV": [
      {
        "first": "Timothy",
        "last": "Finnegan",
        "school": "NNHS"
      },
      {
        "first": "Allison",
        "last": "Malkin",
        "school": "NNHS"
      }
    ],
    "B": [
      {
        "first": "Amy",
        "last": "Donovan",
        "school": "NNHS"
      }
    ],
    "C": [
      {
        "first": "Timothy",
        "last": "Finnegan",
        "school": "NNHS"
      }
    ],
    "D": [
      {
        "first": "Isongesit",
        "last": "Ibokette",
        "school": "NNHS"
      }
    ],
    "E": [
      {
        "first": "Amelia",
        "last": "May",
        "school": "NNHS"
      }
    ],
    "G": [
      {
        "first": "Charles",
        "last": "Rooney",
        "school": "NNHS"
      }
    ]
  }
}

"""