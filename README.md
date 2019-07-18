# Resource Principal Function to Stop or Start all Instances in the Calling Compartment.

  This function uses Resource Principal to securely receive information about the user's information from OCI and controls the state of all instances within the compartment that calls the function.

  Uses the [OCI Python SDK](https://oracle-cloud-infrastructure-python-sdk.readthedocs.io/en/latest/index.html) to create a client that receive user information when called in the OCI or a valid config file exists.

  In this example we'll show how you can control a compute function using its name, and the OCI compartment that contains the application. To do this we'll use two API clients exposed by the OCI SDK:

  1. [IdentityClient](https://oracle-cloud-infrastructure-python-sdk.readthedocs.io/en/latest/api/identity/client/oci.identity.IdentityClient.html) - is used to manage users, groups, compartments, and policies. In this scenario we will use the client to find the compartment passed in by its name.

  2. [ComputeClient](https://oracle-cloud-infrastructure-python-sdk.readthedocs.io/en/latest/api/core/client/oci.core.ComputeClient.html) - is used to manage resources such as virtual cloud networks (VCNs), compute instances, and block storage volumes. In this scenario we will use this client to find the correct instance and change its state by calling `instance_action` which takes in an instance id and a state, and then sends a request to that instance to trigger the desired state.

  As you make your way through this tutorial, look out for this icon. ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-control-instances/master/images/userinput.png?token=AK4AYAQ534QXEF2JHIDUZRS5BP632) Whenever you see it, it's time for you to perform an action.


Pre-requisites:
---------------
  1. Start by making sure all of your policies are correct from this [guide](https://preview.oci.oraclecorp.com/iaas/Content/Functions/Tasks/functionscreatingpolicies.htm?tocpath=Services%7CFunctions%7CPreparing%20for%20Oracle%20Functions%7CConfiguring%20Your%20Tenancy%20for%20Function%20Development%7C_____4)

  2. Have [Fn CLI setup with Oracle Functions](https://preview.oci.oraclecorp.com/iaas/Content/Functions/Tasks/functionsconfiguringclient.htm?tocpath=Services%7CFunctions%7CPreparing%20for%20Oracle%20Functions%7CConfiguring%20Your%20Client%20Environment%20for%20Function%20Development%7C_____0)

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

Create application
------------------
 1. Create an Application that is connected to Oracle Functions
  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-control-instances/master/images/userinput.png?token=AK4AYAQ534QXEF2JHIDUZRS5BP632)
  ```
  fn create app <app-name> --annotation oracle.com/oci/subnetIds='["<subnet-ocid>"]'
  ```
  You can find the subnet-ocid by logging on to [cloud.oracle.com](https://cloud.oracle.com/en_US/sign-in), navigating to Core Infrastructure > Networking > Virtual Cloud Networks. Make sure you are in the correct Region and Compartment, click on your VNC and select the subnet you wish to use.

  e.g.
  ```
  fn create app resource-principal --annotation oracle.com/oci/subnetIds='["ocid1.subnet.oc1.phx.aaaaaaaacnh..."]'
  ```
  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-control-instances/master/images/userinput.png?token=AK4AYAQ534QXEF2JHIDUZRS5BP632)
  2. Clone this repository in a separate directory
  ```
  git clone https://github.com/arodri202/oci-rp-control-instances.git
  ```
  3. Change to the correct directory where you cloned this example.
  ```
  cd oci-rp-control-instances
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
  Upon success, you should see the name of the instance passed in as well as it's current lifecycle_state.

  You can also check your instance's state by logging on to [cloud.oracle.com](https://cloud.oracle.com/en_US/sign-in) and navigating to Core Infrastructure > Compute > Instances
