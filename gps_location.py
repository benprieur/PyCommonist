'''
    gps_location
'''
import traceback

def _get_if_exist(data, key):
    """ get_files """
    if key in data:
        return data[key]
    return None

def convert_to_degress(value):
    """ convert_to_degress """ 
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)
    return d + (m / 60.0) + (s / 3600.0)

def get_exif_location(exif_data):
    """ get_exif_location """ 
    lat = None
    lon = None
    heading = 0
    gps_latitude = _get_if_exist(exif_data, 'GPS GPSLatitude')
    gps_latitude_ref = _get_if_exist(exif_data, 'GPS GPSLatitudeRef')
    gps_longitude = _get_if_exist(exif_data, 'GPS GPSLongitude')
    gps_longitude_ref = _get_if_exist(exif_data, 'GPS GPSLongitudeRef')
    gps_direction = _get_if_exist(exif_data, 'GPS GPSImgDirection')
    gps_direction_ref = _get_if_exist(exif_data, 'GPS GPSImgDirectionRef')
    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
        lat = convert_to_degress(gps_latitude)
        if gps_latitude_ref.values[0] != 'N':
            lat = 0 - lat
        lon = convert_to_degress(gps_longitude)
        if gps_longitude_ref.values[0] != 'E':
            lon = 0 - lon
    if str(gps_direction_ref) == "T": # Real North
        try:
            tab = str(gps_direction).split('/')
            tab[0] = int(tab[0])
            tab[1] = int(tab[1])
            heading = tab[0]/tab[1]
        except ValueError:
            traceback.print_exc()
    return lat, lon, heading
