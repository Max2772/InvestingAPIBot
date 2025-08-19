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

async def fetch_api_data(client, url, message):
    try:
        response = await client.get(url)
        if response.status_code == 404:
            await message.answer("Sorry, this asset doesn't exist.")
            return None
        response.raise_for_status()
        return response.json()
    except Exception as e:
        await message.answer(f"Error fetching data: {str(e)}")
        return None