# Fireflies All-in-One App

This app lets you collect Fireflies recordings for Brandon and browse them easily with Streamlit. It includes a full Docker setup with nginx reverse proxy, Adminer for database management, and **ready-to-deploy DigitalOcean App Platform configuration**.

---

## 🏗️ Architecture Overview

**Services:**
- **PostgreSQL Database** (`localhost:5432`) - Data storage with health checks
- **Streamlit App** (`localhost:8501`) - Main application interface  
- **Adminer** (`localhost:8080`) - Database management web UI
- **Nginx Reverse Proxy** (`localhost:8090`) - Routes traffic and serves both app and Adminer

**Cloud Deployment Ready:**
- **DigitalOcean App Platform** - Managed deployment in Singapore
- **GitHub Integration** - Automatic deployments on push
- **Terraform Configuration** - Infrastructure as code
- **Repository Optimization** - 6x faster git uploads

---

## 🚀 Quick Deploy to Production (Singapore)

### **Option A: DigitalOcean App Platform (Recommended)**
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your DO token and GitHub repo
terraform init
terraform apply
```

**Cost**: ~$27/month | **Deploy Time**: 5 minutes | **Zero server management**

See [terraform/DEPLOY.md](terraform/DEPLOY.md) for detailed deployment guide.

---

## 🔧 Repository Optimization

**Before committing large changes, run:**
```bash
./scripts/optimize-repo.sh
```

**Performance improvements:**
- ✅ **6x faster git uploads** (16 KiB/s → 92 KiB/s)
- ✅ **Comprehensive .gitignore** for data files
- ✅ **Size monitoring** script
- ✅ **Best practices** enforcement

---

## 🖥️ Local Development (Run on Your Own Computer)

Follow these steps exactly to get the app running locally:

### 1. Install Prerequisites
- **Install Docker Desktop:** [Download here](https://www.docker.com/products/docker-desktop)
  - Make sure Docker Desktop is running before proceeding
- **Install Git:** [Download here](https://git-scm.com/downloads)

### 2. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/anthonyscolaro/n8n-fireflies.git
cd n8n-fireflies

# Check for large files before making changes
./scripts/optimize-repo.sh
```

### 3. Start All Services
```bash
# Start all containers (database, app, nginx, adminer)
docker-compose up -d

# Check that everything is running
docker-compose ps
```

### 4. Access the Applications
- **🌐 Main App (via nginx)**: http://localhost:8090
- **🗄️ Database Admin (Adminer)**: http://localhost:8090/adminer
- **📊 Direct Streamlit**: http://localhost:8501 
- **⚕️ Health Check**: http://localhost:8090/health

---

## 📊 Service Management

### **View Logs**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f nginx
```

### **Restart Services**
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart web
```

### **Stop Everything**
```bash
docker-compose down
```

### **Clean Rebuild** 
```bash
# Stop and remove everything
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

## 🗄️ Database Management

### **Using Adminer (Web Interface)**
1. Go to: http://localhost:8090/adminer
2. **Server**: `db`
3. **Username**: `firefliesuser` 
4. **Password**: `firefliespass`
5. **Database**: `firefliesdb`

### **Direct PostgreSQL Access**
```bash
# Connect to database directly
docker exec -it fireflies-postgres psql -U firefliesuser -d firefliesdb

# Backup database
docker exec fireflies-postgres pg_dump -U firefliesuser firefliesdb > backup.sql

# Restore database  
docker exec -i fireflies-postgres psql -U firefliesuser firefliesdb < backup.sql
```

---

## 🧪 Development Workflow

### **Making Changes**
```bash
# 1. Check repository size/optimization
./scripts/optimize-repo.sh

# 2. Make your changes to the code

# 3. Rebuild and test locally
docker-compose down
docker-compose build
docker-compose up -d

# 4. Test the application
curl http://localhost:8090/health
```

### **Deploying Changes**
```bash
# 1. Commit optimized changes
git add .
git commit -m "Your change description"

# 2. Push to GitHub (triggers auto-deploy if using App Platform)
git push github main

# 3. Or deploy manually with Terraform
cd terraform
terraform apply
```

---

## 🚨 Troubleshooting

### **Docker Issues**
```bash
# Check container status
docker-compose ps

