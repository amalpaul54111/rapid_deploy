import paramiko
import threading
import frappe

def ssh_command(host, command, lock):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())    

    try:
        client.connect(
            hostname=host['ip_address'],
            port=host['ssh_port'],
            username=host['username'],
            password=host['password']
        )
        
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        errors = stderr.read().decode()
        exit_code = stdout.channel.recv_exit_status()
        
        with lock:
            host['output'] = output
            host['errors'] = errors
            host['exit_code'] = exit_code

    finally:
        client.close()


def run(hosts, command):

    lock = threading.Lock()
    threads = []
    for host in hosts:
        print(f"Running command on {host['ip_address']} ")
        t = threading.Thread(target=ssh_command, args=(host, command, lock))
        threads.append(t)
        t.start()

    for thread in threads:
        thread.join()

    print("Deployment Completed")