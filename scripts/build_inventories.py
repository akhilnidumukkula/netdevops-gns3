from app.lab import Lab

def main():
    lab = Lab.create()
    lab.build_ansible_inventories("ansible/inventory")
    lab.build_ansible_inventories("ansible/inventory-big", random_data=True)
    lab.build_nornir_inventory("nornir/inventory")
    
if __name__ == "__main__":
    main()
