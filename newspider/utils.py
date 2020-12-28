def safe_cast(obj, dtype, fallback=None):
    try:
        return dtype(obj)
    except (TypeError, ValueError):
        return fallback
