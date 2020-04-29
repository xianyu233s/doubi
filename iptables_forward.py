# coding=utf-8
import os
import commands
import socket

# 检查当前系统
def check_sys():
    global sys
    value = commands.getstatusoutput('cat /etc/redhat-release | grep -q -E -i "centos"')
    if value[0] == 0:
        sys = 'centos'
    else:
        value = commands.getstatusoutput('cat / etc / issue | grep - q - E - i "debian"')
        if value[0] == 0:
            sys = 'debian'
        else:
            value = commands.getstatusoutput('cat /etc/issue | grep -q -E -i "ubuntu"')
            if value[0] == 0:
                sys = 'ubuntu'
            else:
                value = commands.getstatusoutput('cat /etc/issue | grep -q -E -i "centos|red hat|redhat"')
                if value[0] == 0:
                    sys = 'centos'
                else:
                    value = commands.getstatusoutput('cat /proc/version | grep -q -E -i "debian"')
                    if value[0] == 0:
                        sys = 'debian'
                    else:
                        value = commands.getstatusoutput('cat /proc/version | grep -q -E -i "ubuntu"')
                        if value[0] == 0:
                            sys = 'ubuntu'
                        else:
                            value == commands.getstatusoutput('cat /proc/version | grep -q -E -i "centos|red hat|redhat"')
                            if value[0] == 0:
                                sys = 'centos'
                            else:
                                print('此脚本不支持你的系统!')
                                os._exit(0)

# 重新运行程序
def restart_program():
    os.system('python iptables_forward.py')

# 安装iptables
def install_iptables():
    status = commands.getstatusoutput('iptables -V')
    if status[1] != '':
        print('已安装iptables')
        raw_input('按任意键继续')
        restart_program()
    else:
        print('iptables未安装,开始安装~~~')
        if sys == 'centos':
            os.system('yum update&&yum install -y iptables')
        else:
            os.system('apt-get update&&apt-get install -y iptables')
        status = commands.getstatusoutput('iptables -V')
        if status[1] != '':
            print('已完成安装iptables')
            raw_input('按任意键继续')
            restart_program()
        else:
            print('iptables未安装,请检查可能是系统不支持')
            raw_input('按任意键继续')
            os._exit(0)

# 获得ip
def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

# 添加iptables端口转发
def add_forward():

    forward_ip = raw_input('输入本地ip(回车自动获取):') or get_host_ip()
    print(forward_ip)

    forward_port = raw_input('输入本地端口(默认10000):') or '10000'
    print(forward_port)

    forwarded_ip = raw_input('输入被转发ip:')
    print(forwarded_ip)

    forwarded_port = raw_input('输入被转发端口(默认' + forward_port + '):') or forward_port
    print(forwarded_port)

    forward_type = raw_input('请输入数字 来选择 iptables 转发类型(默认TCP+UDP):\n1.TCP\n2.UDP\n3.TCP+UDP\n') or '3'

    while forward_type == '1' or '2' or '3':
        if forward_type == '1':
            os.system(
                'iptables -t nat -A PREROUTING -p tcp -m tcp --dport ' + forward_port + ' -j DNAT --to-destination ' + forwarded_ip + ':' + forwarded_port + '&&'
                'iptables -t nat -A POSTROUTING -d ' + forwarded_ip + ' -p tcp -m tcp --dport ' + forwarded_port + ' -j SNAT --to-source ' + forward_ip)
            break
        elif forward_type == '2':
            os.system(
                'iptables -t nat -A PREROUTING -p udp -m udp --dport ' + forward_port + ' -j DNAT --to-destination ' + forwarded_ip + ':' + forwarded_port + '&&'
                'iptables -t nat -A POSTROUTING -d ' + forwarded_ip + ' -p udp -m udp --dport ' + forwarded_port + ' -j SNAT --to-source ' + forward_ip)
            break
        elif forward_type == '3':
            os.system(
                'iptables -t nat -A PREROUTING -p tcp -m tcp --dport ' + forward_port + ' -j DNAT --to-destination ' + forwarded_ip + ':' + forwarded_port + '&&'
                'iptables -t nat -A PREROUTING -p udp -m udp --dport ' + forward_port + ' -j DNAT --to-destination ' + forwarded_ip + ':' + forwarded_port + '&&'
                'iptables -t nat -A POSTROUTING -d ' + forwarded_ip + ' -p tcp -m tcp --dport ' + forwarded_port + ' -j SNAT --to-source ' + forward_ip + '&&'
                'iptables -t nat -A POSTROUTING -d ' + forwarded_ip + ' -p udp -m udp --dport ' + forwarded_port + ' -j SNAT --to-source ' + forward_ip)
            break
        else:
            forward_type = raw_input('输入错误!!!\n请再次输入数字 来选择 iptables 转发类型(默认TCP+UDP):\n1.TCP\n2.UDP\n3.TCP+UDP\n') or '3'
    choice = raw_input('是否需要继续添加y/n(默认y):') or 'y'
    if choice == 'y':
        add_forward()
        # 开启防火墙的ipv4转发
        os.system('echo -e "net.ipv4.ip_forward=1" >> /etc/sysctl.conf&&sysctl -p')
        # 配置iptables开机加载
        if sys == 'centos':
            os.system('service iptables save&&chkconfig --level 2345 iptables on')
        else:
            os.system(
                'iptables-save > /etc/iptables.up.rules&&echo -e ''#''!/bin/bash\\n/sbin/iptables-restore < /etc/iptables.up.rules'' > /etc/network/if-pre-up.d/iptables&&chmod +x /etc/network/if-pre-up.d/iptables')
    else:
        restart_program()

