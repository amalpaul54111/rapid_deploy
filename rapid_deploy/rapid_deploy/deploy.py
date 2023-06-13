import paramiko
import threading
import frappe

def ssh_command(host, command, lock, log):
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
            log.output = output
            log.errors = errors
            log.exit_code = exit_code
            if exit_code == 0:
                log.success = True

    finally:
        client.close()


def run(hosts, command, deployment):

    lock = threading.Lock()
    threads = []
    for host in hosts:
        print(f"Running command on {host['ip_address']} ")
        # doc = frappe.get_doc({'doctype': 'Host Log', 'title': 'New Log'})
        # doc.deployment = deployment
        # doc.host = host
        t = threading.Thread(target=ssh_command, args=(host, command, lock))
        threads.append(t)
        # doc.db_insert()
        t.start()

    for thread in threads:
        thread.join()