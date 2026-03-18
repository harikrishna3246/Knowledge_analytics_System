# Knowledge Analytics System

This is the backend for the Knowledge Analytics System.

## Setup

1.  Navigate to the `backend` directory.
2.  Create a virtual environment: `python -m venv venv`
3.  Activate the virtual environment.
4.  Install dependencies: `pip install fastapi uvicorn pymongo python-dotenv certifi dnspython pyjwt`

### MongoDB Atlas (Cloud)

- Update `backend/.env` with your Atlas connection string. Example:
  ```
  MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
  ```
- Ensure your Atlas cluster has an IP whitelist entry (e.g. `0.0.0.0/0` for testing) and the user exists.

5.  Run the server: `uvicorn main:app --reload`
