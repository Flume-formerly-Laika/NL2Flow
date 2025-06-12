'''
@brief code for compiling krb files
@author Huy Le (huyisme-005)
@file compile_pyke_rules.py
'''

from pyke import krb_compiler
import os

krb_file = "app/rules/field_mapping.krb"
generated_root_pkg = "app.rules"
generated_root_dir = os.path.dirname(krb_file)

krb_compiler.compile_krb(krb_file, generated_root_pkg, generated_root_dir, krb_file)
print("Compilation successful!")
