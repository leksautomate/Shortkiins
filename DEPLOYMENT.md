

# VPS Deployment Guide - Ubuntu Linux

Complete guide to deploy the AI Video Generator on your Ubuntu VPS.

## 📋 Prerequisites

- Ubuntu 20.04+ VPS
- Root or sudo access
- Domain name (optional, can use IP)
- Minimum 2GB RAM, 2 CPU cores
- 20GB+ storage

## 🚀 Quick Deployment (Automated)

### 1. Clone Repository

```bash
cd /var/www
sudo git clone https://github.com/your-username/Shortkiins.git
cd Shortkiins
```

### 2. Run Deployment Script

```bash
chmod +x deployment/deploy.sh
sudo ./deployment/deploy.sh
```

### 3. Configure API Keys

```bash
sudo nano /var/www/Shortkiins/.env
```

Add your API keys:
```env
GROQ_API_KEY=your_groq_key_here
WAVESPEED_API_KEY=your_wavespeed_key_here
ASYNCFLOW_API_KEY=your_asyncflow_key_here
```

### 4. Restart Service

```bash
sudo systemctl restart video-generator
```

### 5. Access Your App

Visit: `http://your-server-ip`

---

## 🔧 Manual Deployment (Step by Step)

### Step 1: Update System

```bash
sudo apt-get update && sudo apt-get upgrade -y
```

### Step 2: Install Dependencies

```bash
# Python and tools
sudo apt-get install -y python3 python3-pip python3-venv git

# FFmpeg for video processing
sudo apt-get install -y ffmpeg

# Nginx web server
sudo apt-get install -y nginx
```

### Step 3: Clone Repository

```bash
sudo mkdir -p /var/www
cd /var/www
sudo git clone https://github.com/your-username/Shortkiins.git
cd Shortkiins
```

### Step 4: Setup Python Environment

```bash
# Create virtual environment
sudo python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install uvicorn fastapi python-multipart
```

### Step 5: Configure Environment

```bash
# Copy env example
sudo cp .env.example .env

# Edit with your API keys
sudo nano .env
```

Add your API keys:
```env
GROQ_API_KEY=your_key_here
WAVESPEED_API_KEY=your_key_here
ASYNCFLOW_API_KEY=your_key_here
FREEPIK_API_KEY=your_key_here  # Optional
REPLICATE_API_TOKEN=your_key_here  # Optional
```

### Step 6: Create Directories

```bash
sudo mkdir -p output temp static
sudo chown -R www-data:www-data /var/www/Shortkiins
```

### Step 7: Setup Systemd Service

```bash
# Copy service file
sudo cp deployment/video-generator.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable video-generator

# Start service
sudo systemctl start video-generator

# Check status
sudo systemctl status video-generator
```

### Step 8: Configure Nginx

```bash
# Copy nginx config
sudo cp deployment/nginx.conf /etc/nginx/sites-available/video-generator

# Enable site
sudo ln -s /etc/nginx/sites-available/video-generator /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### Step 9: Configure Firewall

```bash
# Allow HTTP
sudo ufw allow 80

# Allow HTTPS (for later)
sudo ufw allow 443

# Allow SSH (if not already allowed)
sudo ufw allow 22

# Enable firewall
sudo ufw enable
```

---

## 🔐 SSL Certificate (HTTPS)

### Using Let's Encrypt (Free)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal is set up automatically
# Test renewal:
sudo certbot renew --dry-run
```

After getting SSL, uncomment the HTTPS section in nginx config.

---

## 📊 Monitoring & Logs

### View Application Logs

```bash
# Follow logs in real-time
sudo journalctl -u video-generator -f

# View last 100 lines
sudo journalctl -u video-generator -n 100

# View logs from today
sudo journalctl -u video-generator --since today
```

### View Nginx Logs

```bash
# Access logs
sudo tail -f /var/log/nginx/video-generator-access.log

# Error logs
sudo tail -f /var/log/nginx/video-generator-error.log
```

### Check Service Status

```bash
# Service status
sudo systemctl status video-generator

# Nginx status
sudo systemctl status nginx

# Disk usage
df -h

# Memory usage
free -h
```

---

## 🔄 Updates & Maintenance

### Update Application

```bash
cd /var/www/Shortkiins
sudo git pull
sudo systemctl restart video-generator
```

### Restart Service

```bash
sudo systemctl restart video-generator
```

### Reload Nginx

```bash
sudo systemctl reload nginx
```

### Clear Output Directory

```bash
# Be careful! This deletes all generated videos
sudo rm -rf /var/www/Shortkiins/output/*
sudo rm -rf /var/www/Shortkiins/temp/*
```

---

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u video-generator -n 50

# Check Python environment
/var/www/Shortkiins/venv/bin/python --version

# Test manually
cd /var/www/Shortkiins
source venv/bin/activate
python api.py
```

### Nginx Errors

```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log
```

### Permission Issues

```bash
# Fix ownership
sudo chown -R www-data:www-data /var/www/Shortkiins

# Fix permissions
sudo chmod -R 755 /var/www/Shortkiins
```

### API Key Errors

```bash
# Check .env file
sudo cat /var/www/Shortkiins/.env

# Make sure it's readable
sudo chmod 644 /var/www/Shortkiins/.env
```

### FFmpeg Not Found

```bash
# Install FFmpeg
sudo apt-get install -y ffmpeg

# Verify
which ffmpeg
ffmpeg -version
```

---

## ⚡ Performance Optimization

### Use Redis for Job Storage (Production)

```bash
# Install Redis
sudo apt-get install -y redis-server

# Enable Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

Then update `api.py` to use Redis instead of in-memory storage.

### Add More Workers

Edit `/etc/systemd/system/video-generator.service`:

```ini
ExecStart=/var/www/Shortkiins/venv/bin/uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

Then restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart video-generator
```

### Enable Gzip Compression

Add to nginx config:
```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

---

## 🔒 Security Best Practices

1. **Use HTTPS** (Let's Encrypt SSL)
2. **Configure Firewall** (ufw)
3. **Keep system updated** (`sudo apt-get update && sudo apt-get upgrade`)
4. **Use strong API keys**
5. **Limit CORS origins** in `api.py`
6. **Regular backups**
7. **Monitor logs** for suspicious activity

---

## 📦 Backup & Restore

### Backup

```bash
# Backup .env file
sudo cp /var/www/Shortkiins/.env ~/backup_env

# Backup database (if using)
# Backup generated videos
sudo tar -czf videos_backup.tar.gz /var/www/Shortkiins/output/
```

### Restore

```bash
# Restore .env
sudo cp ~/backup_env /var/www/Shortkiins/.env

# Restore videos
sudo tar -xzf videos_backup.tar.gz -C /
```

---

## 📞 Support

- Check logs: `sudo journalctl -u video-generator -f`
- Test API: Visit `http://your-ip/api/health`
- Nginx status: `sudo systemctl status nginx`

---

## 🎉 Success!

Your AI Video Generator is now running on your VPS!

**Access Points:**
- Web UI: `http://your-server-ip`
- API Docs: `http://your-server-ip/docs` (FastAPI auto-docs)
- Health Check: `http://your-server-ip/api/health`

**Next Steps:**
1. Set up SSL certificate
2. Configure domain name
3. Add monitoring (optional)
4. Set up automatic backups
