import matplotlib.pyplot as plt
import mpld3
from mpld3._server import serve
fig1 =plt.figure()

plt.plot([3,1,4,1,5], 'ks-', mec='w', mew=5, ms=20)
#mpld3.show(ip='192.168.178.31', port=8889)


fig2 =plt.figure()
plt.plot([3,1,4,1,5], 'ks-', mec='w', mew=5, ms=20)
#mpld3.show(ip='192.168.178.31', port=8889)


# create html for both graphs 
html1 = mpld3.fig_to_html(fig1)
html2 = mpld3.fig_to_html(fig2)
# serve joined html to browser
serve(html1+html2, ip='192.168.178.31', port=8889)


import socket
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


print(get_ip())