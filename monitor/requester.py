import urllib.request
from time import sleep

if __name__ == '__main__':

    while True:
        try:
            urllib.request.urlopen('http://localhost:8000/monitor')
            sleep(10)
        except():
            continue
