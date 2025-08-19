from src.config import API_BASE_URL


def profit_emoji(value):
    return ' 📈' if value > 0 else ' 📉' if value < 0 else ''

def profit_sign(value):
    return '+' if value > 0 else ''

def get_api_url(asset_type: str, asset_name: str, app_id: int = None):
    return (
        f"{API_BASE_URL}/{asset_type}/{asset_name}"
        if app_id is None else
        f"{API_BASE_URL}/{asset_type}/{app_id}/{asset_name}"
    )