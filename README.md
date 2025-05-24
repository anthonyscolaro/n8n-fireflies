# Fireflies All-in-One App

This app lets you collect Fireflies recordings for Brandon and browse them easily with Streamlit.

## Quick Start

### 1. Start PostgreSQL with Docker Compose

```
docker-compose up -d
```

This will start PostgreSQL and create the `recordings` table automatically.

### 2. Run the N8N Workflow
- Import and run the provided N8N workflow to fetch Brandon's recordings and store them in the database.

### 3. Install Python Dependencies

```
pip install -r requirements.txt
```

### 4. Start the Streamlit App

```
streamlit run fireflies_streamlit_app.py
```

Then open the provided local URL in your browser to browse and filter Brandon's recordings.

---

## Deploying to DigitalOcean

You can deploy this app to a DigitalOcean droplet for remote access and automation.

### 1. Create a Droplet
- Go to [DigitalOcean](https://cloud.digitalocean.com/droplets)
- Create a new droplet (Ubuntu 22.04 recommended, 1GB+ RAM)
- Add your SSH key or set a root password
- Note the droplet's public IP address

### 2. SSH Into Your Droplet
```
ssh root@your_droplet_ip
```

### 3. Install Docker and Docker Compose
```
apt update && apt install -y docker.io docker-compose git
systemctl enable --now docker
```

### 4. Clone Your Project Repo
```
git clone https://github.com/yourusername/fireflies-app.git
cd fireflies-app
```

### 5. Start PostgreSQL
```
docker-compose up -d
```

### 6. Install Python and Streamlit
```
apt install -y python3 python3-pip
pip3 install -r requirements.txt
```

### 7. Run the Streamlit App
```
nohup streamlit run fireflies_streamlit_app.py --server.port 8501 --server.address 0.0.0.0 &
```
- The app will be available at `http://your_droplet_ip:8501`

### 8. (Optional) Run N8N on the Droplet
- You can install N8N using Docker or npm, or connect to your existing N8N instance.
- If running N8N here, expose its port (default 5678) and set up the workflow as before.

### 9. Open Firewall Ports
- Make sure ports 5432 (PostgreSQL, if remote access needed), 8501 (Streamlit), and 5678 (N8N, if used) are open in your DigitalOcean dashboard.

---

## Troubleshooting
- Make sure Docker is running.
- If you change the database credentials, update them in both `docker-compose.yml` and `fireflies_streamlit_app.py`.
- If you want to reset the database, run `docker-compose down -v` and then `docker-compose up -d` again.
- For production, consider using a process manager (like systemd or pm2) for Streamlit and N8N. 