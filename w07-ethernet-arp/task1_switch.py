#!/usr/bin/env python3
import argparse

class Switch:
    BROADCAST = "ff:ff:ff:ff:ff:ff"
    AGE_SECONDS = 300

    def __init__(self, ports):
        self.num_ports = ports
        self._mac_table = {}
        self.current_time = 0.0

    def handle(self, frame, in_port):
        src_mac, dst_mac, time = frame
        self.current_time = max(self.current_time, time)
        self._mac_table[src_mac] = (in_port, time)
        flood_ports = [p for p in range(self.num_ports) if p != in_port]

        if dst_mac == self.BROADCAST:
            return flood_ports

        if dst_mac in self._mac_table:
            dst_port, last_seen = self._mac_table[dst_mac]
            if self.current_time - last_seen <= self.AGE_SECONDS:
                if dst_port == in_port:
                    return []
                return [dst_port]

        return flood_ports

    def table(self):
        active_table = {}
        for mac, (port, last_seen) in list(self._mac_table.items()):
            if self.current_time - last_seen <= self.AGE_SECONDS:
                active_table[mac] = port
            else:
                del self._mac_table[mac]
        return active_table

# ------------------------------------------------------------------- harness
A, B, C = "00:00:00:00:00:0a", "00:00:00:00:00:0b", "00:00:00:00:00:0c"
BC = Switch.BROADCAST

def verify():
    fails = 0
    def check(label, got, want):
        nonlocal fails
        ok = got == want
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<46} {got}"
              + ("" if ok else f"   want {want}"))
        fails += not ok

    try:
        s = Switch(4)
    except NotImplementedError:
        print("  Switch is still a stub"); return 1

    check("unknown destination floods", s.handle((A, B, 0.0), 0), [1, 2, 3])
    check("known destination is not flooded", s.handle((B, A, 1.0), 2), [0])
    check("learned both", s.table(), {A: 0, B: 2})
    check("broadcast floods", s.handle((A, BC, 2.0), 0), [1, 2, 3])
    check("never back out the arrival port", s.handle((C, A, 3.0), 0), [])
    check("station moved, table follows", (s.handle((B, A, 4.0), 3), s.table()[B]), ([0], 3))
    s.handle((C, BC, 400.0), 1)
    check("aged-out entry is gone", A in s.table(), False)

    print(f"\n  {'all ok' if not fails else str(fails) + ' failed'}")
    return 1 if fails else 0

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    raise SystemExit(verify() if a.verify else p.print_help())
