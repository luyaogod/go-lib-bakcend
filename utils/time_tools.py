from datetime import datetime, timedelta,timezone
import pytz

def time_validate(utc_now):
    # 转换为北京时间
    beijing_tz = pytz.timezone('Asia/Shanghai')
    beijing_now = utc_now.astimezone(beijing_tz)

    # 定义18:00和20:00的时间点
    start_of_period = beijing_now.replace(hour=18, minute=0, second=0, microsecond=0)
    end_of_period = beijing_now.replace(hour=20, minute=0, second=0, microsecond=0)

    # 判断当前时间是否在时间段内
    if start_of_period <= beijing_now <= end_of_period:
        return True
    else:
        return False


def get_set_time(utc_now):
    # 转换为北京时间
    beijing_tz = pytz.timezone('Asia/Shanghai')
    beijing_now = utc_now.astimezone(beijing_tz)

    # 计算今天晚上20点的时间点
    today_evening_20 = beijing_now.replace(hour=20, minute=0, second=0, microsecond=0)
    if today_evening_20 < beijing_now:
        # 如果已经过了今天的20点，则设定为明天的20点
        today_evening_20 += timedelta(days=1)

    # 计算到今晚20点的时间差（以秒为单位）
    time_to_evening = (today_evening_20 - beijing_now).total_seconds()

    # 将时间差转换为eta参数所需的datetime对象，并转回UTC时区
    eta_time = utc_now + timedelta(seconds=time_to_evening)
    return eta_time

# if __name__ == "__main__":
#     # current_utc_time = datetime.now(timezone.utc)
#     # result =  is_within_beijing_time_period(current_utc_time)
#     # eta_for_eight_pm = get_delay_to_beijing_eight_pm(current_utc_time)
#     # print(result)
#     # print(eta_for_eight_pm)
