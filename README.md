# Fireflies All-in-One App

This app lets you collect Fireflies recordings for Brandon and browse them easily with Streamlit. It includes a full Docker setup with nginx reverse proxy and Adminer for database management.

---

## 🏗️ Architecture Overview

**Services:**
- **PostgreSQL Database** (`localhost:5432`) - Data storage with health checks
- **Streamlit App** (`localhost:8501`) - Main application interface  
- **Adminer** (`localhost:8080`) - Database management web UI
- **Nginx Reverse Proxy** (`localhost:8090`) - Routes traffic and serves both app and Adminer

---

## 🚀 Local Development (Run on Your Own Computer)

Follow these steps exactly to get the app running locally:

### 1. Install Prerequisites
- **Install Docker Desktop:** [Download here](https://www.docker.com/products/docker-desktop/)
- **Install Git:** [Download here](https://git-scm.com/downloads)

### 2. Clone the Repository
Open a terminal and run:
```sh
git clone https://github.com/yourusername/fireflies-app.git
cd fireflies-app
```

### 3. Start the App with Docker Compose
In the project folder, run:
```sh
docker-compose up -d
```
- This will start PostgreSQL, Streamlit, Adminer, and nginx in separate containers
- The first time you run this, Docker will build the Streamlit app image
- Health checks ensure services start in the correct order

### 4. Access the App
**Main Access Points:**
- **Main App (via nginx):** [http://localhost:8090](http://localhost:8090)
- **Database Admin (via nginx):** [http://localhost:8090/adminer](http://localhost:8090/adminer)
- **Health Check:** [http://localhost:8090/health](http://localhost:8090/health)

**Direct Access (if needed):**
- **Streamlit Direct:** [http://localhost:8501](http://localhost:8501)
- **Adminer Direct:** [http://localhost:8080](http://localhost:8080)
- **PostgreSQL:** `localhost:5432`

---

## 🗄️ Database Management with Adminer

Adminer provides a web-based interface for managing your PostgreSQL database:

**Access:** [http://localhost:8090/adminer](http://localhost:8090/adminer)

**Login Credentials:**
- **System:** PostgreSQL
- **Server:** db
- **Username:** firefliesuser
- **Password:** firefliespass
- **Database:** firefliesdb

**Features:**
- Browse tables and data
- Run SQL queries
- Import/export data
- Manage database schema
- Beautiful Hydra theme pre-configured

---

## 🚀 Deployment (Run on a Remote Server like DigitalOcean)

Follow these steps to deploy the app for remote access:

### 1. Create a DigitalOcean Droplet
- Go to [DigitalOcean](https://cloud.digitalocean.com/droplets)
- Create a new droplet (Ubuntu 22.04+, 2GB+ RAM recommended)
- Add your SSH key or set a root password
- Note your droplet's public IP address

### 2. Connect to Your Droplet
On your local machine, run:
```sh
ssh root@your_droplet_ip
```

### 3. Install Required Software on the Droplet
Run these commands one by one:
```sh
apt update
apt install -y docker.io docker-compose git
systemctl enable --now docker
```

### 4. Clone the Project Repo
```sh
git clone https://github.com/yourusername/fireflies-app.git
cd fireflies-app
```

### 5. Update nginx Configuration for Production
Edit `nginx.conf` and update the server_name:
```nginx
server_name your_domain.com www.your_domain.com;
```

### 6. Start the App with Docker Compose
```sh
docker-compose up -d
```

### 7. Access the App
- **Main App:** http://your_domain.com:8090
- **Database Admin:** http://your_domain.com:8090/adminer
- **Health Check:** http://your_domain.com:8090/health

### 8. Open Firewall Ports
In the DigitalOcean dashboard, open these ports:
- **8090** (nginx reverse proxy - main access point)
- **5432** (PostgreSQL, only if you need remote DB access)
- **8501** (Streamlit, optional for direct access)
- **8080** (Adminer, optional for direct access)

---

## ⚙️ Environment Variables

All environment variables are configured in `docker-compose.yml`. No separate `.env` file needed.

**Database Configuration:**
- `DB_HOST`: Database host (`db` for Docker Compose networking)
- `DB_PORT`: Database port (`5432`)
- `DB_USER`: Database username (`firefliesuser`)
- `DB_PASSWORD`: Database password (`firefliespass`)
- `DB_NAME`: Database name (`firefliesdb`)

**PostgreSQL Service Variables:**
- `POSTGRES_USER`: Database username
- `POSTGRES_PASSWORD`: Database password  
- `POSTGRES_DB`: Database name

**Adminer Configuration:**
- `ADMINER_DEFAULT_SERVER`: Points to database service (`db`)
- `ADMINER_DESIGN`: UI theme (`hydra`)

---

## 🧠 Cline Memory Bank

The Cline Memory Bank lets you save, search, and manage notes or context snippets directly within the Fireflies app interface.

**Capabilities:**
- Add new notes with a title and content
- Search notes by title
- View all notes in a table
- Notes are stored in PostgreSQL with full persistence
- Manage notes via Adminer database interface

**How to use:**
- Use the "Cline Memory Bank" section in the app interface
- Access database directly via Adminer for advanced management
- All notes persist across container restarts

---

## 🔧 Service Management

**Check all services:**
```sh
docker-compose ps
```

**View logs:**
```sh
docker-compose logs
docker-compose logs [service_name]  # e.g., nginx, web, db, adminer
```

**Restart specific service:**
```sh
docker-compose restart [service_name]
```

**Stop all services:**
```sh
docker-compose down
```

**Stop and remove volumes (reset database):**
```sh
docker-compose down -v
```

---

## 🛠️ Troubleshooting

**Service Status:**
- Check all containers: `docker-compose ps`
- All services should show "Up" or "Up (healthy)" status

**Port Conflicts:**
- If port 8090 is in use, change it in `docker-compose.yml` nginx service
- Update nginx.conf if using different internal ports

**Database Issues:**
- Reset database: `docker-compose down -v && docker-compose up -d`
- Check logs: `docker-compose logs db`
- Use Adminer to inspect database state

**Nginx Issues:**
- Test config: `docker-compose exec nginx nginx -t`
- Check logs: `docker-compose logs nginx`
- Verify upstreams are reachable

**Health Checks:**
- PostgreSQL health: `docker-compose exec db pg_isready -U firefliesuser -d firefliesdb`
- App health: `curl http://localhost:8090/health`

**Network Issues:**
- Verify Docker network: `docker network ls`
- Check service connectivity: `docker-compose exec web ping db`

---

## 🔄 Development Workflow

1. **Make changes** to code or configuration files
2. **Rebuild if needed:** `docker-compose build [service_name]`
3. **Restart services:** `docker-compose up -d`
4. **Test via nginx:** http://localhost:8090
5. **Check logs:** `docker-compose logs -f`
6. **Commit changes:** `git add . && git commit -m "description"`

---

## 📊 Monitoring & Health

**Health Check Endpoints:**
- **Main Health:** http://localhost:8090/health
- **Database Status:** Check via Adminer or `docker-compose logs db`
- **Service Status:** `docker-compose ps`

**Performance:**
- All services include restart policies (`unless-stopped`)
- PostgreSQL includes proper health checks
- nginx includes timeout configurations for Streamlit WebSocket support 