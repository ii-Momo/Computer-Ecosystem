from .cpu_state import reset_state
from .memory import Memory
from .executor_v1 import step


def make_mem(program: bytes, start: int = 0x0000) -> Memory:
    mem = Memory.blank()
    mem.load(start, program)
    return mem

file_path = input("Input your filepath (exp : home/usr/file.bin) : ")

with open(file_path, 'rb') as f:
    content_bytes = f.read()
f.close()

prog_str = ""


for i in content_bytes:
    hecks =str(hex(i))[2:]
    if len(hecks) < 2 :
        prog_str +="0" +hecks
    else :
        prog_str +=hecks

mem = make_mem(bytes.fromhex(prog_str))
st = reset_state()
st.pc = 0x0000

for _ in range(len(prog_str)//16):
    step(st, mem)
print(st)