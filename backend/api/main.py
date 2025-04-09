from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import data_product, intent, workflow
from database.database import init_db

import uvicorn

app = FastAPI()

# Initialize Database
init_db()

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(data_product.router)
app.include_router(intent.router)
app.include_router(workflow.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
