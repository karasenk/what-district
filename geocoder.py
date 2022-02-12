import requests

API_KEY = '40d1649f-0493-4b70-98ba-98533de7710b'


def geocode(address):
    # Собираем запрос для геокодера.
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": API_KEY,
        "geocode": address,
        "format": "json"}

    # Выполняем запрос.
    response = requests.get(geocoder_request, params=geocoder_params)

    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()
    else:
        raise RuntimeError(
            f"""Ошибка выполнения запроса:
            {geocoder_request}
            Http статус: {response.status_code} ({response.reason})""")

    # Получаем первый топоним из ответа геокодера.
    # Согласно описанию ответа он находится по следующему пути:
    features = json_response["response"]["GeoObjectCollection"]["featureMember"]
    return features[0]["GeoObject"] if features else None


# Получаем координаты объекта по его адресу.
def get_coordinates(address):
    toponym = geocode(address)
    if not toponym:
        return None, None

    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Широта, преобразованная в плавающее число:
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    return float(toponym_longitude), float(toponym_lattitude)


# Получаем параметры объекта для рисования карты вокруг него.
def get_ll_span(address):
    toponym = geocode(address)
    if not toponym:
        return (None, None)

    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и Широта :
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    # Собираем координаты в параметр ll
    ll = ",".join([toponym_longitude, toponym_lattitude])

    # Рамка вокруг объекта:
    envelope = toponym["boundedBy"]["Envelope"]

    # левая, нижняя, правая и верхняя границы из координат углов:
    l, b = envelope["lowerCorner"].split(" ")
    r, t = envelope["upperCorner"].split(" ")

    # Вычисляем полуразмеры по вертикали и горизонтали
    dx = abs(float(l) - float(r)) / 2.0
    dy = abs(float(t) - float(b)) / 2.0

    # Собираем размеры в параметр span
    span = f"{dx},{dy}"

    return ll, span


def get_nearest_organization(point, text):
    ll = "{0},{1}".format(point[0], point[1])
    request = f"https://search-maps.yandex.ru/v1/?"
    org_params = {
        "apikey": f'dda3ddba-c9ea-4ead-9010-f43fbc15c6e3',
        'text': text,
        "lang": "ru_RU",
        "ll": ll,
        "type": 'biz'}
    response = requests.get(request, params=org_params)
    if not response:
        full_request = request + '&'.join([f'{k}={org_params[k]}' for k in org_params.keys()])
        raise RuntimeError(
            f"""Ошибка выполнения запроса:
            {full_request}
            Http статус: {response.status_code,} ({response.reason})""")
    json_response = response.json()
    organizations = json_response["features"][:10]
    # org_name = organization["properties"]["CompanyMetaData"]["name"]
    # org_address = organization["properties"]["CompanyMetaData"]["address"]
    # working_hours = organization["properties"]["CompanyMetaData"]["Hours"]["text"]
    points = []
    for org in organizations:
        if 'Hours' in org["properties"]["CompanyMetaData"].keys():
            hours = org["properties"]["CompanyMetaData"]["Hours"]["text"]
        else:
            hours = ''
        points.append([org["geometry"]["coordinates"], hours])
    return points


# Находим ближайшие к заданной точке объекты заданного типа.
def get_nearest_object(point, kind):
    ll = "{0},{1}".format(point[0], point[1])
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": API_KEY,
        "geocode": ll,
        "format": "json"}
    if kind:
        geocoder_params['kind'] = kind
    # Выполняем запрос к геокодеру, анализируем ответ.
    response = requests.get(geocoder_request, params=geocoder_params)
    if not response:
        full_request = geocoder_request + '?' + '&'.join([f'{k}={geocoder_params[k]}' for k in geocoder_params.keys()])
        raise RuntimeError(
            f"""Ошибка выполнения запроса:
            {full_request}
            Http статус: {response.status_code,} ({response.reason})""")

    # Преобразуем ответ в json-объект
    json_response = response.json()

    # Получаем первый топоним из ответа геокодера.
    # organization = json_response["features"][0]
    # Название организации.
    # org_name = organization["properties"]["CompanyMetaData"]["name"]
    # Адрес организации.
    # org_address = organization["properties"]["CompanyMetaData"]["address"]

    # Получаем координаты ответа.
    # point = organization["geometry"]["coordinates"]
    district = json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']['Components'][-1]['name']
    return district
