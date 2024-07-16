from pydantic import BaseModel
from pydantic import PlainValidator, PlainSerializer, errors, WithJsonSchema
from typing_extensions import Annotated, Any
from typing import List
from fastapi.responses import ORJSONResponse
import json
import logging

logger = logging.getLogger('uvicorn.error')

def hex_bytes_validator(o: Any) -> bytes:
    if isinstance(o, bytes):
        return o
    elif isinstance(o, bytearray):
        return bytes(o)
    elif isinstance(o, str):
        return bytes.fromhex(o)
    raise errors.BytesError()

HexBytes = Annotated[bytes, PlainValidator(hex_bytes_validator), PlainSerializer(lambda b: b.hex()), WithJsonSchema({'type': 'string'})]

class MemePydantic(BaseModel):
    id : int
    text : str
    image_uuid : str

class Meme_Imagebytes(MemePydantic):
    image_bytes : HexBytes


class HttpErrors(BaseModel):
    status: int
    detail: str

    def render(self) -> ORJSONResponse:
        logger.info(f"Returned error response: status: {self.status}, msg: {self.content}")
        return ORJSONResponse(
            status_code=self.status,
            content=self.content()
        )

    def content(self):
        return {'detail': self.detail}

    def json_content(self):
        return json.dumps(self.content())


class BadRequest(HttpErrors):
    status : int = 400

class NotFound(HttpErrors):
    status : int = 404

class InternalServerError(HttpErrors):
    status : int = 500

class UnprocessableEntity(BaseModel):
    status : int = 422
    detail: List[dict]

    def render(self) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=self.status,
            content={'detail': self.detail}
        )