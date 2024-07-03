## Getting Started

### Pull and run docker image

   1. First authenticate with your github credentials (if you haven't already)

   ```bash
   docker login ghcr.io -u <username> --password-stdin
   ```

   Replace < username > with your GitHub username and enter your personal access token (PAT) that has the read:packages scope.

   2. Pull the image

   ```bash
   docker pull ghcr.io/islemmedjahdi/itouch-api-marketplace-backend:latest
   ```

  3. Run the container

  ```bash
  docker run -p 5000:5000 ghcr.io/islemmedjahdi/itouch-api-marketplace-backend:latest
  ```
