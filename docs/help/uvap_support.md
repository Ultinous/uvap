---
id: uvap_support
title: Support
hide_title: true
---

# Support

In case of an unresolvable issue regarding UVAP, email support@ultinous.com
with the details.

# Problem Reporting

1. Describe the issue and the environment.

1. Take a screenshot (if that can help for debugging).

1. Show the list of docker container status:
    
    ```
    $ docker ps -a
    ```
    
1. Give the log lines of the problematic component with the
   `docker logs <NAME_OF_DOCKER_CONTAINER>` command. For example:
   
   ```
   $ docker logs uvap_mgr
   ```
  
