# Resource Principal Function to Stop or Start all Instances in the Calling Compartment.

  This function uses Resource Principal to securely receive information about the user's information from OCI and controls the state of all instances within the compartment that calls the function.

  Uses the [OCI Python SDK](https://oracle-cloud-infrastructure-python-sdk.readthedocs.io/en/latest/index.html) to create a client that receive user information when called in the OCI or a valid config file exists.

  As you make your way through this tutorial, look out for this icon. ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-control-instances/master/images/userinput.png?token=AK4AYAQ534QXEF2JHIDUZRS5BP632) Whenever you see it, it's time for you to perform an action.


Pre-requisites:
---------------
  1. Start by making sure all of your policies are correct from this [guide](https://preview.oci.oraclecorp.com/iaas/Content/Functions/Tasks/functionscreatingpolicies.htm?tocpath=Services%7CFunctions%7CPreparing%20for%20Oracle%20Functions%7CConfiguring%20Your%20Tenancy%20for%20Function%20Development%7C_____4)

  2. Download [rp.py](https://github.com/arodri202/oci-rp-control-instances/blob/master/rp.py) and move it into your working directory.

  3. Have [Fn CLI setup with Oracle Functions](https://preview.oci.oraclecorp.com/iaas/Content/Functions/Tasks/functionsconfiguringclient.htm?tocpath=Services%7CFunctions%7CPreparing%20for%20Oracle%20Functions%7CConfiguring%20Your%20Client%20Environment%20for%20Function%20Development%7C_____0)

### Switch to the correct context
  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-control-instances/master/images/userinput.png?token=AK4AYAQ534QXEF2JHIDUZRS5BP632)
  ```
  fn use context <your context name>
  ```
  Check using
  ```
  fn ls apps
  ```

### Create or Update your Dynamic Groups
  In order to use and retrieve information about other OCI Services you must grant access to your Function via a dynamic group. If you've done this before, feel free to skip past this section, otherwise...

  For information on how to create a dynamic group, click [here.](https://preview.oci.oraclecorp.com/iaas/Content/Identity/Tasks/managingdynamicgroups.htm#To)

  When specifying a rule, consider the following examples:

  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-control-instances/master/images/userinput.png?token=AK4AYAQ534QXEF2JHIDUZRS5BP632)
  * If you want all functions in a compartment to be able to access a resource, enter a rule similar to the following that adds all functions in the compartment with the specified compartment OCID to the dynamic group:
  ```
  ALL {resource.type = 'fnfunc', resource.compartment.id = 'ocid1.compartment.oc1..aaaaaaaa23______smwa'}
  ```

  * If you want a specific function to be able to access a resource, enter a rule similar to the following that adds the function with the specified OCID to the dynamic group:
  ```
  resource.id = 'ocid1.fnfunc.oc1.iad.aaaaaaaaacq______dnya'
  ```

### Create or Update Policies
  Now that your dynamic group is created, we need two new policies that allows your new dynamic group to manage any resources you are interested in receiving information about, and allow a user group to manage the resource you want to control, in this case we will grant access to `instance-family` in the functions related compartment.

  Your policy should look something like this:

  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-control-instances/master/images/userinput.png?token=AK4AYAQ534QXEF2JHIDUZRS5BP632)
  ```
  Allow dynamic-group <your dynamic group name> to manage instance-family in compartment <your compartment name>
  Allow group <your group name> to manage instance-family in compartment <your compartment name>
  ```

  e.g.

  ```
  Allow dynamic-group demo-func-dyn-group to manage instance-family in compartment demo-func-compartment
  Allow group demo-functions-developers to manage instance-family in compartment demo-functions-compartment
  ```

  For more information on how to create policies, go [here.](https://docs.cloud.oracle.com/iaas/Content/Identity/Concepts/policysyntax.htm)



### (Optional) Have a config file in the ~/.oci directory
  If you would like to call the function from the command line you will need a valid config file.

  If you do not have one, go [here](https://preview.oci.oraclecorp.com/iaas/Content/Functions/Tasks/functionsconfigureocicli.htm?tocpath=Services%7CFunctions%7CPreparing%20for%20Oracle%20Functions%7CConfiguring%20Your%20Client%20Environment%20for%20Function%20Development%7C_____2)

Create application
------------------
  Get the python boilerplate by running:

  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-control-instances/master/images/userinput.png?token=AK4AYAQ534QXEF2JHIDUZRS5BP632)
  ```
  fn init --runtime python <function-name>
  ```
  e.g.
  ```
  fn init --runtime python control-instances
  ```
  Enter the directory, create a new `__init__.py` file so the directory can be recognized as a package by Python.

  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-control-instances/master/images/userinput.png?token=AK4AYAQ534QXEF2JHIDUZRS5BP632)
  ```
  cd control-instances
  touch __init__.py
  ```

### Create an Application that is connected to Oracle Functions
  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-control-instances/master/images/userinput.png?token=AK4AYAQ534QXEF2JHIDUZRS5BP632)
  ```
  fn create app <app-name> --annotation oracle.com/oci/subnetIds='["<subnet-ocid>"]'
  ```
  You can find the subnet-ocid by logging on to [cloud.oracle.com](https://cloud.oracle.com/en_US/sign-in), navigating to Core Infrastructure > Networking > Virtual Cloud Networks. Make sure you are in the correct Region and Compartment, click on your VNC and select the subnet you wish to use.

  e.g.
  ```
  fn create app resource-principal --annotation oracle.com/oci/subnetIds='["ocid1.subnet.oc1.phx.aaaaaaaacnh..."]'
  ```

Writing the Function
------------------
### Requirements
  Update your requirements.txt file to contain the following:

  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-control-instances/master/images/userinput.png?token=AK4AYAQ534QXEF2JHIDUZRS5BP632)
  ```
  fdk
  oci-cli
  ```

