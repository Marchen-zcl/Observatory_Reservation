import requests
import hashlib
import datetime
import ddddocr
from config_log import logger
requests.packages.urllib3.disable_warnings()
import ntp
wxuser="226607ec9c3b47eaa919020144fb857a" or input("请输入wxuser：")
user_info=[
    {
        "name": "赵晨龙",
        "cardNumber": "513423200111100019",
        "sex": "0",
        "mobile": "18980286350"
    },
    {
        "name": "秦雯",
        "cardNumber": "513902200110153982",
        "sex": "1",
        "mobile": "18980286350"
    }
]

def post(url,params,payload,headers,cookies=None):
    response = requests.post(url, params=params, data=payload, cookies=cookies, headers=headers,verify=False)
    if response.status_code == 200:
        return response.json()
    else:
        return None
def get(url,params,headers,cookies=None):
    response = requests.get(url, params=params, cookies=cookies, headers=headers,verify=False)
    if response.status_code == 200:
        return response
    else:
        return None

def get_code(timestamp):
    url = "https://weather.121.com.cn/szqx/api/twt/kfr/gryy/code.do"

    params = {
        'source': "wx",
        'wxuser': wxuser,
        't': timestamp
    }

    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090a13) XWEB/8555 Flue",
        'Accept': "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        'Sec-Fetch-Site': "same-origin",
        'Sec-Fetch-Mode': "no-cors",
        'Sec-Fetch-Dest': "image",
        'Referer': "https://weather.121.com.cn/sztwt/",
        'Accept-Language': "zh-CN,zh;q=0.9",
        # 'Cookie': "Path=/; __jsluid_s=4af4dd434a9b59d87b2c41296a1600f1; /; Hm_lvt_567b491b0e5bc0444e010725fcd1d558=1745295791,1745297985,1745378805,1745386940; HMACCOUNT=6381F8443F145EC6; Hm_lpvt_567b491b0e5bc0444e010725fcd1d558=1745411719"
    }

    response = get(url, params, headers)
#     将返回的图片保存到本地
    if response.status_code == 200:
        result = ocr.classification(response.content)
        return result
    else:
        return None

def schedule_list(max_retries=3):
    """
    获取排班列表，自动处理可能遇到的验证码
    
    Args:
        max_retries: 最大重试次数
        
    Returns:
        dict: 排班信息或错误信息
    """
    url = "https://weather.121.com.cn/szqx/api/twt_v2/kfr/list.do"

    params = {
        'source': "wx",
        'wxuser': wxuser
        }

    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090a13) XWEB/8555 Flue",
        'Accept': "application/json, text/plain, */*",
        'Origin': "https://weather.121.com.cn",
        'Sec-Fetch-Site': "same-origin",
        'Sec-Fetch-Mode': "cors",
        'Sec-Fetch-Dest': "empty",
        'Referer': "https://weather.121.com.cn/sztwt/",
        'Accept-Language': "zh-CN,zh;q=0.9"
    }
    
    for attempt in range(1, max_retries + 1):
        timestamp = int(datetime.datetime.now().timestamp() * 1000)
        
        # 首先不带验证码尝试
        payload = {
            'yzm': "",
            'lonlat': ""
        }
        
        schedule = post(url, params, payload, headers)
        
        # 处理需要验证码的情况
        if schedule and schedule.get("code") == 1002:
            logger.info(f"获取排班列表需要验证码，正在进行识别...")
            code = get_code(timestamp)
            logger.info(f"验证码识别结果: {code}")
            
            # 携带验证码重新请求
            payload['yzm'] = code
            schedule = post(url, params, payload, headers)
        
        if schedule and schedule.get("code") == 0:
            return extract_reservation_info(schedule)
        elif schedule:
            logger.warning(f"获取排班信息失败 (尝试 {attempt}/{max_retries}): {schedule.get('msg')}")
            if attempt < max_retries:
                time.sleep(1)  # 短暂等待后重试
        else:
            logger.error(f"获取排班信息失败 (尝试 {attempt}/{max_retries}): 网络错误或服务器未响应")
            if attempt < max_retries:
                time.sleep(1)

    logger.error("获取排班信息失败！已达到最大重试次数")
    return None

