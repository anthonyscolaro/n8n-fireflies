# Fireflies All-in-One App

This app lets you collect Fireflies recordings for Brandon and browse them easily with Streamlit.

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
- This will start both the PostgreSQL database and the Streamlit app in separate containers.
- The first time you run this, Docker will build the Streamlit app image.

### 4. Access the App
- Open your browser and go to [http://localhost:8501](http://localhost:8501)
- You can now browse and filter Brandon's recordings.

---

## 🚀 Deployment (Run on a Remote Server like DigitalOcean)

Follow these steps to deploy the app for remote access:

### 1. Create a DigitalOcean Droplet
- Go to [DigitalOcean](https://cloud.digitalocean.com/droplets)
- Create a new droplet (Ubuntu 22.04+, 1GB+ RAM)
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

### 5. Start the App with Docker Compose
```sh
docker-compose up -d
```
- This will start both the PostgreSQL database and the Streamlit app in separate containers.

### 6. Access the App
- The app will be available at:
  - **Production:** https://ff.projectassistant.ai
  - **Staging:** https://staging.ff.projectassistant.ai
- You must configure your DNS and reverse proxy (e.g., Nginx) to point these URLs to your server's public IP and port 8501.

### 7. Open Firewall Ports
- In the DigitalOcean dashboard, open these ports:
  - **5432** (PostgreSQL, only if you need remote DB access)
  - **8501** (Streamlit web app)

---

## ⚙️ Environment Variables

All environment variables are set in `docker-compose.yml` under the `web` and `db` services. You do NOT need to create a `.env` file for the Python app.

**Database variables (used by the app):**
- `DB_HOST`: Database host (should be `db` for Docker Compose)
- `DB_PORT`: Database port (default: `5432`)
- `DB_USER`: Database username (default: `firefliesuser`)
- `DB_PASSWORD`: Database password (default: `firefliespass`)
- `DB_NAME`: Database name (default: `firefliesdb`)

**PostgreSQL variables (used by the db service):**
- `POSTGRES_USER`: Database username
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name

If you change any of these in `docker-compose.yml`, make sure the values match between the `db` and `web` services.

---

## 🧠 Cline Memory Bank

The Cline Memory Bank lets you save, search, and manage notes or context snippets directly within the Fireflies app interface.

**Capabilities:**
- Add new notes with a title and content
- Search notes by title
- View all notes in a table
- Notes are stored in the PostgreSQL database for persistence

**How to use:**
- Use the "Cline Memory Bank" section in the app interface to add or search notes.
- All notes are persistent and can be managed from the web UI.

---

## 🛠️ Troubleshooting
- Make sure Docker is running: `docker ps` should show both the database and web containers.
- If you change database credentials, update them in both `docker-compose.yml` services.
- To reset the database: `docker-compose down -v` then `docker-compose up -d`.
- For production, use a process manager (like systemd or pm2) for Docker if needed. 