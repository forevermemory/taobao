#!/usr/bin/python
#-*- coding:utf-8 -*-
import os
import paramiko


# stdin, stdout, stderr = ssh.exec_command('cd /mnt/apps/')
# print(stdout.read().decode())
# print(stderr.read().decode())


def exec_command(client,cmd):
    try:
        stdin, stdout, stderr = client.exec_command(cmd,get_pty=True)
        # logWriteToTxt(self.sitename + "执行"+cmd)
        res=""
        # return stdout.read().decode()
        results = stdout.readlines()
 
        for line in results:
            res+=line
        try:
            err=stderr.readlines()
            for line in err:
                res+=line
        except:
            pass
        return res
    except:
        pass


def get_ssh_conn():
    try:
        private_key = paramiko.RSAKey.from_private_key_file('/root/.ssh/id_rsa_new')
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname = '116.62.240.28', port=22, username="deploy", pkey=private_key)
        return ssh
    except Exception as err:
        print(err)


def main():
    os.popen('rm cpm.tar.gz ').read()
    os.popen('tar -zcvf cpm.tar.gz --exclude=*.git *').read()
    print('打包完成')
    os.popen('scp cpm.tar.gz deploy@116.62.240.28:/home/deploy/apps/').read()
    print('上传完成')
    # exec_scp()  rm -rf cpm/;tar -zxvf cpm.tar.gz
    client = get_ssh_conn()
    print('建立连接')
    exec_command(client,'rm -rf /home/deploy/apps/cpm/*;cd /home/deploy/apps;mkdir cpm;mv cpm.tar.gz cpm;cd cpm;tar -zxvf cpm.tar.gz;rm /home/deploy/apps/cpm/cpm/settings.py;cd cpm;cp settings_.py settings.py')
    print('部署结束')
    client.close()

if __name__ == "__main__":
    main()
