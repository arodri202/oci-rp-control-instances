# Copyright (c) 2016, 2018, Oracle and/or its affiliates.  All rights reserved.

import base64
import json
import os.path

from fdk import response

import oci.auth.signers.security_token_signer
import oci.signer


class ResourcePrincipalProvider:
    def __init__(self):
        self.reload()

        # Pull our tenancy from the RPST
        claims = json.loads(b64(self.rpst.split(".")[1]))
        self.tenancy = claims["res_tenant"]
        self.compartment = claims["res_compartment"]
        self.fn_id = claims["sub"]

        self.config = {"region": os.environ["OCI_REGION"], "tenancy": self.tenancy}

    def reload(self):
        base_dir = os.environ["OCI_RESOURCE_PRINCIPAL_DIR"]

        with open(os.path.join(base_dir, "rpst")) as f:
            self.rpst = f.read().strip()

        self.private = oci.signer.load_private_key_from_file(os.path.join(base_dir, "private.pem"))
        self.signer = oci.auth.signers.security_token_signer.SecurityTokenSigner(self.rpst, self.private)


def b64(s):
    s += "=" * ((4 - len(s) % 4) % 4)
    try:
        return base64.b64decode(s)
    except:
        pass
    if s.startswith("ST$"):
        try:
            return base64.b64decode(s[3:])
        except:
            pass
    return s


class MockResourcePrincipalProvider:
    """Something that looks like a ResourcePrincipalProvider but just uses the user's (developer's) local ~/.oci/config"""

    def __init__(self, profile=None, config_file="~/.oci/config"):
        if profile is None:
            profile = os.environ.get("OCI_CLI_PROFILE", "DEFAULT")
        config = self.config = oci.config.from_file("~/.oci/config", profile)
        self.tenancy = config["tenancy"]
        self.compartment = config.get("compartment", self.tenancy)
        self.region = config["region"]
        self.signer = oci.signer.Signer(
            tenancy=self.tenancy,
            user=config["user"],
            fingerprint=config["fingerprint"],
            private_key_file_location=config.get("key_file"),
            pass_phrase=oci.config.get_config_value_or_default(config, "pass_phrase"),
            private_key_content=config.get("key_content")
            )

    def reload(self):
        pass
