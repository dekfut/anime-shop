import http.server
import socketserver
import os
import sys
import subprocess
import atexit
import signal

DIRECTORY = "/home/nyxorelle/Рабочий стол/antigravity/ItStep/ITSTEP project html ANIME SHOP /html"
PORT = 8848

FRP_BIN = "/home/nyxorelle/Рабочий стол/antigravity/frp_0.71.1_linux_amd64/frpc"
FRP_CONF = "/home/nyxorelle/Рабочий стол/antigravity/frp_0.71.1_linux_amd64/frpc.toml"

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # Если обращение к корню '/', отдаем error503.html
        if self.path == '/' or self.path.split('?')[0] == '/':
            self.path = '/error503.html'
        return super().do_GET()

    def do_HEAD(self):
        if self.path == '/' or self.path.split('?')[0] == '/':
            self.path = '/error503.html'
        return super().do_HEAD()

def start_frpc_if_not_running():
    # Проверяем, запущен ли frpc
    try:
        output = subprocess.check_output(["pgrep", "-f", "frpc.*frpc.toml"]).decode().strip()
        if output:
            print(f"[frpc] Уже запущен (PID: {output.split()[0]})")
            return None
    except subprocess.CalledProcessError:
        pass

    # Если не запущен — запускаем
    if os.path.exists(FRP_BIN) and os.path.exists(FRP_CONF):
        print(f"[frpc] Запуск frpc: {FRP_BIN} -c {FRP_CONF}")
        proc = subprocess.Popen([FRP_BIN, "-c", FRP_CONF])
        
        def kill_frpc():
            try:
                proc.terminate()
            except Exception:
                pass
        atexit.register(kill_frpc)
        return proc
    else:
        print("[frpc] Бинарник или конфиг не найден!")
        return None

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == '__main__':
    frpc_proc = start_frpc_if_not_running()
    
    try:
        with ReusableTCPServer(("0.0.0.0", PORT), CustomHTTPRequestHandler) as httpd:
            print(f"==================================================")
            print(f" Сайт запущен!")
            print(f" Локально:    http://127.0.0.1:{PORT}/")
            print(f" Из мира:     http://87.120.187.210:8930/")
            print(f"==================================================")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nОстановка сервера...")
        if frpc_proc:
            frpc_proc.terminate()
