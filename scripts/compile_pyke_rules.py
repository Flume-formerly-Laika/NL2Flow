"""
/**
 * @file compile_pyke_rules.py
 * @brief Compiles PyKE knowledge base rules for the application
 * @author Huy Le (huyisme-005)
 */
"""

import os

from pyke import krb_compiler


def main():

    """
    /**
     * @brief Main function to compile PyKE rules from .krb files
     * @return None
     * @throws Exception if compilation fails
     * @details Compiles field_mapping.krb into a knowledge base package
     */
    """

    src = os.path.join("app", "rules", "field_mapping.krb")
    pkg = "app.rules.kb_field_mapping"
    out = os.path.join("app", "rules", "kb_field_mapping")
    os.makedirs(out, exist_ok=True)
    krb_compiler.compile_krb(src, pkg, out, src)
    print("✅ Pyke rules compiled")

if __name__ == "__main__":
    main()
