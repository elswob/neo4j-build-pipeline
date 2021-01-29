from typing import Dict, List, Union

from pydantic import BaseModel, ValidationError, validator

class PropertyScalar(BaseModel):
    doc: str
    type: str


class PropertyArray(BaseModel):
    doc: str
    items: PropertyScalar
    type: str = "array"


class MetaNodeMetaField(BaseModel):
    id: str
    name: str
    class Config:
        fields = {"id": "_id", "name": "_name"}


class MetaNode(BaseModel):
    doc: str
    properties: Dict[str, Union[PropertyScalar, PropertyArray]]
    required: List[str]
    index: str
    meta: MetaNodeMetaField


class MetaRel(BaseModel):
    doc: str
    properties: Dict[str, Union[PropertyScalar, PropertyArray]]
    required: List[str]

    # @validator("required")
    # def source_target_in_required(cls, v):
    #     if not {"source", "target"}.issubset(set(v)):
    #         raise ValidationError("fields `source` and `target` must exist")
    #     return v
