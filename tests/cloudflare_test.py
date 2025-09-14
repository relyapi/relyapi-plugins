"""
cb-lb

https://www.bilibili.com/video/BV1Dm421x73t/?vd_source=44c52730b7b5612e95a86d9473811e95

代码文章：https://articles.zsxq.com/id_weapaj332b75.html
dp作者官方文档 https://drissionpage.cn/get_start/installation
1、设置无头模式：co.headless(True)
2、设置无痕模式：co.incognito(True)
3、设置访客模式：co.set_argument('--guest')
4、设置请求头user-agent：co.set_user_agent()
5、设置指定端口号：co.set_local_port(9211)

<iframe src="https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/b/turnstile/if/ov2/av0/rcv/73cdg/0x4AAAAAAADnPIDROrmt1Wwj/light/fbE/new/normal/auto/" allow="cross-origin-isolated; fullscreen; autoplay" sandbox="allow-same-origin allow-scripts allow-popups" id="cf-chl-widget-73cdg" tabindex="0" title="包含 Cloudflare 安全质询的小组件" style="border: none; overflow: hidden; width: 300px; height: 65px;"></iframe>
"""

from DrissionPage import ChromiumPage, ChromiumOptions
from loguru import logger

# .set_paths(user_data_path=r'C:\Users\PC\Desktop\user_data\qMtPicXA')
co = ChromiumOptions()
# co.incognito(True)
# co.set_argument('--guest')
# co = ChromiumOptions().set_paths(browser_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
value = '确认您是真人'

browser = ChromiumPage(co)  # 创建对象
browser.set.window.max()
browser.get(
    'https://freedium.cfd/https://medium.com/the-riff/ozzy-osbourne-legacy-of-a-madman-264a0a6c30c5',
    retry=3, interval=2, timeout=15)
# browser.get("https://cn.airbusan.com/content/common/customercenter/noticeList", retry=3, interval=2, timeout=15)  # 访问网

logger.info(f"user_agent is {browser.user_agent}")
browser.wait(10)

# checkbox = browser.ele('input[type="checkbox"]')
# checkbox.click()

# browser.ele(f'x://input[@value="{value}"]').click()
# browser.wait(2)
print('start')

label = browser.ele('label:hasText("确认您是真人")')

if label:
    label.click()  # 点击 label 会自动触发 checkbox 勾选
else:
    print('未找到 label')

print(print(browser.cookies().as_dict()))
