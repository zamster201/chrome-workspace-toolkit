from pyvda import VirtualDesktop, get_virtual_desktops

def get_current_virtual_desktop_id():
    current = VirtualDesktop.current()
    return str(current.id)

def get_current_virtual_desktop_index():
    current = VirtualDesktop.current()
    all_desktops = get_virtual_desktops()
    return all_desktops.index(current) + 1

def get_virtual_desktop_id_map():
    """Returns a dict of {desktop_number: friendly_name} for all current desktops"""
    return {i + 1: (d.name or f"Desktop #{i + 1}") for i, d in enumerate(get_virtual_desktops())}

def get_virtual_desktop_guid_map():
    """Returns a dict of {desktop_number: guid_string} for restore matching"""
    return {i + 1: str(d.id) for i, d in enumerate(get_virtual_desktops())}

def get_virtual_desktop_by_id(desktop_id):
    """Find and return a VirtualDesktop object by its ID"""
    for d in get_virtual_desktops():
        if str(d.id) == str(desktop_id):
            return d
    return None