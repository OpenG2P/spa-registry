def render_template(value, context: dict):
    """Replace {identifier} and the other tokens inside a provider payload.

    The JSON keys stay as the provider defined them.
    """
    if isinstance(value, str):
        try:
            return value.format(**context)
        except KeyError:
            return value
    if isinstance(value, dict):
        return {key: render_template(item, context) for key, item in value.items()}
    if isinstance(value, list):
        return [render_template(item, context) for item in value]
    return value
