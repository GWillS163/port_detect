# -*- coding:utf-8 -*-
# _thakskaliarch

import requests
from configparser import ConfigParser
import re

import logger_file
import smtplib
from email.mime.text import MIMEText

class check_ports():
    def __init__(self, logger):
        """
        初始化，获取配置文件信息
        """
        self.url = 'http://tool.chinaz.com/iframe.ashx?t=port'
        self.headers = {
            'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Content-Length': '62',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'tool.chinaz.com',
            'Origin': 'http://tool.chinaz.com',
            'Referer': 'http://tool.chinaz.com/port/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        config = ConfigParser()
        config.read('.\info.cfg', encoding='utf-8')
        self.address_list = config['port_check_info']['address']
        self.port_list = config['port_check_info']['ports']

        self.mailto_list = config['mail']['mailto_list'].split(',')
        self.mail_host = config['mail']['mail_host']   # 设置服务器
        self.mail_user = config['mail']['mail_user']   # 用户名
        self.mail_pass = config['mail']['mail_pass']   # 口令
        self.mail_postfix = config['mail']['mail_postfix']
        # 初始化logger
        logger = logger.LogHelper()
        logname = logger.create_dir()
        self.logoper = logger.create_logger(logname)

    def _get_body(self):
        """
        获取address和port
        :return: list
        """
        address_list = self.address_list.split(',')
        port_list = self.port_list.split(',')

        # 处理端口范围，返回range
        range_flag = False
        port_range = None
        content_List_range = []
        for port in port_list:
            if '-' in port:
                range_flag = True
                port_range = range(int(port.split('-')[0]), int(port.split('-')[1]) + 1)
                port_list.remove(port)

        # 处理总体list
        for add in address_list:
            if range_flag:
                for port in port_range:
                    content_List_range.append(add + ':' + str(port))

        # 合并range和普通list
        content_List = [add + ':' + port for add in address_list for port in port_list]
        content_List_range.extend(content_List)
        return content_List_range

    def send_mail(self, to_list, sub, content):  # to_list：收件人；sub：主题；content：邮件内容
        me = "Port_Warning_Service" + "<" + self.mail_user + "@" + self.mail_postfix + ">"  # 这里的hello可以任意设置，收到信后，将按照设置显示
        msg = MIMEText(content, _subtype='html', _charset='gb2312')  # 创建一个实例，这里设置为html格式邮件
        msg['Subject'] = sub  # 设置主题
        msg['From'] = me
        msg['To'] = ";".join(to_list)
        try:
            s = smtplib.SMTP()
            s.connect(self.mail_host)  # 连接smtp服务器
            s.login(self.mail_user, self.mail_pass)  # 登陆服务器
            s.sendmail(me, to_list, msg.as_string())  # 发送邮件
            s.close()
            return True
        except Exception as e:
            print(str(e))
            return False

    def run(self):
        """
        进行端口检测
        :return:
        """
        for content in self._get_body():
            content_list = content.split(':')
            body = {
                'host': content_list[0],
                'port': content_list[1],
                'encode': 'tlCHS1u3IgF4sC57m6KOP3Oaj1Y1kfLq'
            }
            try:  # 扫描 主程序
                response = requests.post(url=self.url, data=body, headers=self.headers)
                port_status = re.findall("msg:'(.*?)'", response.text)
                if len(port_status) > 0:
                    if port_status == ['关闭']:  # 查看port_staus状态
                        print(' %s,\t端口状态为:%s' % (content, port_status), end='\t')
                        self.logoper.info('%s,端口状态为:%s' % (content, port_status))
                        if self.send_mail(self.mailto_list, content + "端口" + port_status[0] + "告警",
                                     "主机content" + "端口" + " port_status[0]" + "未检测到生存，请<a href='http://www.172.16.88.100:8000/'>点此进入系统查看</a>"):
                            print("已发送告警")
                        else:
                            print("检测出异常，但发送失败")
                    else:
                        print(' %s,\t端口状态为:%s' % (content, port_status))
                        self.logoper.info('%s,端口状态为:%s' % (content, port_status))

                else:
                    self.logoper.info('%s,端口状态为:%s' % (content, port_status))
                    print('Occer error！请输入正确的地址和端口')

            except KeyboardInterrupt:
                print('用户中断')
                try:
                    input('Enter 继续/Ctrl+C 退出')
                    continue
                except KeyboardInterrupt:
                    break
            except Exception as e:
                self.logoper.info(e)
                print('执行出错', e)

if __name__ == '__main__':
    print('测试模式-')
    print('提示： 当检测到非活跃端口， 以及发送邮件时较慢请耐心等待')
    check_app = check_ports(logger_file)
    check_app.run()
    input('@finish')
