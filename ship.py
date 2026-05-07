import json
import random

import requests
import time
from datetime import datetime

def post_msg(content):
    url = "https://www.pushplus.plus/send"

    payload = json.dumps({
        "token": "",
        "title": "有船票啦",
        "content": content
    })
    headers = {
        'Content-Type': 'application/json'
    }

    requests.request("POST", url, headers=headers, data=payload,verify=False)

def post_order(token,configs={"contactId":24423}):
    url = "https://pxh-api.oceanusgroup.cn/api/mall/orderSave"

    payload = {
        "type": 1,
        "mallId": 41,
        "specId": configs.get("specId"),
        "distributionId": "",
        "contactId": configs["contactId"],
        "orderAmount": 80,
        "orderAmountHandle": 80,
        "orderAmountPay": 80,
        "couponId": "",
        "couponCode": "",
        "orderAmountDiscount": 100,
        "orderAmountInteger": 0,
        "orderAmountBalance": 0,
        "orderRemark": "",
        "childList": [
            {
                "priceId": configs.get("priceId"),
                "childNum": 1,
                "priceClassify": 1,
                "contactId": configs["contactId"]
            }
        ]
    }

    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) XWEB/8555",
        'Content-Type': "application/json",
        'xweb_xhr': "1",
        'token': token,
        'Sec-Fetch-Site': "cross-site",
        'Sec-Fetch-Mode': "cors",
        'Sec-Fetch-Dest': "empty",
        'Referer': "https://servicewechat.com/wx8ac43785fe6fc479/42/page-frame.html",
        'Accept-Language': "zh-CN,zh;q=0.9"
    }

    response = requests.post(url, data=json.dumps(payload), headers=headers,verify=False)
    if response.status_code == 200:
        if response.json().get("success")==True:
            print("订单提交成功")
            post_msg("订单提交成功，请及时付款！")
        else:
            print("订单提交失败")
            post_msg("订单提交失败，请检查！")

def check_tickets(token,target_date=None, target_spec=None, target_ticket_type=None, refresh_interval=30, max_attempts=None):
    """
    定期检查指定日期的船票是否有余票

    Args:
        target_date: 指定日期(格式如"20241025")，None表示任意日期
        target_spec: 指定船班(如"香港→珠海")，None表示任意船班
        target_ticket_type: 指定票种(如"成人票"或"优待票")，None表示任意票种
        refresh_interval: 刷新间隔(秒)
        max_attempts: 最大尝试次数，None表示无限循环

    Returns:
        找到符合条件的船票时返回True，达到最大尝试次数返回False
    """
    attempt = 1

    # 初始化请求参数
    url = "https://pxh-api.oceanusgroup.cn/api/mall/mallGet"
    payload = {'mallId': "41"}
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) XWEB/8555",
        'xweb_xhr': "1",
        'token': token,
        'Sec-Fetch-Site': "cross-site",
        'Sec-Fetch-Mode': "cors",
        'Sec-Fetch-Dest': "empty",
        'Referer': "https://servicewechat.com/wx8ac43785fe6fc479/42/page-frame.html",
        'Accept-Language': "zh-CN,zh;q=0.9"
    }

    requests.packages.urllib3.disable_warnings()

    try:
        while max_attempts is None or attempt <= max_attempts:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{current_time}] 第{attempt}次查询船票")

            try:
                response = requests.post(url, data=payload, headers=headers, verify=False, timeout=10)
                data = response.json()

                # 解析数据
                result = {}
                for spec in data['data']['specList']:
                    spec_name = spec['specName']
                    spec_id = spec['specId']

                    # 如果指定了船班，但不匹配，则跳过
                    if target_spec and spec_name != target_spec:
                        continue

                    for price in spec['priceList']:
                        price_classify = price.get('priceClassify', 0)
                        if price_classify not in (1, 2):  # 只保留成人票(1)和优待票(2)
                            continue

                        ticket_type = price.get('priceName', '')
                        if ticket_type not in ('成人票', '优待票'):
                            continue

                        # 如果指定了票种，但不匹配，则跳过
                        if target_ticket_type and ticket_type != target_ticket_type:
                            continue

                        date = str(price.get('pricePhase', ''))
                        # 如果指定了日期，但不匹配，则跳过
                        if target_date and date != target_date:
                            continue

                        stock = price.get('priceStock', 0)
                        price_id = price.get('priceId', '')

                        if date not in result:
                            result[date] = {}
                        date_entry = result[date]
                        if spec_name not in date_entry:
                            date_entry[spec_name] = {}
                        time_entry = date_entry[spec_name]
                        time_entry[ticket_type] = {
                            'priceId': price_id,
                            'specId': spec_id,
                            'num': stock
                        }

                # 检查是否有符合条件的船票
                found_tickets = False
                if result:
                    for date, date_info in result.items():
                        for spec_name, spec_info in date_info.items():
                            for ticket_type, ticket_info in spec_info.items():
                                if ticket_info['num'] > 0:
                                    print(
                                        f"🎉 发现有票! 日期:{date} 船班:{spec_name} 票种:{ticket_type} 余票:{ticket_info['num']}")
                                    post_msg(f"🎉 发现有票! 日期:{date} 船班:{spec_name} 票种:{ticket_type} 余票:{ticket_info['num']}")
                                    found_tickets = True
                                    post_order(token,{"contactId":24423,"specId":ticket_info['specId'],"priceId":ticket_info['priceId']})
                                else:
                                    print(f"❌ 无票: 日期:{date} 船班:{spec_name} 票种:{ticket_type}")

                    if found_tickets:
                        return True
                else:
                    if target_date or target_spec or target_ticket_type:
                        filter_conditions = []
                        if target_date:
                            filter_conditions.append(f"日期:{target_date}")
                        if target_spec:
                            filter_conditions.append(f"船班:{target_spec}")
                        if target_ticket_type:
                            filter_conditions.append(f"票种:{target_ticket_type}")

                        condition_str = " ".join(filter_conditions)
                        print(f"❌ 未找到符合条件的船票: {condition_str}")
                    else:
                        print("❌ 未找到任何船票")

            except Exception as e:
                print(f"查询出错: {str(e)}")

            if max_attempts is None or attempt < max_attempts:
                random_delay = refresh_interval + (random.uniform(-3, 3) if refresh_interval > 3 else 0)
                print(f"等待{random_delay:.2f}秒后再次查询...")
                time.sleep(random_delay)

            attempt += 1

    except KeyboardInterrupt:
        print("\n用户中断查询")

    return False


# 使用示例
if __name__ == "__main__":
    print("船票查询系统")
    print("[1] 查询指定日期船票")
    print("[2] 查询所有船票")
    print("[q] 退出程序")

    choice = input("\n请选择功能: ")
    token= input("请输入token: ") or "fe18a47623a14a7497f7211bd6a339bc"
    if choice == '1':
        target_date = input("请输入日期 (格式: YYYYMMDD，如20241025): ")
        target_spec = input("请输入船班 (直接回车表示查询所有船班): ") or "17:00开航"
        target_ticket_type = input("请输入票种 (成人票/优待票，直接回车表示查询所有票种): ") or "成人票"
        refresh_interval = int(input("请输入刷新间隔秒数 (默认5秒): ") or "5")

        check_tickets(token,target_date, target_spec, target_ticket_type, refresh_interval)

    elif choice == '2':
        refresh_interval = int(input("请输入刷新间隔秒数 (默认5秒): ") or "5")
        check_tickets(token,refresh_interval=refresh_interval)

    elif choice.lower() == 'q':
        print("程序已退出")

    else:
        print("无效的选择")