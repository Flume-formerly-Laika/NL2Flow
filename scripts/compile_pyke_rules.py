import os
from pyke import krb_compiler

def main():
    src = os.path.join("app", "rules", "field_mapping.krb")
    pkg = "app.rules.kb_field_mapping"
    out = os.path.join("app", "rules", "kb_field_mapping")
    os.makedirs(out, exist_ok=True)
    krb_compiler.compile_krb(src, pkg, out, src)
    print("✅ Pyke rules compiled")

if __name__ == "__main__":
    main()
