from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import HTTPException
from fastapi_pagination import Page, add_pagination, LimitOffsetPage
from fastapi_pagination.ext.sqlalchemy import paginate
from starlette.responses import Response, JSONResponse
from models import Meme
from models_pydantic import MemePydantic, Meme_Imagebytes
from sqlalchemy.orm import Session
from extensions import get_db, init, get_s3_client, get_bucket
from sqlalchemy import select
from typing import Annotated
from fastapi import FastAPI, File, UploadFile, Form

from boto import upload_file, update_file, delete_file, get_file

app = FastAPI()
init()
add_pagination(app)

@app.get("/memes", response_model=Page[MemePydantic])
@app.get("/memes/limit-offset", response_model=LimitOffsetPage[MemePydantic])
async def meme_list(db: Session = Depends(get_db)) -> any:
    return paginate(db, select(Meme).order_by(Meme.id))

@app.get("/memes/{id}", response_model = Meme_Imagebytes)
async def meme_by_id(id : int , 
                     db : Session = Depends(get_db),
                     s3_client = Depends(get_s3_client),
                     bucket = Depends(get_bucket)):
    try:
        meme = db.query(Meme).where(Meme.id == id).first()
        if meme:
            meme_dict = meme.__dict__
            meme_dict["image_bytes"] = get_file(meme.image_uuid, s3_client, bucket)
            return Meme_Imagebytes.model_validate(meme_dict, from_attributes=True)
        else:
            return Response(status_code=404)
    except Exception as e:
        print(e)
        return Response(status_code=500)  

@app.post("/memes", response_class=Response)
async def meme_add(file: UploadFile,
                   text: Annotated[str, Query(max_length=64), Query(min_length=1), Form()] = "Meme Description",
                   db: Session = Depends(get_db),
                   s3_client = Depends(get_s3_client),
                   bucket = Depends(get_bucket)):
    try:
        result = upload_file(file, s3_client, bucket)
        if result:
            meme = Meme(text = text, image_uuid = result["new_image_uuid"])
            db.add(meme)
            db.commit()
            return Response(content='Successfully added meme', status_code=201)
        return Response(content='Failed to add meme', status_code=400)  
    except Exception as e:
        print(e)
        return Response(status_code=500)  

@app.put("/memes/{id}", response_class=Response)
async def meme_update_by_id(id : int,
                            new_file: UploadFile,
                            text: Annotated[str, Query(max_length=64), Query(min_length=1), Form()] = "Meme Description",
                            db: Session = Depends(get_db),
                            s3_client = Depends(get_s3_client),
                            bucket = Depends(get_bucket)):
    try:
        meme = db.query(Meme).where(Meme.id == id).first()
        if meme:
            result = update_file(meme.image_uuid, new_file, s3_client, bucket)
            if result:  
                meme.text = text
                meme.image_uuid = result['new_image_uuid']
                db.commit()
                return Response(status_code=201)
            else:
                return Response(status_code=400)
        else:
            return Response(status_code=404)
    except Exception as e:
        print(e)
        return Response(status_code=500)  
    
@app.delete("/memes/{id}", response_class=Response)
async def meme_delete_by_id(id : int,
                            db: Session = Depends(get_db),
                            s3_client = Depends(get_s3_client),
                            bucket = Depends(get_bucket)):
    try:
        meme = db.query(Meme).where(Meme.id == id).first()
        if meme:
            response = delete_file(meme.image_uuid, s3_client, bucket)
            if response["ResponseMetadata"]["HTTPStatusCode"] == 204:
                db.delete(meme)
                db.commit()
                return Response(status_code=204)
            else:
                return Response(status_code=400)
        else:
            return Response(status_code=404)
    except Exception as e:
        print(e)
        return Response(status_code=500)  
    