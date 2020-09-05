#!/usr/bin/python3
# -*- coding: utf-8 -*-
from socket import *
import threading, time, os, smtplib
from configparser import ConfigParser
from email.mime.text import MIMEText

def detect_infocfg():
    init_config = """[port_check_info]

# 指定主机 是否扫描 True为是，False否
single_switch = True
# 指定主机检测列表 可参考下方示例
# 多个检测对象使用回车分割   端口间用,(英文逗号)分割   主机与端口间用：(英文冒号)分隔
detect_lst = 172.16.88.100:   80,22,8000,23,
             114.114.114.114:  53,23,343,343
             172.16.66.1:     23,5000

batch_switch = True
# 批量主机 是否扫描 True为是，False否
address=172.16.66.166,137.78.5.39
#检查的端口，如多个端口使用,隔开,端口范围使用'-'
ports=80,22,52,5539

# 检测时间间隔
detect_gap = 30
# 超时时间，tcp超时时间
timeout = 1


#日志配置
[log]
#日志文件名称
logfile_name = check_port.log

# 定义邮件提醒， #邮件发送间隔 收件人列表 /  发件人服务器  / 发件人用户名(xxx@xx.com）/ 发件人密码
[mail]
# 是否发送邮件  True为是，False为否
sendmail = True
send_gap = 2
error_send_gap = 10
mailto_list = <把我连同尖括号替换成邮箱地址 |例如：gwisss@qq.com,2869424475@qq.com>
mail_host = <把我同尖括号替换成你邮箱对应的服务器 |例如: smtp.163.com>
mail_user = <把我同尖括号替换成你的邮箱 |例如: GWixx@163.com>
mail_pass = <把我同尖括号替换成你的密码>
content =  本选项自定义邮件内容 现已弃用

#自定义插件-指定行为可触发自定义功能
[plugins]
# 建议插件1： 本地弹出窗口告警
plugins1 = msg * {host}端口{port}告警
plugins2 =
plugins3 =
plg1when_port_up = echo port_UP_plugins1_successful_run!

#Tip
#使用时Ctrl+C 可以中断扫描，回车立即开始扫描
#每次扫描时都会重新读取配置文件，可以在运行时修改配置
"""
    # 尝试打开, 只有能打开且不等于默认配置时
    try:
        with open('config.ini', 'r', encoding='utf-8')as f:
            file = f.read()
            if len(init_config) == len(file):
                print('配置文件未修改！ 请查看同目录下的config.ini 文件，并参照注释后的格式修改(文件长度相同)')
                return False
            else:
                print('校验配置文件成功')
                return True
    except:
        print('config.ini 无法打开')
        with open('config.ini', 'w', encoding='utf-8') as f:
            f.write(init_config)
            return False


