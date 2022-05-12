import re
#from decrypt_hike import decrypt
from decrypt_api import decrypt

with open("./level0.js") as f:
    content = f.read()

def escape(s:str):
    return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n")

arg_re = re.compile("[\"\'](.*?)[\"\']")

cnt = 0
## dealing with hike's obfuscation
#func_name = "jaira"
#func_re = re.compile(f"({func_name}\\( *[\"\'].*?[\"\'], *[\"\'].*?[\"\'] *\\))")
# for call in func_re.findall(content):
#     cnt += 1
#     arg1, arg2 = arg_re.findall(call)
#     content = content.replace(call, ' "'+escape(decrypt(arg1, arg2))+'" ')

# dealing with studyservice-api's obfuscation
for func in re.findall("([a-zA-Z0-9_]+?)\\(\"0x[0-9a-f]+?\"\\)", content):
    for call in re.findall(f"(?<![a-zA-Z0-9_])({func}\\( *[\"\'].*?[\"\'] *\\))", content):
        index = arg_re.search(call).group(1)
        print(func, index)
        content = content.replace(call, ' "'+escape(decrypt(index))+'" ')
        cnt += 1

print("total: ", cnt)

with open("./level1.js", "w") as f:
    f.write(content)



