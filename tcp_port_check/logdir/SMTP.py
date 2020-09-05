# encoding=utf-8
import smtplib
from email.mime.text import MIMEText
from configparser import ConfigParser


def send_mail(to_list, sub, content):  # to_list：收件人；sub：主题；content：邮件内容
    global mail_user, mail_postfix
    me = "By" + "<" + mail_user + "@" + mail_postfix + ">"  # 这里的hello可以任意设置，收到信后，将按照设置显示
    msg = MIMEText(content, _subtype='html', _charset='gb2312')  # 创建一个实例，这里设置为html格式邮件
    msg['Subject'] = sub  # 设置主题
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        s = smtplib.SMTP()
        s.connect(mail_host)  # 连接smtp服务器
        s.login(mail_user, mail_pass)  # 登陆服务器
        s.sendmail(me, to_list, msg.as_string())  # 发送邮件
        s.close()
        return True
    except Exception as e:
        print(str(e))
        return False


if __name__ == '__main__':

    config = ConfigParser()
    config.read('info.cfg', encoding='utf-8')
    mailto_list = config['mail']['mailto_list']
    mail_host = config['mail']['mail_host']  # 设置服务器
    mail_user = config['mail']['mail_user']  # 用户名
    mail_pass = config['mail']['mail_pass']  # 口令
    mail_postfix = config['mail']['mail_postfix']

    if send_mail(mailto_list, "端口down告警", "主机127.0.0.1, port[22,23,50]未检测到，请<a href='http://www.172.16.88.100:8000/'>点此进入系统查看</a>"):
        print("发送成功")
    else:
        print("发送失败")
