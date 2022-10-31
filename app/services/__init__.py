def gen_paged_data(page, page_size, total, items):
    return {"page": page, "page_size": page_size, "details": items, "total": total}


def gen_option_data(lst, label_attr, value_attr):
    return [{'label': getattr(lst, label_attr), 'value': getattr(item, value_attr)} for item in lst]
