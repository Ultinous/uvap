---
id: uvap_upgrade
title: Upgrading UVAP
sidebar_label: Upgrade Procedure 
hide_title: true
---

# Upgrading UVAP

New versions of UVAP are released regularly. You can use the following set of
commands to upgrade to the latest version of UVAP:

1. Ensure you are logged in as `ultinous`. If necessary, log out and log in
   with `ultinous` user.

1. Check license validity:

    ```
    $ grep "Expiration Date" "${UVAP_HOME}/license/license.txt"
    ```

    > **Note:**  
	The received date must be in the future.  
    If the license has expired, contact support@ultinous.com.

1. Update helper scripts from GithHub:

    ```
    $ cd "${UVAP_HOME}"
    git pull
    ```

1. Update Docker images. Run the install script, it collects all Docker images
   for UVAP:

    ```
    $ "${UVAP_HOME}/scripts/install.sh"
    ```