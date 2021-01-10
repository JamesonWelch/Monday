from apscheduler.schedulers.background import BackgroundScheduler


sched = BackgroundScheduler(daemon=True)

sched.add_job(lambda: )