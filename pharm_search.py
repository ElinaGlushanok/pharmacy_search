import os
import sys
import pygame
import requests
from adjust_ll_span import adjust_ll_span


API_KEY = '40d1649f-0493-4b70-98ba-98533de7710b'


def adjust_ll_span(address):
    toponym = geocode(address)
    if not toponym:
        return None, None
    convert = toponym["boundedBy"]["Envelope"]
    left, bottom = convert["lowerCorner"].split()
    right, top = convert["upperCorner"].split()
    width = abs(float(left) - float(right))
    height = abs(float(top) - float(bottom))
    return ",".join(toponym["Point"]["pos"].split()), f"{width/2},{height/2}"


def geocode(address):
    request = f"http://geocode-maps.yandex.ru/1.x/"
    params = {
        "apikey": API_KEY,
        "geocode": address,
        "format": "json"}
    response = requests.get(request, params=params)
    if response:
        jsresponse = response.json()
    else:
        raise RuntimeError(
            f"""Ошибка выполнения запроса:
            {request} \nHttp статус: {response.status_code} ({response.reason})""")
    features = jsresponse["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    if features:
        return features



def show_map(ll_spn, type="map", add_params=None):
    map_request = f"http://static-maps.yandex.ru/1.x/?{ll_spn}&l={type}"
    if add_params:
        map_request += "&" + add_params
    response = requests.get(map_request)
    if not response:
        sys.exit(1)
    map = "map.png"
    try:
        with open(map, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        sys.exit(2)

    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    screen.blit(pygame.image.load(map), (0, 0))
    pygame.display.flip()
    while pygame.event.wait().type != pygame.QUIT:
        continue

    pygame.quit()
    os.remove(map)


place = " ".join(sys.argv[1:])
if not place:
    print('Введите данные')
    sys.exit(0)
ll, spn = adjust_ll_span(place)
ll_spn = f"ll={ll}&spn={spn}"
show_map(ll_spn, "map", add_params=f"pt={ll}")
