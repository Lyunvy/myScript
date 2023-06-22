# -- coding: utf-8 --
import requests
from lxml import etree
import time
from random import randint

# 如果脚本位置在青龙默认通知脚本所在目录的下一级目录，则需取消以下两行注释
# import sys
# sys.path.append("..")
import notify

requests.packages.urllib3.disable_warnings()


def pt_signin(cookie, signin_url):
    session = requests.Session()
    headers = {'cookie': cookie,
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'}
    signin_url = signin_url
    res = session.get(signin_url, headers=headers).text
    html = etree.HTML(res)
    msg = html.xpath(
        '//td[@class="embedded"]/h2/text()|//td[@class="embedded"]//p//text()|//td[@class="embedded"]//b//text()|//*[@class="embedded"]//*[@class="text"]//text()')

    if not msg:
        return "无法获取签到信息"

    msg = msg[0] + ',' + ''.join(msg[1:]) + '\n'
    try:
        msg1 = ''.join(html.xpath('//*[@id="outer"]//a/font/text()|//*[@id="outer"]//a/font/span/text()'))
        if "未" in msg1:
            msg += msg1
    except:
        pass
    return msg


if __name__ == '__main__':
    site_ob = [
        {
            'website': '', # 站点名字
            'signin_url': '', #站点签到链接，例如 https://example.com/attendance.php
            'cookie': 'c_secure_uid=; c_secure_ssl=;...'
        },
    ]
    t = randint(0, 10)
    print(f'延迟{int(t/60)}分{t%60}秒执行任务')
    time.sleep(t)
    output_msg = ""
    for i in site_ob:
        try:
            website = i['website']
            cookie = i['cookie']
            signin_url = i['signin_url']
            msg = f"{website}\n{pt_signin(cookie, signin_url)}"

            if '无法获取签到信息' in msg:
                output_msg += f"{website} 无法获取签到信息, signin_url: {signin_url} {msg}\n"
            elif '签到成功' not in msg:
                if any(word in msg for word in ['重复', '抱歉']):
                    output_msg += f"{website} 重复签到\n"
                else:
                    output_msg += f"{website} 签到失败, signin_url: {signin_url} {msg}\n"
            else:
                output_msg += f"{website} 签到成功\n"
        except Exception as e:
            print(e)
    # 调用青龙面板配置的通知方式对签到结果进行通知
    notify.send(title='PT 签到结果', content=output_msg)
