Docker Image
~~~~~~~~~~~~

Optim3D is also available as `Docker
image <https://hub.docker.com/r/yarroudh/optim3d>`__.

These are the steps to run Optim3D as a Docker container:

1. First pull the image using the `docker pull` command:

.. code:: bash

   docker pull yarroudh/optim3d

2. To run the Docker container and mount your data inside it, use the
   `docker run` command with the `-v` option to specify the path to the host
   directory and the path to the container directory where you want to
   mount the data folder. For example:

.. code:: bash

   docker run -d -v ABSOLUTE_PATH_TO_HOST_DATA:/home/user/data yarroudh/optim3d

This command will start a Docker container in detached mode, mount the
**ABSOLUTE_PATH_TO_HOST_DATA** directory on the host machine to the
**/home/user/data** directory inside the container, and run the
**yarroudh/optim3d** image. Do not change the path of the directory inside
the container.

3. Find the container ID and copy it. You can use the `docker ps` command
   to list all running containers and their IDs.
4. Launch a command inside the container using `docker exec`, use the
   container ID or name and the command you want to run. For example:

.. code:: bash

   docker exec CONTAINER_ID optim3d index2d data/FILE_NAME
   docker exec CONTAINER_ID optim3d index3d data/FILE_NAME
   docker exec CONTAINER_ID optim3d tiler3d
   docker exec CONTAINER_ID optim3d reconstruct
   docker exec CONTAINER_ID optim3d post

5. To copy the output of the command from the container to a local path,
   use the `docker cp` command with the container ID or name, the path to
   the file inside the container, and the path to the destination on the
   host machine. For example:

-  To copy the output of one command:

.. code:: bash

   docker cp CONTAINER_ID:/home/user/output/footprint_tiles PATH_ON_HOST_MACHINE

This will copy the output of footprints tiling. Please check the results section for the output structure.

-  Top copy the output of all the commands:

.. code:: bash

   docker cp CONTAINER_ID:/home/user/output PATH_ON_HOST_MACHINE

6. Finally, after executing all the commands and copying the results to
   your local machine, you can stop the Docker container using the
   `docker stop` command followed by the container ID or name:

.. code:: bash

   docker stop CONTAINER_ID