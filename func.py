import io
import json
import sys
import importlib
from fdk import response

import oci.core

sys.path.append(".")
import rp

def handler(ctx, data: io.BytesIO=None):
    provider = rp.ResourcePrincipalProvider() # initialized provider here
    resp = do(provider)
    return response.Response(
        ctx, response_data=json.dumps(resp),
        headers={"Content-Type": "application/json"}
    )


def do(provider):
    # List instances (in IAD) --------------------------------------------------------------------------------
    client = oci.core.ComputeClient(provider.config, signer=provider.signer)
    # Use this API to manage resources such as virtual cloud networks (VCNs), compute instances, and block storage volumes.
    try:
        inst = client.list_instances(provider.compartment)
        finst = []

        for i in inst.data:
            finst.append( [i.id, i.display_name])

            if (i.lifecycle_state == "RUNNING"):
                client.instance_action(i.id, "SOFTSTOP")
            else:
                client.instance_action(i.id, "START")

    except Exception as e:
        inst = str(e)

    resp = {
             "instances": finst,
            }

    return resp

def main():
    # If run from the command-line, fake up the provider by using stock user credentials
    provider = rp.MockResourcePrincipalProvider()
    resp = do(provider)
    print((resp))
    print(json.dumps(resp))


if __name__ == '__main__':
    main()