class check_ports():
    def __init__(self):
        """
        初始化，获取配置文件信息
        """
        config = ConfigParser()
        config.read('.\config.ini', encoding='utf-8')
        self.detect_gap = float(config['port_check_info']['detect_gap'])

        self.single_switch = config['port_check_info']['single_switch']
        self.detect_lst = config['port_check_info']['detect_lst'].split('\n')

        self.batch_switch = config['port_check_info']['batch_switch']
        self.address_list = config['port_check_info']['address'].split(',')
        self.port_list = config['port_check_info']['ports'].split(',')
        self.timeout = int(config['port_check_info']['timeout'])

        self.sendmail = config['mail']['sendmail']
        self.send_gap = int(config['mail']['send_gap'])
        self.error_send_gap = int(config['mail']['error_send_gap'])
        self.mailto_list = config['mail']['mailto_list'].split(',')
        self.mail_host = config['mail']['mail_host']  # 设置服务器
        self.mail_user = config['mail']['mail_user'].split('@')[0]  # 用户名
        self.mail_pass = config['mail']['mail_pass']  # 口令
        self.mail_postfix = config['mail']['mail_user'].split('@')[1]
        self.content = config['mail']['content']

        self.plugins1 = config['plugins']['plugins1']
        self.plugins2 = config['plugins']['plugins2']
        self.plugins3 = config['plugins']['plugins3']

        self.logfile_name = config['log']['logfile_name']
        self.undete_data = ''

    def _get_body(self):
        """
        获取address和port
        :return: list
        """
        address_list = self.address_list
        port_list = self.port_list

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

    def detect_mail_info_vail(self):
        return self.send_mail(self.mailto_list, '测试端口检测器-邮件信息有效性',
                              '本邮件是运行前检测配置文件config.ini中邮件信息填写的有效性，避免关键时刻发送失败' + '<br>' +
                              # str(self.content.replace('{host}', str(bad_host_list)).replace('{port}', str(bad_port_list)) +
                              time.strftime('\n%Y-%m-%d_%H:%M:%S', time.localtime())
                              )

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
            # print(str(e))
            print(str(e).replace('authentication failed', '[邮件服务器]认证失败 请检查用户名密码')
                  .replace('Connection unexpectedly closed', '[邮件服务器]与服务器未能建立连接')
                  # .replace()
                  )
            return False

    # 传入单个ip, port 测试
    def portScanner(self, host, port):
        global openNum
        try:
            s = socket(AF_INET, SOCK_STREAM)
            s.connect((host, port))
            lock.acquire()
            openNum += 1
            print(f'！！！{host:>15}\t\t{port:>5}\topen')
            lock.release()
            s.close()
        except timeout as e:
            stutas = '超时:' + str(e)
            bad_host.append([host, port, stutas])  # 记录下来等会统一发送
        except Exception as e:
            print('执行扫描时出现了非超时问题:', e)
            stutas = '非超时:' + str(e)
            bad_host.append([host, port, stutas])  # 记录下来等会统一发送

    def lst_auto_merge(self, lst):
        # add primary Key
        data = {}
        for i in lst:
            data.update({i[0]: []})
        # Merge
        for i in lst:
            data[i[0]].append(i[1:])
        return data

    # def test_detect_every_port(self):
    #     print('即将检测的为：')
    #     for i in self.detect_lst:
    #         print(i)
    #         # host, port_lst_str = i.split(':')
    #         # port_lst = port_lst_str.strip().split(',')
    #         # for port in port_lst:
    #             # print(f'  ┖port:{port:20}')
    #             # print(f'执行单个检测{host}:{port}')
    #     print('\n')

    def main(self):  # TODO: change to self host and design port
        global bad_host_list_lenth, bad_port_list_lenth
        log_file = open(self.logfile_name, 'a+', encoding='utf-8')
        try:  # 扫描 主程序
            # 播报 即将检测的地址端口列表
            # 播报 单个扫描
            if self.single_switch == 'True':
                print('指定主机端口扫描列表：')  # , self.detect_lst)
                print('指定主机端口扫描列表：', file=log_file)  # , self.detect_lst)

                for i in self.detect_lst:
                    single_host, port_lst_str = i.strip().split(':')
                    port_lst = port_lst_str.strip().split(',')
                    if port_lst[-1] == '':
                        port_lst = port_lst[:-1]
                    print(f"{single_host:>20}:\t\t {str(port_lst):<20}")
                    print(f"{single_host:>20}:\t\t {str(port_lst):<20}", file=log_file)
            # 播报 批量扫描
            if self.batch_switch == 'True':
                print('批量扫描列表:')
                print('批量扫描列表:', file=log_file)
                # print('\t┣─', self.address_list, '端口:', self.port_list)
                print(f"    主机: {str(self.address_list):>20}\n    端口: {str(self.port_list):<20}")
                print(f"    主机: {str(self.address_list):>20}\n    端口: {str(self.port_list):<20}", file=log_file)

            print('=' * 60)
            print('=' * 60, file=log_file)

            # 正式批量扫描
            if self.batch_switch == 'True':
                for content in self._get_body():
                    content_list = content.split(':')  # [0]为ip [1]为port
                    setdefaulttimeout(self.timeout)
                    t = threading.Thread(target=self.portScanner,
                                         args=(content_list[0], int(content_list[1])))  # 传入ip, port
                    threads.append(t)
                    t.start()

            # 单个扫描
            if self.single_switch == 'True':
                for i in self.detect_lst:
                    single_host, port_lst_str = i.strip().split(':')
                    port_lst = port_lst_str.strip().split(',')
                    for single_port in port_lst:
                        if single_port != '':
                            setdefaulttimeout(self.timeout)
                            t = threading.Thread(target=self.portScanner,
                                                 args=(single_host, int(single_port)))  # 传入ip, port

                            threads.append(t)
                            t.start()
            for t in threads:
                t.join()
        except Exception as E:
            print('执行批量扫描主程序时出现了问题', E)
            print('执行批量扫描主程序时出现了问题', E, file=log_file)
        if not bad_host == []:
            print('###未检测到的结果:\t', )
            print('###未检测到的结果:\t', file=log_file)

            # 报告超时结果
            # print('整理前的数据')
            # pprint(bad_host)
            data = self.lst_auto_merge(bad_host)
            # print('整理后的数据')
            # pprint(data)
            self.undete_data = data
            for i in data:
                print(f"主机:{i:>16}的:")
                print(f"主机:{i:>16}的:", file=log_file)
                for x in data[i]:
                    print(f'{x[0]:>33}\t {x[1]:<10}')
                    print(f'{x[0]:>33}\t {x[1]:<10}', file=log_file)
            print(time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime()), f'共扫描到 {openNum} 个开放端口 ',
                  len(data), '个主机出现端口问题'
                  )
            print(time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime()), f'共扫描到 {openNum} 个开放端口 ',
                  len(data), '个主机出现端口问题', file=log_file
                  )
            print('=' * 60)
            print('=' * 60, file=log_file)
            # print('\n')

            # 发送邮件
            # print('#' * 12, '准备发送告警邮件, 速度:', self.send_gap, 's/次', '#' * 12)
            print('#' * 21, '准备发送告警邮件', '#' * 21)
            bad_host_list = []
            bad_port_list = []
            for hosts in bad_host:
                bad_host_list.append(hosts[0])
                bad_port_list.append(hosts[1])

                host = hosts[0]
                port = hosts[1]
                status = hosts[2]
                if self.plugins1:
                    try:
                        os.system(eval(f'f"""{self.plugins1}"""'))
                    except Exception as E:
                        print(self.plugins1, '插件运行出问题:', E)
                if self.plugins2:
                    try:
                        os.system(self.plugins2)  # TODO: can add parameter
                    except Exception as E:
                        print(self.plugins1, '插件运行出问题:', E)
                if self.plugins3:
                    try:
                        os.system(self.plugins3)
                    except Exception as E:
                        print(self.plugins1, '插件运行出问题:', E)
            if self.sendmail == 'True':
                try:
                    while True:  # try hard loops to send_mail
                        # send_result = True
                        # send_result = self.send_mail(self.mailto_list, host + "端口" + str(port) + "告警",
                        #                              str(self.content.replace('{host}', host).replace('{port}', str(port))) +status +
                        #                              time.strftime('\n%Y-%m-%d_%H:%M:%S', time.localtime()))
                        bad_host_list_lenth = str(len(data))
                        bad_port_list_lenth = str(len(bad_host))
                        mail_data = ''
                        for i in data:
                            mail_data += '主机:' + i + '<br>'
                            for x in data[i]:
                                mail_data += '&nbsp;' * 20 + str(x[0]) + '&nbsp;' * 10 + str(x[1])
                                mail_data += '<br>'
                            mail_data += '<br>' '<br>'

                        mail_title = "<告警！共" + bad_host_list_lenth + "个主机" + bad_port_list_lenth + "个端口出现问题>"
                        send_result = self.send_mail(self.mailto_list, mail_title,
                                                     mail_data + '<br>' +
                                                     # str(self.content.replace('{host}', str(bad_host_list)).replace('{port}', str(bad_port_list)) +
                                                     time.strftime('\n%Y-%m-%d_%H:%M:%S', time.localtime())
                                                     )
                        if send_result:
                            print(f'...邮件主题: ', mail_title, "告警发送:", send_result)
                            print(f'...邮件主题: ', mail_title, "告警发送:", send_result, file=log_file)
                            # time.sleep(self.send_gap)  # 现已汇总发送， 不需要sleep
                            break
                        print(f'...邮件主题: ', mail_title, "告警发送:", send_result, '发送失败 可能被拒发',
                              self.error_send_gap, "s后尝试重新发送")
                        print(f'...邮件主题: ', mail_title, "告警发送:", send_result, '发送失败 可能被拒发 ',
                              self.error_send_gap, "s后尝试重新发送", file=log_file)
                        time.sleep(self.error_send_gap)
                except Exception as E:
                    with open('error_info.txt', 'w+', encoding='utf-8') as f:
                        f.write(str(E))
                        f.write(f"检测出{bad_host_list_lenth}个主机{bad_port_list_lenth}个端口异常，但发送失败,已写入日志")
                    print(f"检测出{bad_host_list_lenth}个主机{bad_port_list_lenth}个端口异常，但发送失败,已写入日志")
                    pass
            print('#' * 18, '扫描、写入日志并发送完成!', '#' * 18)
        log_file.write('\n\n\n')
        log_file.close()
        print('=' * 18, '等待下次扫描:', self.detect_gap, '分钟', '=' * 18)
        second = self.detect_gap * 60
        print('\n' * 5)
        while second >= 0:
            print(time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime()), "距离下次执行还有:    ", int(second),'秒', end="\r")
            time.sleep(1)
            second -= 1
        print(time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime()), '开始检测                                   ')


