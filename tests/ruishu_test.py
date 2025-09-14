import curl_cffi

"""
https://github.com/FlareSolverr/FlareSolverr

https://freedium.cfd/https://medium.com/the-riff/ozzy-osbourne-legacy-of-a-madman-264a0a6c30c5

https://zhuanlan.zhihu.com/p/697358189
"""
# r = curl_cffi.get("https://zhuanlan.zhihu.com/p/697358189",
#                   impersonate="chrome")

r = curl_cffi.get("https://freedium.cfd/https://medium.com/the-riff/ozzy-osbourne-legacy-of-a-madman-264a0a6c30c5",
                 impersonate="chrome")
print(r.text)
