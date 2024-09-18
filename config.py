import json
from datetime import datetime

# 从客户端获取的数据
def get_data(data):
    try:
        return json.loads(list(data)[0])
    except Exception as e:
        return dict(data)

# 传给客户端的数据
def send_data(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False)

# 传提示数据 1为错误, 0为正常, 默认是1, 方便处理错误的消息
def send_cc(msg: str, status: int = 1) -> str:
    return json.dumps({'status': status, 'msg': msg}, ensure_ascii=False)


# 获取当前日期
def get_cur_time():
    cur_time = str(datetime.now())[0:19]
    return cur_time



