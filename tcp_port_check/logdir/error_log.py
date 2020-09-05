# encoding=utf-8
import time


# 定义装饰器
def error_log_candy(func):
    def wrapper(*args, **kargs):
        while True:
            try:
                print('添加测试模块')
                f = func(*args, **kargs)
                break
            except Exception as e:
                print('出现异常,将报错信息给我(error_log.txt):\n\t', e)
                print('10s后重试')
                current_time = time.strftime("%Y-%m-%d_%H:%M:%S\t", time.localtime())
                with open('error_log.txt', 'w+') as f:
                    f.write(current_time)
                    f.write(str(e))
                    f.write('\n-------------\n\n\n')
                time.sleep(10)

        print('\n\n测试 采集任务结束无报错100s后退出')
        time.sleep(100)
        return f

    return wrapper

# from configparser import ConfigParser
#
# ini = ConfigParser()
# ini.read('config.cfg',encoding='utf-8')
# print(ini['login']['username'])
