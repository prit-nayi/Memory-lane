from fastapi import FastAPI

app = FastAPI(
    title ="Memory Lane API",
    description="Visitor photo slideshow Application ",
    version ="1.0.0"
)

@app.get("/")
def root():
    return{
        "message":"Welcome to Memory Lane Api"
    }

@app.get("/health")
def health():
    return{
        "status":"healthy",
        "Application":"Memory Lane"
    }
    
    