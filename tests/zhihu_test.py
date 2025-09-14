"""
==> Checking connectivity with the snap store
===> System doesn't have a working snapd, skipping
Unpacking chromium-browser (2:1snap1-0ubuntu2) ...
Setting up chromium-browser (2:1snap1-0ubuntu2) ...
update-alternatives: using /usr/bin/chromium-browser to provide /usr/bin/x-www-browser (x-www-browser) in auto mode
update-alternatives: using /usr/bin/chromium-browser to provide /usr/bin/gnome-www-browser (gnome-www-browser) in auto mode

是否使用 neko集群 来承接  但是需要控制并发 一个neko同一时间只能有一个进程访问
"""
import time

# https://freedium.cfd/https://medium.com/the-riff/ozzy-osbourne-legacy-of-a-madman-264a0a6c30c5


from DrissionPage import WebPage, ChromiumOptions

# co = ChromiumOptions().set_paths(browser_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe')
# .set_paths(browser_path=r"/usr/bin/chromium-browser")
co = ChromiumOptions()
# co.headless(True)  # 设置无头加载  无头模式是一种在浏览器没有界面的情况下运行的模式，它可以提高浏览器的性能和加载速度
co.incognito(True)  # 无痕隐身模式打开的话，不会记住你的网站账号密码的

co.set_argument("--disable-gpu")  # 禁用GPU加速可以避免浏览器在加载页面时使用过多的计算资源，从而提高加载速度
co.set_user_agent(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')  # 设置ua

page = WebPage(chromium_options=co, session_or_options=False)

page.get('https://zhuanlan.zhihu.com/p/697358189')

print(page.html)

# close_btn = page.ele('.Modal-closeButton')
# if close_btn:
#     close_btn.click()

page.wait.ele_displayed('@aria-label=关闭', timeout=10)

# 点击关闭按钮
close_btn = page.ele('@aria-label=关闭')
if close_btn:
    close_btn.click()

time.sleep(1)
page.get_screenshot('./zhihu.png')
page.quit()
