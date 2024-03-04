from modules import downaload, work_tables
import datetime

def main():

    date = datetime.date.today() - datetime.timedelta(days = 15)
    while date < datetime.date.today():
        # downaload.download_repors(driver = downaload.openBrowser().initialize_driver(), date = date).download_reports()
        work_tables.wor_tables(date_work =  date)
        date = date + datetime.timedelta(days = 1 )

if __name__ == '__main__':
    main()
    print("Download e worktables finalizados!")
    