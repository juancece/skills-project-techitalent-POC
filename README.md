# Google Bigquery for Skills POC in Techitalent
## Running the Application with Docker Compose
For this POC it is only needed to run the docker-compose from this repo
### Prerequisites
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Setup

1. **Clone the Repository** (if applicable):
   `git clone https://github.com/juancece/skills-project-techitalent-POC.git`
   
   `cd python-bigquery`
3. **Build and Run with Docker Compose**:
4. 
   `docker-compose up --build`
   
   This command will build the Docker image and start the container as defined in the `docker-compose.yml` file. The `--build` flag ensures that Docker Compose rebuilds the image if there have been changes.

   `http://localhost:8000`

   Replace `8000` with the appropriate port number if you have modified it in the `docker-compose.yml` file.

### Stopping the Application

To stop the application, use the following command in the terminal:

`docker-compose down`

This command stops and removes the containers, networks, volumes, and images created by `docker-compose up`.
