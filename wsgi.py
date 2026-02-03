from app.main import app

# This file is the entry point for WSGI servers like PythonAnywhere
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
