To use your Docker container on another computer, you can follow these steps:

---

### **Step 1: Push Your Container to Docker Hub (Already Done)**
If you've already pushed your images (`bkarthik7/cns_backend` and `bkarthik7/cns_frontend`) to Docker Hub, you're ready to pull them on another machine.Once that is done go to next step

---

### **Step 2: Install Docker on the Other Machine**
Ensure that Docker is installed on the target machine. You can download and install Docker from [Docker's official website](https://www.docker.com/products/docker-desktop/) or use package managers like `apt` (Ubuntu) or `brew` (MacOS).

---

### **Step 3: Pull the Images on the Target Machine**
On the target machine, pull the images from Docker Hub using the following commands:

```bash
docker pull bkarthik7/cns_backend:latest
docker pull bkarthik7/cns_frontend:latest
```

---

### **Step 4: Run the Containers**
Run the containers using the following commands:

1. **Run the backend container**:
   ```bash
   docker run -d -p 8000:8000 bkarthik7/cns_backend:latest
   ```
   This maps the backend service to port `8000` on the target machine.

2. **Run the frontend container**:
   ```bash
   docker run -d -p 80:80 bkarthik7/cns_frontend:latest
   ```
   This maps the frontend service to port `80` on the target machine.

---

### **Step 5: Test the Application**
1. Access the **frontend** by opening a browser and navigating to `http://<TARGET_MACHINE_IP>` (default port 80).
2. Access the **backend** by navigating to `http://<TARGET_MACHINE_IP>:8000`.
3. Usually <TARGET_MACHINE_IP> is localhost

---

### **Alternative: Use Docker Compose**
If the project requires both frontend and backend services to work together, you can:
1. Copy your `docker-compose.yml` file to the target machine.
2. Run the following commands on the target machine:
   ```bash
   docker-compose pull
   docker-compose up
   ```

This ensures both services run as defined in your `docker-compose.yml`.

---
