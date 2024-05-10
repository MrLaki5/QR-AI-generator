# QR-AI-generator
Transform ordinary QR codes into engaging visual experiences with AI technology.

## Setup
* Required dependencies
    * [Docker](https://docs.docker.com/engine/install/)
    * [Docker compose](https://docs.docker.com/compose/install/)
    * [Nvidia container toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

* Clone the repo
    ``` bash
    git clone https://github.com/MrLaki5/QR-AI-generator.git
    git lfs install
    git submodule update --init --recursive
    ```

* Start the application
    ```
    docker compose up -d
    ```

* Open starting page in browser under link *localhost:8089*
