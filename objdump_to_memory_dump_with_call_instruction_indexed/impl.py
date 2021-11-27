import subprocess
from os.path import realpath, join, dirname, exists
import re

base_dir = join(dirname(realpath(__file__)), '..')

prog_disassembled_bytes = re.compile(r'([0-9a-zA-Z]+):\s*([0-9a-zA-Z ]+)\s*([\(\)<>a-z]*)')
prog_symbol = re.compile(r'([0-9a-zA-Z]+)\s*<([a-zA-Z0-9_]+)>:')

call_ins_opcodes = [0xff, 0xe8, 0x9A]

class MemoryDump:
    def __init__(self, path_to_executable, use_objdump_txt_if_possible=True):
        if exists(path_to_executable):
            if exists(path_to_executable+".objdump.txt") and use_objdump_txt_if_possible:
                print("objdum.txt exists, gonna use it.")
                with open(path_to_executable+".objdump.txt", 'r') as f:
                    output = f.read()
            else:
                cmd = ["C:\\Program Files\\mingw-w64\\x86_64-8.1.0-posix-seh-rt_v6-rev0\\mingw64\\bin\\objdump", "-D", "-z", "--section=.text", f"{path_to_executable}"]
                output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout
                output = str(output, 'ascii')
        else:
            raise Exception(path_to_executable+" does not exist.")

        prev_addr = None
        prev_memory_bytes = None
        prev_instruction = None

        ret_bytes = []
        ret_callins_index = []
        ret_symbol_index = []
        ret_retaddr_index = []

        base_addr = None
        for line_str in output.splitlines():
            # print(line_str)
            match = prog_disassembled_bytes.match(line_str)
            if match:
                # print('re matched')
                addr_str, memory_bytes_str, instruction = match.groups()
                addr = int(addr_str, 16)
                memory_bytes = [int(i, 16) for i in memory_bytes_str.strip().split(' ')]

                if base_addr is None:
                    base_addr = addr

                n = addr+len(memory_bytes)-base_addr-len(ret_bytes)
                if n > 0:
                    if n > len(memory_bytes):
                        print("*" * 20)
                        print(n)
                        print(hex(prev_addr), [hex(mb) for mb in prev_memory_bytes], prev_instruction)
                        print(hex(addr), [hex(mb) for mb in memory_bytes], instruction, flush=True)
                        raise Exception("A gap is found in memory bytes")
                    ret_bytes.extend(memory_bytes[-n:])
                    assert(len(ret_bytes) == addr+len(memory_bytes)-base_addr)

                if instruction.lower().startswith('call'):
                    idx = addr-base_addr
                    ret_callins_index.append(idx)
                    ret_retaddr_index.append(idx+len(memory_bytes))

                    # if memory_bytes[0] not in call_ins_opcodes or ret_bytes[idx] not in call_ins_opcodes:
                    #     print('*'*20)
                    #     print(addr_str, memory_bytes_str, instruction)
                    #     print(idx, hex(ret_bytes[idx]))
                    #     print(len(ret_bytes))



                prev_addr = addr
                prev_memory_bytes = memory_bytes
                prev_instruction = instruction
            else:
                symbol_math = prog_symbol.match(line_str)
                if symbol_math:
                    addr_str, symbol = symbol_math.groups()
                    addr = int(addr_str, 16)
                    if base_addr is None:
                        base_addr = addr
                    ret_symbol_index.append(addr-base_addr)
                    # print(addr_str, symbol)


        for idx in ret_callins_index:
            if ret_bytes[idx] not in call_ins_opcodes:
                print("WARNING: possible wrong call ins detected: ", hex(ret_bytes[idx]))

        assert(len(ret_retaddr_index) == len(ret_callins_index))

        self.base_addr = base_addr
        self.memory_bytes = ret_bytes
        self.callins_index = ret_callins_index
        self.symbol_index = ret_symbol_index
        self.retaddr_index = ret_retaddr_index

if __name__ == "__main__":
    md = MemoryDump(join(base_dir, "test_executables", "kernel32.dll"))

    print("size of memory bytes = ", len(md.memory_bytes))
    print(f"found {len(md.callins_index)} call instructions")
    print(f'has {len(md.symbol_index)} symbols')

    for idx in set(md.symbol_index) & set(md.callins_index):
        print(hex(idx+md.base_addr))

    s = set()
    for idx in range(len(md.retaddr_index)):
        diff = md.retaddr_index[idx]-md.callins_index[idx]
        s.add(diff)

    print(s)
