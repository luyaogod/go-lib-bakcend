if __name__ == "__main__":
    from book_task.book_sync import DailyTasks
    dt = DailyTasks(worker_id=1,worker_size=2)
    mydb = dt.db()
    tasks = dt.task_pull_user_id_and_wx_cookie(db=mydb)
    print(tasks)
    v_tasks = dt.task_assiginment(tasks)
    print(v_tasks)