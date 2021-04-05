import uvicorn

from fast_api_challenge.index import app

if __name__ == "__main__":
    # Running here is generally done for local development purposes - run this python file to run the app
    # For production, the server is generally run from the command line with its own specific configuration
    uvicorn.run(app=app, host="127.0.0.1", port=5000, log_level="debug")