# View specific container logs
docker-compose logs nginx
docker-compose logs web
docker-compose logs db

# Reset everything
docker-compose down -v
docker system prune -f
docker-compose up -d
```

### **Database Connection Issues**
```bash
# Check database health
docker-compose exec db pg_isready -U firefliesuser

# Reset database
docker-compose down -v
docker-compose up -d
```

### **Nginx/Proxy Issues**
```bash
# Check nginx configuration
docker-compose exec nginx nginx -t

# Reload nginx config
docker-compose restart nginx
```

### **Performance Issues**
```bash
# Check resource usage
docker stats

# Optimize repository
./scripts/optimize-repo.sh

# Check for large files
find . -type f -size +1M | head -10
```

---

## 📁 Project Structure

```
fireflies-app/
├── 🐳 docker-compose.yml        # Multi-service Docker setup
├── 🐳 Dockerfile               # Streamlit app container
├── ⚙️ nginx.conf               # Reverse proxy configuration
├── 🗄️ init.sql                # Database initialization
├── 📊 fireflies_streamlit_app.py # Main Streamlit application
├── 📋 requirements.txt         # Python dependencies
├── 🚀 terraform/              # Cloud deployment configuration
│   ├── main.tf                # DigitalOcean infrastructure
│   ├── variables.tf           # Configuration variables
│   ├── outputs.tf             # Deployment outputs
│   └── DEPLOY.md              # Deployment guide
├── 🔧 scripts/
│   ├── optimize-repo.sh       # Repository optimization tool
│   └── fireflies/            # Data processing scripts
└── 📚 README.md              # This file
```

---

## 🌐 Production URLs (After Deployment)

After deploying to DigitalOcean App Platform:
- **🌐 Main App**: `https://your-app-xyz.ondigitalocean.app`
- **🗄️ Database Admin**: `https://your-app-xyz.ondigitalocean.app/adminer`
- **⚕️ Health Check**: `https://your-app-xyz.ondigitalocean.app/health`

---

## 🔐 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | Database hostname | `db` |
| `DB_PORT` | Database port | `5432` |
| `DB_USER` | Database username | `firefliesuser` |
| `DB_PASSWORD` | Database password | `firefliespass` |
| `DB_NAME` | Database name | `firefliesdb` |

---

## 📈 Monitoring & Maintenance

### **Health Monitoring**
- **App Health**: http://localhost:8090/health
- **Database Health**: `docker-compose exec db pg_isready -U firefliesuser`
- **Container Status**: `docker-compose ps`

### **Performance Monitoring**
- **Resource Usage**: `docker stats`
- **Repository Size**: `./scripts/optimize-repo.sh`
- **Upload Speed**: Monitor git push times

### **Backup Strategy**
```bash
# Database backup
docker exec fireflies-postgres pg_dump -U firefliesuser firefliesdb > "backup-$(date +%Y%m%d).sql"

# Code backup (already in GitHub)
git push github main
```

---

## 🤝 Contributing

1. **Check optimization** before committing:
   ```bash
   ./scripts/optimize-repo.sh
   ```

2. **Follow naming conventions**:
   - Data files → `scripts/fireflies/data/` (gitignored)
   - Large files → External storage links
   - Keep repository < 50MB

3. **Test locally** before deploying:
   ```bash
   docker-compose down && docker-compose up -d
   curl http://localhost:8090/health
   ```

---

## 📋 System Requirements

### **Local Development**
- **OS**: macOS, Windows 10+, or Linux
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 10GB free space
- **Docker**: Docker Desktop 4.0+

### **Production (DigitalOcean App Platform)**
- **App Instance**: 512MB RAM ($7/month)
- **Adminer Instance**: 256MB RAM ($5/month)  
- **Database**: 1GB RAM PostgreSQL ($15/month)
- **Total**: ~$27/month

---

## 📞 Support

- **Documentation**: [terraform/DEPLOY.md](terraform/DEPLOY.md)
- **Repository Optimization**: `./scripts/optimize-repo.sh`
- **Health Checks**: http://localhost:8090/health
- **Container Logs**: `docker-compose logs -f`

---

*Last Updated: May 2024 | Repository optimized for 6x faster deployments* 