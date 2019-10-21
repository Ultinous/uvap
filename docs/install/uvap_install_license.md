---
id: uvap_install_license
title: License Key
hide_title: true
---

# License Key

Components of UVAP are protected against illegal access. In order to access the
components, the collection of some information is necessary.

>Note:  
To gather the necessary information for licensing, make sure the Docker
environment is up and running.
For more information, see [Adding Docker Environment]

## Collect Information for Licensing

To gather the information needed for the access:

1. Collect the hardware information for license generation:

   ```text
   $ mkdir -p /tmp/uvap && nvidia-docker run --rm -u $(id -u) \
   ultinous/licence_data_collector > /tmp/uvap/data.txt
   ```

1. Save `/tmp/uvap/data.txt` file, as it is needed at later step during the
   installation.
   
1. Create a Docker account on
   <a href="https://hub.docker.com/" target="_blank">Docker Hub</a>.
   In order to access the docker images of UVAP, an account is required.

   > **Attention!**  
   The password of the Docker account is stored on the computer in a plain-text
   format, so it is recommended to choose a strong auto-generated password that
   is not used anywhere else.

1. Log in to the Docker account:

   ```
   $ docker login
   ```

## Request Access to Licensed Resources

To request and get access to licensed resources:

1. Send an email to support@ultinous.com with the following details:

   - Subject of email: `UVAP - Requesting access to licensed resources`
   - The DockerHub account ID, created previously
   - The hardware information, which can be found in the file `/tmp/uvap/data.txt`

   Based on the information above, you will receive the following:

   - The license text and key
   - Access to the UVAP Docker repository `ultinous/uvap`
   - A download URL for AI resources
     >Note:  
	 The download URL is valid for only 72 hours.

1. Save the license text as `"${UVAP_HOME}/license/license.txt"`
   and the license key as `"${UVAP_HOME}/license/license.key"`.

1. The license is provided within the following two files:

   * `licence.txt`:

     ```text
     Product Name    = UVAP Multi Graph Runner
     GPU             = aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
     Expiration Date = 2018-01-01
     Customer        = Demo User
     ```

   * `licence.key`:

     ```text
     --- No human readable key data ---
     ```
   
   >**Note:**  
   Without the license files, the installation process can be continued until
   the UVAP usage.

1. Download the AI resources

   In the following command, substitute `[DOWNLOAD_URL]` with the
   download URL received from `support@ultinous.com`:

   ```text
   $ mkdir -p "${UVAP_HOME}/models"
   $ cd "${UVAP_HOME}/models"
   $ wget -q -O - "[DOWNLOAD_URL]" | tar xzf -
   ```

The steps above are not meant to have a working environment yet, only intended
to quickly check that the access to all requested resources is granted.


[Adding Docker Environment]: uvap_install_setup.md#adding-docker-environment