# Copyright (c) 2023, Amal Paul and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from rapid_deploy.rapid_deploy import deploy
import threading

class Deployment(Document):
    
    def before_submit(self):
        script_id = 'Script', self.script
        host_group_id = 'Host', self.host_group

        print(f"{script_id}\n{host_group_id}")

        script = frappe.db.get_value('Script', script_id, 'script')


        host_group = frappe.get_doc('Host Group', host_group_id)
        hosts = []
        for host_group_child in host_group.hosts:
            host_id = host_group_child.host
            hosts.append(frappe.db.get_value('Host', host_id, ['ip_address','username','password','ssh_port'], as_dict=1))

        # deploy.run(hosts,f"bash -c '{script}'")
        t = threading.Thread(target=deploy.run, args=(hosts,f"bash -c '{script}'"))
        t.start()