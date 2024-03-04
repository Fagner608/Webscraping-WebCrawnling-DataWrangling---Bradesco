from modules import requests, downaload
import datetime


def main():

    date = datetime.date.today() - datetime.timedelta(days = 15)
    while date < datetime.date.today():
        teste = requests.get_tables(downaload.openBrowser().initialize_driver(), date = date) 
        print("Requisição do dia: ", date)
        date = date + datetime.timedelta(days = 1)


if __name__ == '__main__':
    main()
    print("Requisições finalizadas")