def post_order(yzzuser,timestamp,kfrSdId,kfrId,code=None):
    url = "https://weather.121.com.cn/szqx/api/twt/kfr/gryy/save.do"

    params = {
        'source': "wx",
        'wxuser': wxuser,
    }

    payload = {
        'dyEndDate': "",
        'isTYXY': "no",
        'time': timestamp,
        'yzzuser': yzzuser,
        'name': user_info[0]['name'],
        'cardType': "1",
        'cardNumber': user_info[0]['cardNumber'],
        'sex': user_info[0]["sex"],
        'mobile': user_info[0]["mobile"],
        'carNumber': "",
        'entourageCount': "1",
        'nonage': "0",
        'kfrSdId': kfrSdId,
        'kfrId': kfrId,
        'isDydptx': "0",
        'name1': user_info[1]['name'],
        'cardType1': "1",
        'cardNumber1': user_info[1]['cardNumber'],
        "sex1": user_info[1]["sex"],
        "yzm": code,
    }

    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090a13) XWEB/8555 Flue",
        'Accept': "application/json, text/plain, */*",
        'Origin': "https://weather.121.com.cn",
        'Sec-Fetch-Site': "same-origin",
        'Sec-Fetch-Mode': "cors",
        'Sec-Fetch-Dest': "empty",
        'Referer': "https://weather.121.com.cn/sztwt/",
        'Accept-Language': "zh-CN,zh;q=0.9",
    }
    result=post(url, params, payload, headers)
    return result

# 新增抢号函数
def book_appointment(kfrSdId, kfrId, max_retries=10, retry_interval=0.5):
    """
    尝试预约指定的时间段，支持自动重试和验证码识别
    
    Args:
        kfrSdId: 排班ID
        kfrId: 预约ID
        max_retries: 最大重试次数
        retry_interval: 重试间隔(秒)
    
    Returns:
        dict: 预约结果
    """
    logger.info(f"开始预约 kfrSdId={kfrSdId}, kfrId={kfrId}")
    for attempt in range(1, max_retries + 1):
        post_info = get_yzzuser()
        yzzuser, timestamp = post_info.values()
        
        # 首次尝试不带验证码
        result = post_order(yzzuser, timestamp, kfrSdId, kfrId)
        
        if result:
            # 需要验证码
            if result['code'] == 1002:
                logger.info(f"第{attempt}次尝试：触发验证码，正在识别...")
                code = get_code(timestamp)
                logger.info(f"验证码：{code}")
                result = post_order(yzzuser, timestamp, kfrSdId, kfrId, code)
            
            # 处理预约结果
            if result["code"] == 0:
                logger.info(f"🎉 预约成功！详情: {result['msg']}")
                return result
            else:
                logger.warning(f"第{attempt}次尝试：预约失败，{result['msg']}")
        else:
            logger.error(f"第{attempt}次尝试：wxuser失效或网络错误！")
        
        # 如果还有重试次数，则等待后继续
        if attempt < max_retries:
            logger.info(f"等待{retry_interval}秒后重试...")
            time.sleep(retry_interval)
    
    logger.error(f"预约失败！已达到最大重试次数{max_retries}次")
    return None

def extract_reservation_info(json_data):
    """
    从给定的 JSON 数据中提取预约信息，并返回格式化后的结果。

    :param json_data: 包含预约信息的 JSON 数据
    :return: 格式化后的预约信息字典
    """
    # 初始化结果字典
    result = {}

    # 提取 kfrs 数据
    kfrs = json_data.get("data", {}).get("kfrs", {})
    for date, slots in kfrs.items():
        # 初始化日期对应的上午和下午信息
        date_info = {"上午": {}, "下午": {}}

        for slot in slots:
            # 获取时间段名称（如“上午9:00-12:00”）
            name = slot.get("name", "")
            # 判断是上午还是下午
            time_of_day = "上午" if "上午" in name else "下午"

            # 填充对应时间段的信息
            date_info[time_of_day] = {
                "name": name,
                "time": slot.get("time", ""),
                "maxNum": slot.get("maxNum", 0),
                "curNum": slot.get("curNum", 0),
                "kfr_id": slot.get("kfr_id", 0),
                "kfr_sd_id": slot.get("kfr_sd_id", 0),
                "is_start": slot.get("isStart", 0),
            }

        # 如果是闭馆日，手动设置为“闭馆维护”
        if "闭馆维护" in date_info["上午"].get("name", ""):
            date_info["上午"] = {
                "name": "闭馆维护",
                "time": "",
                "maxNum": 0,
                "curNum": 0,
                "kfr_id": 0,
                "kfr_sd_id": 0
            }
            date_info["下午"] = {
                "name": "闭馆维护",
                "time": "",
                "maxNum": 0,
                "curNum": 0,
                "kfr_id": 0,
                "kfr_sd_id": 0
            }

        # 将日期信息添加到结果字典
        result[date.split("<")[0]] = date_info
    return result

