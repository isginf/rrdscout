import settings
from app import app

@app.template_filter()
def translate(data_source, device=None):
    """
    translate data sources according to settings
    """
    translated_value = ""

    if device and settings.DEVICE_TRANSLATION.get(device) and \
       settings.DEVICE_TRANSLATION.get(device).get(data_source):
        translated_value = settings.DEVICE_TRANSLATION.get(device).get(data_source)
    else:
        translated_value = settings.DATA_SOURCE_TRANSLATION.get(data_source, data_source)
        
    return translated_value
