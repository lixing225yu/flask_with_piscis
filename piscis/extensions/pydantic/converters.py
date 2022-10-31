from typing import Type

from pydantic import BaseModel
from werkzeug.datastructures import ImmutableMultiDict

from piscis.extensions.pydantic import FileField


def convert_query_params(query_params: ImmutableMultiDict,
                         model: Type[BaseModel]) -> dict:
    return {
        **query_params.to_dict(),
        **{
            key: value
            for key, value in query_params.to_dict(flat=False).items() if key in model.__fields__ and model.__fields__[key].is_complex(
            )
        },
    }


def convert_form_data_params(form, files, model: Type[BaseModel]) -> dict:
    result = {}
    if form:
        result = dict(result, **convert_query_params(form, model))
    if files:
        for key, value in files.to_dict().items():
            if key in model.__fields__:
                ext = ''
                if '.' in value.filename:
                    ext = value.filename[value.filename.rindex('.') + 1:]
                value.seek(0)
                file = FileField(name=value.filename,
                                 content_type=value.content_type,
                                 mimetype=value.mimetype,
                                 ext=ext,
                                 content=value.read())
                result[key] = file
    return result
