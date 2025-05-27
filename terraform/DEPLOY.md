# 🚀 Deploy to DigitalOcean App Platform

Super simple deployment using managed services in **Singapore** region.

## 💰 Cost Estimate
- **App Platform (main app)**: $7/month (512MB RAM)
- **App Platform (Adminer)**: $5/month (256MB RAM)  
- **Managed PostgreSQL**: $15/month (1GB RAM)
- **Total**: ~$27/month

## 🎯 Prerequisites

1. **DigitalOcean Account** with API token
2. **GitHub repository** (this repo) 
3. **Terraform installed** locally

## 📋 Quick Deploy Steps

### 1. Get DigitalOcean API Token
- Go to: https://cloud.digitalocean.com/account/api/tokens
- Generate new token with "Write" scope
- Copy the token (starts with `dop_v1_`)

### 2. Configure Variables
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your actual values
```

### 3. Deploy Infrastructure
```bash
terraform init
terraform plan
terraform apply
```

### 4. Get Your URLs
After deployment, Terraform will output your application URLs:
- **Main App**: `https://your-app-abc123.ondigitalocean.app`
- **Adminer**: `https://your-app-abc123.ondigitalocean.app/adminer`

## 🔧 What Gets Created

### **App Platform Services**
- **Main Streamlit App** - Auto-deployed from GitHub
- **Adminer** - Database management interface

### **Managed Database**
- **PostgreSQL 15** - Fully managed, auto-backups
- **Private networking** - Secure connection to apps
- **SSL encryption** - Built-in security

### **Automatic Features**
- ✅ **Auto-scaling** based on traffic
- ✅ **SSL certificates** (HTTPS)
- ✅ **GitHub deployments** on push
- ✅ **Health monitoring**
- ✅ **Backups** (database)
- ✅ **Load balancing**

## 🌏 Region & Performance
- **Singapore (sgp1)** - Low latency for Asia-Pacific
- **CDN included** - Global content delivery
- **99.99% uptime SLA**

## 🎛️ Management
- **DigitalOcean Console**: Full web interface
- **Terraform**: Infrastructure as code
- **GitHub**: Automatic deployments
- **No server management** needed!

## 🔍 Monitoring URLs
```bash
# Main application
curl https://your-app.ondigitalocean.app/

# Health check  
curl https://your-app.ondigitalocean.app/health

# Database via Adminer
open https://your-app.ondigitalocean.app/adminer
```

## 💡 Benefits vs Manual Droplets
- **No server maintenance**
- **Automatic scaling** 
- **Built-in monitoring**
- **Managed database backups**
- **SSL certificates included**
- **Much simpler to manage** 