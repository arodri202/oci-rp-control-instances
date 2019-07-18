# Copyright (c) 2016, 2018, Oracle and/or its affiliates.  All rights reserved.
import io
import json
import sys
from fdk import response

from oci import pagination
from oci import identity
from oci import core
from oci import auth


def handler(ctx, data: io.BytesIO=None):
    signer = auth.signers.get_resource_principals_signer()
    compartment_name = ""
    instance_name = ""
    action = ""

    try:
        body = json.loads(data.getvalue())
        compartment_name = str(body["compartment"])
        instance_name = str(body["instance"])
        action = str(body["action"]).upper()


    except Exception as ex:
        print(str(ex), file=sys.stderr)
        usage = (" usage: echo -n '{\"compartment\":"
                "\"<compartment name>\", \"instance\": \"<instance name>\","
                "\"action\": \"<action type>\"}' | fn invoke --app "
                "<app name> <function name> ")
        raise Exception(usage)

    resp = do(signer, compartment_name, instance_name, action)
    return response.Response(
        ctx, response_data=json.dumps(resp),
        headers={"Content-Type": "application/json"}
    )


def do(signer, compartment_name, instance_name, action):
    compartment = get_compartment(signer, compartment_name)

    client = core.ComputeClient(config={}, signer=signer)
    instance = get_instance(signer, compartment, instance_name, client)
    state = "INVALID ACTION INPUTTED. VALID INPUTS INCLUDE: STOP, START, RESET"

    if action == "STOP" or action == "SOFTSTOP":
        instance = client.instance_action(instance.id, "SOFTSTOP").data
        state = instance.lifecycle_state
    elif action == "START":
        instance = client.instance_action(instance.id, "START").data
        state = instance.lifecycle_state
    elif action == "RESET" or action == "RESTART":
        instance = client.instance_action(instance.id, "SOFTRESET").data
        state = instance.lifecycle_state

    resp = {
             "instance": instance.display_name,
             "state": state
            }

    return resp

def get_compartment(signer, compartment_name):
    """
    Identifies compartment ID by its name within the particular tenancy
    :param signer: OCI resource principal signer
    :param compartment_name: OCI tenancy compartment name
    :return: OCI tenancy compartment
    """
    identity_client = identity.IdentityClient(config={}, signer=signer)
    result = pagination.list_call_get_all_results(
        identity_client.list_compartments,
        signer.tenancy_id,
        compartment_id_in_subtree=True,
        access_level="ACCESSIBLE",
    )
    for c in result.data:
        if compartment_name == c.name:
            print(type(c))
            return c

    raise Exception("compartment not found")

def get_instance(signer, compartment, instance_name, compute_client):
    """
    Identifies instance ID by its name within the particular compartment
    :param signer: OCI resource principal signer
    :param compartment: OCI tenancy compartment returned by IdentityClient
    :param instance_name: OCI compute instance name
    :param compute_client: OCI ComputeClient
    :return: OCI tenancy compartment
    """
    result = pagination.list_call_get_all_results(
        compute_client.list_instances,
        compartment.id,
    )

    for i in result.data:
        if instance_name == i.display_name:
            print(type(i))
            return i

    raise Exception("instance not found")
