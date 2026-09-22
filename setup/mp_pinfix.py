"""Milk Bar map-pin fix.

The mod's InjectDLL scans Cemu's memory for the 32 player map markers using the pattern
[icon 06][X 12340.5][Y 2345.5]. In this game build the marker table stores the icon AFTER the
position, so the byte before X is 00 and the scan never matches; after 15 retries the DLL throws
and Cemu closes ("Could not find map pin address"). Writing 06 into that (otherwise zero) byte
for each of the 32 records makes the scan match while the DLL is still retrying.

usage: python mp_pinfix.py [seconds-to-wait-for-cemu]
"""
import ctypes, ctypes.wintypes as wt, subprocess, sys, time, os

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
k32.OpenProcess.restype = wt.HANDLE
k32.ReadProcessMemory.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
k32.WriteProcessMemory.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
PARKED = bytes.fromhex("4640D20045129800")
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mp_pinfix.log")


class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_void_p), ("AllocationBase", ctypes.c_void_p), ("AllocationProtect", wt.DWORD),
                ("PartitionId", wt.WORD), ("RegionSize", ctypes.c_size_t), ("State", wt.DWORD), ("Protect", wt.DWORD), ("Type", wt.DWORD)]


k32.VirtualQueryEx.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.POINTER(MBI), ctypes.c_size_t]
k32.VirtualQueryEx.restype = ctypes.c_size_t


def log(msg):
    line = time.strftime("%H:%M:%S ") + msg
    print(line, flush=True)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def cemu_pid():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Cemu.exe", "/FO", "CSV", "/NH"], capture_output=True, text=True,
                         creationflags=0x08000000).stdout
    for line in out.splitlines():
        parts = line.strip().strip('"').split('","')
        if len(parts) > 1 and parts[1].isdigit():
            return int(parts[1])
    return None


def big_regions(h):
    addr, m = 0, MBI()
    while addr < 0x7FFFFFFFFFFF and k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(m), ctypes.sizeof(m)):
        base = m.BaseAddress or 0
        if m.State == 0x1000 and not (m.Protect & 0x101) and m.RegionSize >= 64 << 20:
            yield base, m.RegionSize
        addr = base + m.RegionSize


def find_markers(h):
    hits = []
    for base, size in big_regions(h):
        off = 0
        while off < size:
            n = min(64 << 20, size - off)
            buf = ctypes.create_string_buffer(n)
            got = ctypes.c_size_t()
            if k32.ReadProcessMemory(h, ctypes.c_void_p(base + off), buf, n, ctypes.byref(got)) and got.value:
                data = buf.raw[:got.value]
                i = data.find(PARKED)
                while i >= 0:
                    hits.append(base + off + i)
                    i = data.find(PARKED, i + 1)
            off += n
    return hits


def main():
    wait = float(sys.argv[1]) if len(sys.argv) > 1 else 300
    t0 = time.time()
    pid = None
    while time.time() - t0 < wait and not pid:
        pid = cemu_pid()
        if not pid:
            time.sleep(2)
    if not pid:
        log("no Cemu appeared"); return 1
    log("Cemu pid %d" % pid)
    h = k32.OpenProcess(0x0438, False, pid)  # QUERY_INFORMATION | VM_READ | VM_WRITE | VM_OPERATION
    if not h:
        log("OpenProcess failed: %d" % ctypes.get_last_error()); return 1
    while time.time() - t0 < wait + 240:
        hits = find_markers(h)
        if len(hits) >= 32:
            break
        log("markers found: %d, waiting for the game to load them" % len(hits))
        time.sleep(3)
    else:
        log("gave up waiting for markers"); return 1
    hits.sort()
    # the real table is 32 records exactly 0x40 apart; anything after that is a stopper we planted earlier
    records = [hits[0]]
    for a in hits[1:]:
        if a - records[-1] == 0x40 and len(records) < 32:
            records.append(a)
    extra = [a for a in hits if a not in records]
    log("found %d records at %#x (complete table: %s), %d extra copies after it" % (len(records), records[0], len(records) == 32, len(extra)))
    if len(records) < 32:
        log("table incomplete; not touching memory"); return 2
    hits = records
    stopper_exists = any(a > hits[-1] for a in extra)
    patched = 0
    for a in hits:
        cur = ctypes.create_string_buffer(1); got = ctypes.c_size_t()
        k32.ReadProcessMemory(h, ctypes.c_void_p(a - 1), cur, 1, ctypes.byref(got))
        if cur.raw == b"\x06":
            continue
        if cur.raw != b"\x00":
            log("unexpected byte %s before marker at %#x, leaving it" % (cur.raw.hex(), a)); continue
        w = ctypes.c_size_t()
        if k32.WriteProcessMemory(h, ctypes.c_void_p(a - 1), ctypes.c_char_p(b"\x06"), 1, ctypes.byref(w)) and w.value == 1:
            patched += 1
    log("patched %d marker records" % patched)

    # The DLL's loop looks for a 33rd marker after the 32nd with no upper bound. On this machine
    # there are exactly 32 copies of the pattern, so it walks off the end of Cemu's memory and
    # crashes (access violation ~30 s later). Plant one terminator copy in the first zero-filled
    # gap after the table so the loop stops there. Nothing ever writes to that 33rd address.
    last = hits[-1]
    if stopper_exists:
        log("stopper already present after the table; nothing more to do"); return 0
    after = ctypes.create_string_buffer(0x40); got = ctypes.c_size_t()
    k32.ReadProcessMemory(h, ctypes.c_void_p(last + 0x40), after, 0x40, ctypes.byref(got))
    log("bytes after the last record: %s" % after.raw[:got.value].hex(" "))
    window = 0x20000
    buf = ctypes.create_string_buffer(window)
    k32.ReadProcessMemory(h, ctypes.c_void_p(last + 0x40), buf, window, ctypes.byref(got))
    data = buf.raw[:got.value]
    if data.find(PARKED) >= 0:
        log("a terminator already exists %#x bytes after the table" % data.find(PARKED)); return 0
    # first 4-byte-aligned spot at or after +0x40 where 16 bytes are zero; write 8 bytes in, so the
    # pattern is preceded by 8 untouched zeros
    zeros = b"\x00" * 16
    i = data.find(zeros)
    while i >= 0 and i % 4:
        i = data.find(zeros, i + 1)
    if i < 0:
        log("no 16-byte zero gap within %#x bytes after the table; not planting a terminator" % window); return 2
    target = last + 0x40 + i + 8
    w = ctypes.c_size_t()
    if k32.WriteProcessMemory(h, ctypes.c_void_p(target), ctypes.c_char_p(PARKED), 8, ctypes.byref(w)) and w.value == 8:
        log("planted terminator at %#x (%#x bytes after the last record)" % (target, target - last))
    else:
        log("failed to plant terminator: %d" % ctypes.get_last_error()); return 2
    return 0


def loop_forever():
    """--loop: patch every Cemu that appears, for as long as this process lives."""
    while True:
        pid = cemu_pid()
        if not pid:
            time.sleep(2); continue
        main()
        while cemu_pid() == pid:
            time.sleep(3)


if __name__ == "__main__":
    if "--loop" in sys.argv:
        sys.argv = [a for a in sys.argv if a != "--loop"]
        loop_forever()
    sys.exit(main())
