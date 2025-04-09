from typing import Tuple
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
from pathlib import Path
import time
import csv
import shutil
from urllib.parse import quote

from database.database import SessionLocal, init_db
from models import DataProduct

router = APIRouter()

MAX_FILENAME_LENGTH = 50
UPLOAD_DIR = "datasets"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_folder_hierarchy(path:Path):
    if path != Path(UPLOAD_DIR):
        if path.parent != Path(UPLOAD_DIR):
            create_folder_hierarchy(path.parent)
        path.mkdir(exist_ok=True)

def get_root_folder(folder_path:Path) -> Path:
    if folder_path.parent == Path(UPLOAD_DIR):
        return folder_path
    else:
        return get_root_folder(folder_path.parent)
    
def format_path(raw_path:str) ->Path:
    bound = int(MAX_FILENAME_LENGTH/2)
    parts = Path(raw_path).parts
    newparts = []
    for part in parts:
        qpart = quote(part)
        if len(qpart) > MAX_FILENAME_LENGTH:
            qpart = qpart[:bound] + "..." + qpart[-bound:]
        newparts.append(qpart)
    return Path(*newparts)

def process_file(file: UploadFile)->Tuple[str,int,float, Path]:
    file_path = Path(UPLOAD_DIR).joinpath(format_path(file.filename))
    print(file_path)

    # Save file
    create_folder_hierarchy(file_path.parent)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    size = file_path.stat().st_size / (1024 * 1024)  # Convert to MB
    upload_file = file_path.stat().st_ctime

    return file.filename, size, upload_file, file_path

def create_data_product(db: Session, filename, size, upload_time, file_path:Path, attributes=[])-> DataProduct:
    data_product = DataProduct(
        name=quote(filename),
        creation_date=time.ctime(upload_time),
        size=round(size, 2),
        path=file_path.resolve().as_posix(),
        attributes=",".join(attributes)  # Store as CSV string
    )

    db.add(data_product)
    db.commit()

    return data_product


@router.post("/data-product")
async def upload_file(files: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    """Uploads a CSV file and saves metadata to the database."""
    #if not file.filename.endswith(".csv"):
        #raise HTTPException(status_code=400, detail="Only CSV files are allowed!")

    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    folder = Path(files[0].filename).parent

    print(folder, Path(UPLOAD_DIR))

    dps = []

    if folder != Path('.'): #folder import
        folder_size = 0
        for file in files:
            _, size, upload_time , file_path = process_file(file)
            folder_size += size

        folder_path = get_root_folder(file_path)

        dp = create_data_product(db, folder_path.name, folder_size, upload_time, folder_path)
        dps.append(dp)

    else: #file import
        for file in files:
            name, size, upload_time, path = process_file(file)

            if file.filename.endswith(".csv"):# Extract CSV headers
                with open(path, newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    attributes = next(reader, [])
            else:
                attributes = []

            dp = create_data_product(db, name, size, upload_time, path, attributes)
            dps.append(dp)

    return JSONResponse(status_code=200, content={
        "message": "File uploaded successfully",
        "data_product": [data_product.to_dict() for data_product in dps]
    })

@router.get("/data-products")
async def list_uploaded_files(db: Session = Depends(get_db)):
    """Returns a list of all stored CSV files."""
    data_products = db.query(DataProduct).all()
    return JSONResponse(status_code=200, content={"files": [dp.to_dict() for dp in data_products]})


@router.delete("/data-product/{data_product}")
async def delete_data_product(data_product: str, db: Session = Depends(get_db)):
    data_product_formatted = quote(data_product)
    """Deletes a data product by its name from the database and file system."""
    data_product = db.query(DataProduct).filter(DataProduct.name == data_product_formatted).first()

    if data_product is None:
        raise HTTPException(status_code=404, detail="Data product not found")

    # Delete file from the file system
    if Path(data_product.path).is_dir():
        shutil.rmtree(data_product.path)
    else:
        Path(data_product.path).unlink()

    # Delete data product from the database
    db.delete(data_product)
    db.commit()

    return JSONResponse(status_code=200, content={"message": f"Data product '{data_product}' deleted successfully"})
