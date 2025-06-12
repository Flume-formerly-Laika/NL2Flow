'''
@brief code for compiling krb files
@author Huy Le (huyisme-005)
@file compile_pyke_rules.py
'''

from pyke import krb_compiler
import os

krb_file = os.path.join("app", "rules", "field_mapping.krb")
generated_pkg = "app.rules"
generated_dir = os.path.join("app", "rules")

krb_compiler.compile_krb(krb_file, generated_pkg, generated_dir, krb_file)
print("Rules compiled successfully.")
