import sys
from geocoder import get_coordinates, get_nearest_object


def main(toponim):
    ll = get_coordinates(toponim)
    district = get_nearest_object(ll, 'district')
    print(district)


if __name__ == '__main__':
    t = " ".join(sys.argv[1:])
    if t:
        main(t)
