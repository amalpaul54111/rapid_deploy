# Copyright (c) 2023, Amal Paul and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import paramiko
import frappe

class Host(Document):

	def before_save(self):
		ip_address = self.ip_address

		print(f"Adding host {ip_address}")
		command = f"echo {self.name.strip()} > ~/hostname.txt"
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())    
		print("Adding hosts")
		try:
			client.connect(
				hostname=self.ip_address,
				port=self.ssh_port,
				username=self.username,
				password=self.password
			)
			
			stdin, stdout, stderr = client.exec_command(command)
			output = stdout.read().decode()
			errors = stderr.read().decode()
			exit_code = stdout.channel.recv_exit_status()

			updateapi_script = frappe.db.get_value('Script', '8ee6a0dc2b', 'script')
			stdin, stdout, stderr = client.exec_command(f"echo '{updateapi_script}' > ~/script.py")
			output = stdout.read().decode()
			errors = stderr.read().decode()
			exit_code = stdout.channel.recv_exit_status()

			add_cron_job_script = frappe.db.get_value('Script', 'c2ecabb913', 'script')
			stdin, stdout, stderr = client.exec_command(f"bash -c '{add_cron_job_script}'")
			output = stdout.read().decode()
			errors = stderr.read().decode()
			exit_code = stdout.channel.recv_exit_status()

			print(f"Output: {output}")
			print(f"Errors: {errors}")	

			print("Done adding host")
		finally:
			client.close()
