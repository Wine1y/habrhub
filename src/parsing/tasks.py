from celery import shared_task


@shared_task
def temp_task():
    print("Not doing anything, huh?")