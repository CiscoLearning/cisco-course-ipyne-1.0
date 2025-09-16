from netmiko import ConnectHandler

ROUTER_IP = "10.0.0.103" 

cisco_router = {
    "device_type": "cisco_ios",
    "host": ROUTER_IP,
    "username": "cisco",
    "password": "cisco",
    "secret": "cisco",
}

connection = ConnectHandler(**cisco_router)
connection.enable() 

output = connection.send_command("show ip interface brief")
print(output)

connection.disconnect()