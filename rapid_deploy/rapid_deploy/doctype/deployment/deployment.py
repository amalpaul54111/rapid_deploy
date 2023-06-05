# Copyright (c) 2023, Amal Paul and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import ansible_runner

class Deployment(Document):
    
    def before_submit(self):
        script_id = 'Scripts', self.script
        host_id = 'Host', self.hosts

        print(f'Host: {host.ip_address}\nPassword: {host.password}')
        print(f'Script: {script.script}')

