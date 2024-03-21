import celery
from get_seats import main_loop
from settings import BROKER_URL,BACKEND_URL

backend = BACKEND_URL
broker = BROKER_URL

cel = celery.Celery('task',backend=backend,broker=broker)


@cel.task
def add_task(cookie,data_list):
    result =  main_loop(cookie,data_list)
    return result