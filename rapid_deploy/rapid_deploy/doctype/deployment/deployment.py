# Copyright (c) 2023, Amal Paul and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import paramiko
import threading

class Deployment(Document):

    def ssh_command(self, host, command, lock):
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

    def run(self, hosts, command, deployment):

        lock = threading.Lock()
        threads = []
        for host in hosts:
            print(f"Running script on {host['ip_address']}")
            t = threading.Thread(target=self.ssh_command, args=(host, command, lock))
            threads.append(t)
            t.start()

        for thread in threads:
            thread.join()
        
        failure = 0
        success = 0

        for host in hosts:
            if host['exit_code'] == 0:
                success = success + 1
            else:
                failure = failure + 1
        
        if failure == 0:
            comment = f'Deployment Succeded<br>All the hosts succeded in the deployment'
        elif success == 0 :
            comment = f'Deployment Failed<br>All the hosts exited with error <br><code>{hosts[1]["errors"]}</code>'
        else:
            comment = f'Deployment Succeded partially<br>Success: {success}<br>Failure: {failure}'
        doc = frappe.new_doc('Comment')
        doc.comment_type = "Comment"
        doc.content = f'<div class=ql-editor read-mode"><p>{comment}</p><p><br></p></div>'
        doc.reference_doctype = 'Deployment'
        doc.reference_name = deployment
        doc.modified_by = 'System'
        doc.insert(ignore_permissions=True)

        frappe.publish_realtime(event='msgprint', message='Deployment Done', user=frappe.session.user) 
        # frappe.publish_realtime(event='msgprint', message='Deployment Done', user=frappe.session.user, doctype='Deployment')
        print("Deployment completed")

        for host in hosts:
            with lock:
                doc = frappe.new_doc("Host Log")
                doc.deployment = deployment
                if host['exit_code'] == 0:
                    doc.success = True
                doc.host = host.ip_address
                doc.output = host['output']
                doc.errors = host['errors']
                doc.exit_code = host['exit_code']
                doc.datetime = frappe.utils.now()
                doc.insert(ignore_permissions=True)
    
    def before_submit(self):
        script_id = self.script
        host_group_id = self.host_group

        print(f"Deployment {self.name1} submitted on {host_group_id} with script {script_id}")

        script = frappe.db.get_value('Script', script_id, 'script')


        host_group = frappe.get_doc('Host Group', host_group_id)
        hosts = []
        for host_group_child in host_group.hosts:
            host_id = host_group_child.host
            hosts.append(frappe.db.get_value('Host', host_id, ['ip_address','username','password','ssh_port'], as_dict=1))

        #add timeout for the run function with enqueue timeout
        command = f"bash -c '{script}'"
        frappe.enqueue(self.run, hosts=hosts, command=command, deployment=self.name)

    # def before_save(self):
    #     self.before_submit()