### Open func.py
  Update the imports so that you contain the following.

  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-control-instances/master/images/userinput.png?token=AK4AYAQ534QXEF2JHIDUZRS5BP632)
  ```python
  import io
  import json
  import sys
  from fdk import response

  import oci.core
  sys.path.append(".")
  import rp
  ```

  By calling `sys.path.append(".")` the Python interpreter is able to import the `rp.py` Python module in your directory that you downloaded earlier.

### The Handler method
  This is what is called when the function is invoked by Oracle Functions, delete what is given from the boilerplate and update it to contain the following:

  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-control-instances/master/images/userinput.png?token=AK4AYAQ534QXEF2JHIDUZRS5BP632)
  ```python
  def handler(ctx, data: io.BytesIO=None):
      provider = rp.ResourcePrincipalProvider() # initialized provider here
      resp = do(provider)
      return response.Response(
          ctx, response_data=json.dumps(resp),
          headers={"Content-Type": "application/json"}
      )
  ```

### The do method
  Create the following method.

  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-control-instances/master/images/userinput.png?token=AK4AYAQ534QXEF2JHIDUZRS5BP632)
  ```python
  def do(provider):
  ```
  This is where we'll put the bulk of our code that will connect to OCI and return the list of compartments in our tenancy.

  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-control-instances/master/images/userinput.png?token=AK4AYAQ534QXEF2JHIDUZRS5BP632)
  ```python
  # Control instances (in IAD) --------------------------------------------------------------------------------
    client = oci.core.ComputeClient(provider.config, signer=provider.signer)
    # Use this API to manage resources such as virtual cloud networks (VCNs), compute instances, and block storage volumes.
    try:
        inst = client.list_instances(provider.compartment)
        finst = []

        for i in inst.data:
            finst.append( [i.id, i.display_name])

            ## depending on the current state of the instance it will trigger the opposite state
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
  ```
  Here we are creating a [ComputeClient](https://oracle-cloud-infrastructure-python-sdk.readthedocs.io/en/latest/api/core/client/oci.core.ComputeClient.html) from the [OCI Python SDK](https://oracle-cloud-infrastructure-python-sdk.readthedocs.io/en/latest/index.html), which allows us to connect to OCI with the provider's data we get from Resource Principal and it allows us to make a call to compute services to get a list of all of our instances. We then call `instance_action` which takes in an instance id and a state, and sends a request to that instance to trigger the passed in state.

  For more information about `instance_action` and `lifecycle_states`, click [here.](https://oracle-cloud-infrastructure-python-sdk.readthedocs.io/en/latest/api/core/client/oci.core.ComputeClient.html?highlight=instance_action)

### Command Line Usage
  If you want to be able to invoke this function from the command line, copy and paste this at the bottom of your code.

  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-control-instances/master/images/userinput.png?token=AK4AYAQ534QXEF2JHIDUZRS5BP632)
  ```python
  def main():
      # If run from the command-line, fake up the provider by using stock user credentials
      provider = rp.MockResourcePrincipalProvider()
      resp = do(provider)
      print((resp))
      print(json.dumps(resp))


  if __name__ == '__main__':
      main()

  ```
Test
----
### Deploy the function

  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-control-instances/master/images/userinput.png?token=AK4AYAQ534QXEF2JHIDUZRS5BP632)
  ```
  fn -v deploy --app <your app name>
  ```

  e.g.

  ```
  fn -v deploy --app resource-principal
  ```

### Invoke the function

  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-control-instances/master/images/userinput.png?token=AK4AYAQ534QXEF2JHIDUZRS5BP632)
  ```
  fn invoke <your app name> <your function name>
  ```

  e.g.

  ```
  fn invoke resource-principal control-instances
  ```
  Upon success, you should see all of the instances in your compartment appear in your terminal.

  You can also check your instance's state by logging on to [cloud.oracle.com](https://cloud.oracle.com/en_US/sign-in) and navigating to Core Infrastructure > Compute > Instances