def get_yzzuser():
    date = datetime.datetime.now()
    timestamp = int(date.timestamp() * 1000)
    month = date.month - 1
    day = date.day

    inner_md5_str = f"izmby8{month}vlt5Y8{day}qMQu7ys{timestamp}"
    inner_md5_hash = hashlib.md5(inner_md5_str.encode('utf-8')).hexdigest()

    outer_md5_part2_str = f"vlt5Y8{timestamp}{wxuser}"
    outer_md5_part2_hash = hashlib.md5(outer_md5_part2_str.encode('utf-8')).hexdigest()

    final_md5_str = inner_md5_hash + outer_md5_part2_hash
    yzzuser = hashlib.md5(final_md5_str.encode('utf-8')).hexdigest()

    return {"yzzuser": yzzuser, "timestamp": timestamp}

def wait_until_booking_time(target_weekday=0, target_hour=10, target_minute=0):
    """
    等待直到指定的预约时间
    
    Args:
        target_weekday: 目标星期几 (0=周一, 6=周日)
        target_hour: 目标小时 (24小时制)
        target_minute: 目标分钟
    """
    while True:
        now = datetime.datetime.now()
        current_weekday = now.weekday()  # 0是周一，6是周日
        
        if current_weekday == target_weekday and now.hour == target_hour and now.minute == target_minute:
            logger.info(f"已到达预约时间: 周{target_weekday+1} {target_hour}:{target_minute:02d}")
            return
        
        # 计算等待时间
        if current_weekday > target_weekday:
            # 如果当前已经过了目标星期，则等到下周
            days_to_wait = 7 - current_weekday + target_weekday
        elif current_weekday < target_weekday:
            days_to_wait = target_weekday - current_weekday
        else:
            # 同一天
            days_to_wait = 0
            
        target_time = datetime.datetime(
            now.year, now.month, now.day, target_hour, target_minute
        ) + datetime.timedelta(days=days_to_wait)
        
        # 如果今天已经过了目标时间，调整到下周
        if days_to_wait == 0 and now.time() > datetime.time(target_hour, target_minute):
            target_time += datetime.timedelta(days=7)
            
        wait_seconds = (target_time - now).total_seconds()
        
        # 每分钟更新一次日志
        if wait_seconds > 60:
            days = int(wait_seconds // 86400)
            hours = int((wait_seconds % 86400) // 3600)
            minutes = int((wait_seconds % 3600) // 60)
            logger.info(f"距离预约时间还有: {days}天 {hours}小时 {minutes}分钟")
            time.sleep(60)
        else:
            # 最后一分钟倒计时
            logger.info(f"距离预约时间还有: {int(wait_seconds)}秒")
            time.sleep(1)

def select_schedule():
    """
    获取并选择可预约的排班
    
    Returns:
        tuple: (kfrSdId, kfrId) 或在用户取消时返回 None
    """
    logger.info("正在获取预约排班信息...")
    schedules = schedule_list()
    if not schedules:
        logger.error("获取排班信息失败！")
        return None
    elif schedules and schedules.get("code") != None:
        logger.error(f"获取排班信息失败: {schedules.get('msg')}")
        return None
    
    # 显示可预约的日期
    available_dates = []
    print("\n===== 可预约日期 =====")
    for i, (date, info) in enumerate(schedules.items()):
        am_info = info["上午"]
        pm_info = info["下午"]
        available_dates.append(date)
        print(f"[{i+1}] {date}")
        # 上午信息
        am_status_code = am_info.get("is_start", 0)
        if am_status_code == 1:
            am_status = "可以预约"
        elif am_status_code == 0:
            am_status = "不开放"
        elif am_status_code == 2:
            am_status = "已约满"
        elif am_status_code == 3:
            am_status = "时间已过"
        else:
            am_status = "未知状态"

        print(f"    上午: {am_info.get('name', '无信息')} "
          f"(已约{am_info.get('curNum', 0)}/{am_info.get('maxNum', 0)}) "
          f"状态: {am_status}")

        # 下午信息
        pm_status_code = pm_info.get("is_start", 0)
        if pm_status_code == 1:
            pm_status = "可以预约"
        elif pm_status_code == 0:
            pm_status = "不开放"
        elif pm_status_code == 2:
            pm_status = "已约满"
        elif pm_status_code == 3:
            pm_status = "时间已过"
        else:
            pm_status = "未知状态"

        print(f"    下午: {pm_info.get('name', '无信息')} "
          f"(已约{pm_info.get('curNum', 0)}/{pm_info.get('maxNum', 0)}) "
          f"状态: {pm_status}")

    if not available_dates:
        logger.info("当前没有可预约的日期")
        return None

    # 用户选择日期
    choice = input("\n请选择要预约的日期编号 (输入q退出): ")
    if choice.lower() == 'q':
        return None
    
    try:
        date_idx = int(choice) - 1
        selected_date = available_dates[date_idx]
        
        # 显示选择日期的上午/下午排班
        date_info = schedules[selected_date]
        print(f"\n===== {selected_date} 排班信息 =====")
        
        # 显示所有时间段及其状态（不管是否可预约）
        am_info = date_info["上午"]
        am_status_code = am_info.get("is_start", 0)
        if am_status_code == 1:
            am_status = "可以预约"
        elif am_status_code == 0:
            am_status = "不开放"
        elif am_status_code == 2:
            am_status = "已约满"
        elif am_status_code == 3:
            am_status = "时间已过"
        else:
            am_status = "未知状态"
        
        print(f"[1] 上午: {am_info.get('name', '无信息')} "
              f"(已约{am_info.get('curNum', 0)}/{am_info.get('maxNum', 0)}) "
              f"状态: {am_status}")
        
        pm_info = date_info["下午"]
        pm_status_code = pm_info.get("is_start", 0)
        if pm_status_code == 1:
            pm_status = "可以预约"
        elif pm_status_code == 0:
            pm_status = "不开放"
        elif pm_status_code == 2:
            pm_status = "已约满"
        elif pm_status_code == 3:
            pm_status = "时间已过"
        else:
            pm_status = "未知状态"
        
        print(f"[2] 下午: {pm_info.get('name', '无信息')} "
              f"(已约{pm_info.get('curNum', 0)}/{pm_info.get('maxNum', 0)}) "
              f"状态: {pm_status}")
        
        # 用户选择上午/下午
        time_choice = input("\n请选择时间段编号 (输入q退出): ")
        if time_choice.lower() == 'q':
            return None
        
        time_idx = int(time_choice)
        if time_idx == 1:
            selected_time = "上午"
            time_info = am_info
        elif time_idx == 2:
            selected_time = "下午"
            time_info = pm_info
        else:
            logger.error("选择无效: 只能选择1或2")
            return None
        
        logger.info(f"已选择: {selected_date} {selected_time} {time_info['name']}")
        return time_info["kfr_sd_id"], time_info["kfr_id"]
        
    except (ValueError, IndexError) as e:
        logger.error(f"选择无效: {e}")
        return None

# Assuming logger is configured elsewhere as in the original code

def wait_until_booking_time_window(start_hour=9, start_minute=57, end_hour=10, end_minute=3):
    """
    等待直到预约时间窗口，并在开始时间前显示倒计时。
    如果当前时间已经超过结束时间，则返回False。
    
    Args:
        start_hour: 开始时间-小时 (默认9点57分开始监控)
        start_minute: 开始时间-分钟
        end_hour: 结束时间-小时 (默认10点03分结束)
        end_minute: 结束时间-分钟
        
    Returns:
        bool: True表示在预约时间窗口内，False表示已过预约时间或用户中断
    """
    now = datetime.datetime.now()
    today = now.date()
    
    # 计算开始和结束时间点
    start_time = datetime.datetime.combine(today, datetime.time(start_hour, start_minute))
    end_time = datetime.datetime.combine(today, datetime.time(end_hour, end_minute))
    booking_time = datetime.datetime.combine(today, datetime.time(10, 0))  # 10:00是抢号时间
    
    # 检查是否已超过结束时间
    if now > end_time:
        logger.info("当前时间已超过预约结束时间 (10:03)，取消预约")
        return False
    
    # 已经过了抢号时间，但仍在结束时间之前
    if now > booking_time:
        logger.info(f"当前已过抢号开始时间 (10:00)，直接开始预约...")
        return True
    
    # 等待直到开始时间
    print(f"将在 10:00:00 准时开始抢号...当前时间: {now.strftime('%H:%M:%S')}")
    
    try:
        # 等待到监控开始时间
        last_minute_update = None
        while now < start_time:
            now = datetime.datetime.now()
            remaining = (start_time - now).total_seconds()
            
            # 每分钟显示一次提示
            current_minute = now.minute
            if remaining > 60 and (last_minute_update is None or current_minute != last_minute_update):
                last_minute_update = current_minute
                minutes_remaining = int(remaining / 60)
                logger.info(f"未到监测时间，距离开始还有 {minutes_remaining} 分钟")
                time.sleep(10)
            
            # 小于60秒时显示倒计时
            if remaining < 60:
                print(f"\r即将开始监控，剩余 {int(remaining)} 秒" + " "*20,end="")
                time.sleep(0.5)
        
        # 开始倒计时至10:00
        ntp.set_time()
        while now < booking_time:
            time.sleep(0.05)  # 更频繁地检查时间
            now = datetime.datetime.now()
            remaining = (booking_time - now).total_seconds()
            print(f"\r距离抢号开始还有: {remaining:.2f} 秒" + " "*20,end="")
            
        print("\n抢号时间到! 开始尝试预约..." + " " * 40)
        return True
        
    except KeyboardInterrupt:
        print("\n用户手动中断等待。")
        return False

def book_until_success_or_timeout(kfrSdId, kfrId, end_hour=10, end_minute=3, retry_interval=0.5):
    """
    持续尝试预约直到成功或超出结束时间
    
    Args:
        kfrSdId: 排班ID
        kfrId: 预约ID
        end_hour: 结束抢号的小时
        end_minute: 结束抢号的分钟
        retry_interval: 重试间隔(秒)
    
    Returns:
        dict: 预约结果，如果超时返回None
    """
    attempt = 1
    while True:
        now = datetime.datetime.now()
        # 检查是否超出抢号时间窗口
        if (now.hour > end_hour or (now.hour == end_hour and now.minute > end_minute)):
            logger.error(f"抢号超时，已退出抢号流程")
            return None
        
        logger.info(f"第{attempt}次尝试预约 - {now.hour}:{now.minute:02d}:{now.second:02d}")
        post_info = get_yzzuser()
        yzzuser, timestamp = post_info.values()
        
        # 尝试预约
        result = post_order(yzzuser, timestamp, kfrSdId, kfrId)
        
        if result:
            # 处理需要验证码的情况
            max_captcha_attempts = 3
            captcha_attempt = 1
            
            while result and result['code'] == 1002 and captcha_attempt <= max_captcha_attempts:
                logger.info(f"触发验证码，第{captcha_attempt}次识别...")
                code = get_code(timestamp)
                logger.info(f"验证码：{code}")
                result = post_order(yzzuser, timestamp, kfrSdId, kfrId, code)
                
                # 检查是否验证码错误
                if result and (result.get('msg', '').find('验证码错误') != -1 or result.get('msg', '').find('验证码有误') != -1):
                    logger.warning(f"验证码错误，立即重新获取...")
                    captcha_attempt += 1
                else:
                    # 不是验证码错误，跳出验证码重试循环
                    break
            
            # 处理预约结果
            if result and result["code"] == 0:
                logger.info(f"🎉 预约成功！详情: {result['msg']}")
                return result
            else:
                error_msg = result.get('msg', '未知错误') if result else '请求失败'
                logger.warning(f"预约失败，{error_msg}")
        else:
            logger.error(f"请求失败，wxuser可能失效或网络错误")
        
        attempt += 1
        logger.info(f"等待{retry_interval}秒后重试...")
        time.sleep(retry_interval)

def run_leftover_mode(target_date=None, retry_min=1, retry_max=3):
    """
    捡漏模式：定期检查排班，发现有空位就立即预约
    
    Args:
        target_date: 指定日期(格式如"2023-11-05")，None表示任意日期
        retry_min: 最小重试间隔(秒)
        retry_max: 最大重试间隔(秒)
    """
    import random
    
    logger.info(f"启动捡漏模式 - {'指定日期: ' + target_date if target_date else '任意日期'}")
    attempt = 1
    
    try:
        while True:
            logger.info(f"第{attempt}次查询排班")
            schedules = schedule_list()  # 已处理验证码
            
            if not schedules or (schedules and schedules.get("code") is not None):
                logger.error(f"获取排班信息失败: {schedules.get('msg') if schedules else '未知错误'}")
                wait_time = random.uniform(retry_min, retry_max)
                logger.info(f"等待{wait_time:.1f}秒后重试...")
                time.sleep(wait_time)
                attempt += 1
                continue
            
            # 查找可预约的时段
            available_slots = []
            
            for date, info in schedules.items():
                # 如果指定了日期，只检查该日期
                if target_date and not date.startswith(target_date):
                    continue
                
                # 检查上午和下午的时段
                for time_period in ["上午", "下午"]:
                    period_info = info[time_period]
                    
                    # 检查是否可预约（状态为1且未约满）
                    if period_info.get("is_start") != 3:
                        if period_info.get("curNum", 0) < period_info.get("maxNum", 0):
                            available_slots.append({
                                "date": date,
                                "time_period": time_period,
                                "name": period_info.get("name", ""),
                                "kfr_sd_id": period_info.get("kfr_sd_id"),
                                "kfr_id": period_info.get("kfr_id"),
                                "curNum": period_info.get("curNum", 0),
                                "maxNum": period_info.get("maxNum", 0)
                            })
            
            # 如果有可预约的时段，尝试预约
            if available_slots:
                # 按日期排序，取第一个
                available_slots.sort(key=lambda x: x["date"])
                slot = available_slots[0]
                
                logger.info(f"发现可预约时段: {slot['date']} {slot['time_period']} "
                           f"({slot['name']}) 已约{slot['curNum']}/{slot['maxNum']}")
                
                # 尝试预约
                result = book_appointment(slot["kfr_sd_id"], slot["kfr_id"], max_retries=5, retry_interval=0.5)
                
                if result and result.get("code") == 0:
                    logger.info(f"🎉 捡漏成功！已预约 {slot['date']} {slot['time_period']}")
                    return True
                else:
                    logger.warning(f"预约失败，继续捡漏模式")
            else:
                if target_date:
                    logger.info(f"日期 {target_date} 暂无可预约时段")
                else:
                    logger.info("暂无任何可预约时段")
            
            # 随机等待时间，避免请求过于规律
            wait_time = random.uniform(retry_min, retry_max)
            logger.info(f"等待{wait_time:.1f}秒后重试...")
            time.sleep(wait_time)
            attempt += 1
            
    except KeyboardInterrupt:
        logger.info("用户手动中断捡漏模式")
        return False

if __name__ == "__main__":
    import time
    ocr = ddddocr.DdddOcr(show_ad=False, use_gpu=True)
    # test_ocr
    with open("test.png", "rb") as f:
        img = f.read()
        start_time = datetime.datetime.now()
        result = ocr.classification(img)
        end_time = datetime.datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()
        assert result == "kwn8g"
        logger.info(f"初始化识别模型成功，首次识别耗时：{elapsed_time:.4f}秒")
    ntp.set_time()
    print("\n===== 天文台自动预约系统 =====")
    print("[1] 立即预约")
    print("[2] 定点抢号 (9:57-10:03自动抢号)")
    print("[3] 捡漏模式 (自动检测可预约时段)")
    print("[q] 退出程序")
    
    choice = input("\n请选择功能: ")
    
    if choice == '1':
        # 立即预约
        selected = select_schedule()
        if selected:
            kfrSdId, kfrId = selected
            book_appointment(kfrSdId, kfrId)
    
    elif choice == '2':
        # 定点抢号 (9:57-10:03)
        selected = select_schedule()
        if selected:
            kfrSdId, kfrId = selected
            logger.info("已设置定点抢号，将在9:57-10:03时间段内持续抢号")
            
            # 等待到抢号时间窗口
            in_time_window = wait_until_booking_time_window(9, 57, 10, 3)
            
            if in_time_window:
                # 在时间窗口内持续抢号，直到成功或超时
                result = book_until_success_or_timeout(kfrSdId, kfrId, 10, 3, 0.05)
                
                if not result:
                    logger.error("抢号失败，已超出预约时间窗口")
            else:
                logger.error("今日抢号时间已过")
    
    elif choice == '3':
        # 捡漏模式
        print("\n捡漏模式选项：")
        print("[1] 任意日期捡漏")
        print("[2] 指定日期捡漏")
        print("[q] 返回")
        
        leftover_choice = input("\n请选择捡漏模式: ")
        
        if leftover_choice == '1':
            # 任意日期捡漏
            run_leftover_mode()
        elif leftover_choice == '2':
            # 指定日期捡漏
            target_date = input("请输入目标日期 (格式: MM-DD): ")
            run_leftover_mode(target_date)
        elif leftover_choice.lower() == 'q':
            logger.info("返回主菜单")
        else:
            logger.error("无效的选择")
    
    elif choice.lower() == 'q':
        logger.info("程序已退出")
    
    else:
        logger.error("无效的选择")




