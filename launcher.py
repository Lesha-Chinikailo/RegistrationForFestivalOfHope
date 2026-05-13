import subprocess
import sys
import os
import webbrowser
import time
import socket
import tempfile
import shutil


def find_free_port():
    """Находит свободный порт"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def main():
    # Находим свободный порт
    port = find_free_port()

    # Открываем браузер через секунду
    def open_browser():
        time.sleep(2)
        webbrowser.open(f'http://localhost:{port}')

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Определяем путь к app.py
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
        app_path = os.path.join(base_path, 'app.py')
    else:
        app_path = 'app.py'

    # Запускаем Streamlit
    cmd = [
        sys.executable, '-m', 'streamlit', 'run', app_path,
        '--server.port', str(port),
        '--server.headless', 'true',
        '--browser.gatherUsageStats', 'false',
        '--server.enableCORS', 'false',
        '--server.enableXsrfProtection', 'false',
        '--global.developmentMode', 'false',
        '--server.fileWatcherType', 'none',
    ]

    try:
        process = subprocess.Popen(cmd)
        process.wait()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Ошибка: {e}")
        input("Нажмите Enter для выхода...")


if __name__ == '__main__':
    main()