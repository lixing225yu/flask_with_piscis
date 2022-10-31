from functools import wraps
from typing import Callable, Optional, Tuple, Type
from flask import request
from pydantic import BaseModel, ValidationError
from pydantic.tools import parse_obj_as
from piscis.exception import ParameterError
from .converters import convert_form_data_params, convert_query_params


def validate_path_params(func: Callable, kwargs: dict) -> Tuple[dict, list]:
    errors = []
    validated = {}
    for name, type_ in func.__annotations__.items():
        if name in {"query", "body", 'form', "return"}:
            continue
        try:
            value = parse_obj_as(type_, kwargs.get(name))
            validated[name] = value
        except ValidationError as e:
            err = e.errors()[0]
            err["loc"] = [name]
            errors.append(err)
    kwargs = {**kwargs, **validated}
    return kwargs, errors


def get_body_dict(**params):
    data = request.get_json(**params)
    if data is None and params.get("silent"):
        return {}
    return data


def handle_error(model, err):
    # field = err["loc"][0]

    # field_name = model.__fields__[field].field_info.description or field

    field = '.'.join([str(e) for e in err['loc']])
    msg = err.get('msg') or "输入不正确"

    return f'{field}:{msg}'


def validate(
        body: Optional[Type[BaseModel]] = None,
        query: Optional[Type[BaseModel]] = None,
        form: Optional[Type[BaseModel]] = None,
        show_all_errors: bool = False,
        get_json_params: Optional[dict] = None,
):
    def decorate(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            q, b, f, err, model_map = None, None, None, {}, {}
            kwargs, path_err = validate_path_params(func, kwargs)
            if path_err:
                err["path_params"] = path_err
            query_in_kwargs = func.__annotations__.get("query")
            query_model = query_in_kwargs or query
            if query_model:
                model_map["query_params"] = query_model
                query_params = convert_query_params(request.args, query_model)
                try:
                    q = query_model(**query_params)
                except ValidationError as ve:
                    err["query_params"] = ve.errors()

            body_in_kwargs = func.__annotations__.get("body")
            body_model = body_in_kwargs or body
            if body_model:
                model_map["body_params"] = body_model
                body_params = get_body_dict(**(get_json_params or {}))
                try:
                    b = body_model(**body_params)
                except TypeError:
                    return ParameterError('body类型错误')
                except ValidationError as ve:
                    err["body_params"] = ve.errors()

            form_in_kwargs = func.__annotations__.get("form")
            form_model = form_in_kwargs or form
            if form_model:
                model_map["form_params"] = form_model
                form_params = convert_form_data_params(request.form,
                                                       request.files,
                                                       form_model)
                try:
                    f = form_model(**form_params)
                except TypeError:
                    return ParameterError('form类型错误')
                except ValidationError as ve:
                    err["form_params"] = ve.errors()

            request.query_params = q
            request.body_params = b
            request.form_params = f
            if query_in_kwargs:
                kwargs["query"] = q
            if body_in_kwargs:
                kwargs["body"] = b
            if form_in_kwargs:
                kwargs["form"] = f
            if err:
                err_list = []
                try:
                    for t, err_data in err.items():
                        err_data.reverse()
                        for item in err_data:
                            err_list.append(
                                handle_error(model_map.get(t), item))
                            if not show_all_errors:
                                raise Exception('stop')
                except Exception:
                    pass
                return ParameterError('|'.join(err_list))
            res = func(*args, **kwargs)

            return res

        return wrapper

    return decorate
