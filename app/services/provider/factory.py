from app.core.config import settings
from app.services.provider.mock_provider import MockESignProvider
from app.services.provider.real_provider import RealESignProvider

def get_esign_provider():

    env = settings.ENV.upper()

    if env == "DEV":
        return MockESignProvider()

    return RealESignProvider()