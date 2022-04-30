import re
from decrypt import decrypt

func_name = "jaira"

with open("./level1.js") as f:
    content = f.read()

func_re = re.compile(f"({func_name}\\( *[\"\'].*?[\"\'], *[\"\'].*?[\"\'] *\\))")
arg_re = re.compile("[\"\'](.*?)[\"\']")

def escape(s:str):
    return s.replace("\\", "\\\\").replace("\"", "\\\"")

cnt = 0
for func in func_re.findall(content):
    cnt += 1
    arg1, arg2 = arg_re.findall(func)
    content = content.replace(func, ' "'+escape(decrypt(arg1, arg2))+'" ')
print("total", cnt)


with open("./level2.js", "w") as f:
    f.write(content)



