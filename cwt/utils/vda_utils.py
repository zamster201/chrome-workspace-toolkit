from pyvda import VirtualDesktop

def get_current_virtual_desktop_id():
    current = VirtualDesktop.current()
    return str(current.id)

def get_current_virtual_desktop_index():
    current = VirtualDesktop.current()
    all_desktops = VirtualDesktop.get_desktops()
    return all_desktops.index(current) + 1

def get_virtual_desktop_id_map():
    """Returns a dict of {desktop_number: desktop_id} for all current desktops"""
    return {i + 1: str(d.id) for i, d in enumerate(VirtualDesktop.get_desktops())}

def get_virtual_desktop_by_id(desktop_id):
    """Find and return a VirtualDesktop object by its ID"""
    for d in VirtualDesktop.get_desktops():
        if str(d.id) == str(desktop_id):
            return d
    return None