if __name__ == '__main__':
    print("""
    ....,/@@@@@@@\`........  
    ..,@@@@[[[[[@@@@`......  
    ./@@/.       .\@@\.....  
    =@@/.          =@@^....  
    =@@^**.        =@@^....  
    =@@\*****....**/@@^....  
    .\@@\*********@@@/.....  
    ..,@@@@@]]]@@@@@`......  
    .....\@@@@@@@@@@^......  
    ..............\@@\.....  
    ...............=@@@....  
    ................,@@@`..  
    ..................\@@\.  
    ...................=@@.  
    """)

    print('###提示：当检测到非活跃端口，以及发送邮件时较慢\n\n')
    if detect_infocfg():  # 只有确认没有配置文件问题时才
        pass
    else:
        input('config.ini配置有问题，请查看回车后退出')
        raise KeyboardInterrupt
    # print('#### 运行主程序时出现了异常', time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime()), E)



    while True:
        try:
            check_app = check_ports()
            if check_app.sendmail == 'True':
                # 检测邮件信息有效性
                print('###测试邮件发送....', end=' ')
                mail_detect_res = check_app.detect_mail_info_vail()
                if not mail_detect_res:
                    input('\n###配置文件中 [mail]字段的右键信息有误请重新填写, [Enter]后关闭本程序###')
                else:
                    print('发送成功，即将开始检测')
            else:
                print('###未设置发送邮件')
            print('### 已读取配置文件作为设置')
        except AttributeError as e:
            print('配置文件 属性值错误！请确认值是否正确:', e)
            input('Enter 退出程序')
        except KeyError as e:
            print('配置文件 键错误！请确认是否有此键:', e)
            input('Enter 退出程序')
        except Exception as e:
            print('###读取配置文件出现问题', e)
            input('Enter 退出程序')

        try:
            lock = threading.Lock()
            openNum = 0
            threads = []
            bad_host = []
            check_app = check_ports()
            check_app.main()
        except KeyboardInterrupt:
            try:
                input('\n已中断\n>>>Ctrl +C 退出程序/ Enter 重新开始')
            except KeyboardInterrupt:
                break
