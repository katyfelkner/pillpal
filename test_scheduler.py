import schedule
import time

def test_job():
    print("It has been another 5 seconds")

schedule.every(5).seconds.do(test_job)


while True:
    schedule.run_pending()
    time.sleep(1)
