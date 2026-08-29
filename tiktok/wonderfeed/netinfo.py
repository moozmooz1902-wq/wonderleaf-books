"""Work out the address other devices on the same network can use.

Staff should never install anything or open a terminal. One machine runs the
app; everyone else opens a link. That link needs this machine's address on the
local network, which is not something a non-technical user should have to find.
"""

import socket

PORT = 8501


def lan_ip():
    """This machine's address on the local network, or None.

    Opens a UDP socket toward a public address to discover which local
    interface would be used. Nothing is actually sent, and it works offline.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(0.5)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except OSError:
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except OSError:
            return None
    finally:
        s.close()
    if not ip or ip.startswith("127."):
        return None
    return ip


def urls(port=PORT):
    ip = lan_ip()
    return {
        "this_computer": f"http://localhost:{port}",
        "other_devices": f"http://{ip}:{port}" if ip else None,
    }


if __name__ == "__main__":
    u = urls()
    print()
    print("  ┌────────────────────────────────────────────────────┐")
    print("  │  WONDERFEED IS RUNNING                             │")
    print("  └────────────────────────────────────────────────────┘")
    print()
    print("  Your browser should have opened. If not, use the first link.")
    print()
    print(f"  On this computer:   {u['this_computer']}")
    if u["other_devices"]:
        print(f"  For your staff:     {u['other_devices']}")
        print()
        print("  Send that second link to your staff. They open it on their")
        print("  own phone or laptop - nothing to install, no terminal.")
        print("  They must be on the same wifi as this computer.")
    else:
        print("  (Could not detect a network address - staff link unavailable.)")
    print()
    print("  Ignore any line above saying \"External URL\". That is your public")
    print("  internet address, it will not work, and it should not be shared.")
    print()
    print("  Keep this window open. Closing it closes the page.")
    print("  Everything above this line is normal - it is not an error.")
    print()