# 清空iptables端口转发
def del_all_forwarding():
    num = commands.getstatusoutput('iptables -t nat -vnL POSTROUTING')
    all_num = num[1].count('*')/2
    a = 0
    while a < all_num:
        os.system('iptables -t nat -D POSTROUTING 1&&iptables -t nat -D PREROUTING 1')
        a = a+1
    if a == all_num:
        print('所有规则已清除')
        raw_input('按任意键继续')
        restart_program()
    else:
        print('清除未成功')
        raw_input('按任意键继续')
        restart_program()

# 查看iptables端口转发
def view_forwarding():
    show = commands.getoutput('iptables -t nat -vnL POSTROUTING')
    print(show+'\n以上是你现有的规则')
    raw_input('按任意键回到主菜单')
    restart_program()
#删除iptables端口转发
def del_forwarding():
    show = commands.getoutput('iptables -t nat -vnL POSTROUTING')
    print(show + '\n以上是你现有的规则')
    raw_input('按任意键继续')
    if show == 'Chain POSTROUTING (policy ACCEPT 460 packets, 28030 bytes)\npkts bytes target prot opt in out source destination':
        raw_input('你没有任何端口转发,按任意键回主菜单')
        restart_program()
    else:
        no = raw_input('你想删除的规则序号(如1,2,3,4):')
        output = commands.getoutput('iptables -t nat -D POSTROUTING '+no+'&&iptables -t nat -D PREROUTING '+no)
        if output == 'iptables: Bad rule (does a matching rule exist in that chain?).':
            raw_input('你还没有添加规则或是没有输入序号,按任意键回到主菜单')
            restart_program()
        else:
            print('规则已删除')
            choice = raw_input('是否继续删除y/n(默认y):') or 'y'
            if choice == 'y':
                del_forwarding()
            else:
                print('回到主菜单')
                restart_program()

check_sys()

print('你当前的系统为'+sys)

select = raw_input('iptables端口转发一键管理脚本\n'
               '--------------------\n'
               '1.安装iptables\n'
               '2.清空iptables端口转发\n'
               '--------------------\n'
               '3.添加iptables端口转发\n'
               '4.查看iptables端口转发\n'
               '5.删除iptables端口转发\n'
               '--------------------\n'
               '6.退出当前脚本\n'
               '注意：初次使用前请请务必执行 1.安装iptables(不仅仅是安装)\n\n'
               '请输入数字 [1-6]:')
if select == '1':
    install_iptables()
elif select == '2':
    del_all_forwarding()
elif select == '3':
    add_forward()
elif select == '4':
    view_forwarding()
elif select == '5':
    del_forwarding()
elif select == '6':
    os._exit(0)
else:
    raw_input('输入出错,请重新输入,按任意键继续')
    restart_program()