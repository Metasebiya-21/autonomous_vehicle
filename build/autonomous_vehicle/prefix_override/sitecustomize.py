import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/metasebiya/autonomous_vehicle_ws/install/autonomous_vehicle'
