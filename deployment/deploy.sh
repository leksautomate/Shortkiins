#!/bin/bash
# Deployment script for AI Video Generator on Ubuntu VPS

set -e  # Exit on error

echo "🚀 Deploying AI Video Generator..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/var/www/Shortkiins"
VENV_DIR="$APP_DIR/venv"
REPO_URL="https://github.com/your-username/Shortkiins.git"  # Update this

echo -e "${BLUE}📦 Step 1: Installing system dependencies...${NC}"
sudo apt-get update
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    ffmpeg \
    git

echo -e "${BLUE}📥 Step 2: Cloning repository...${NC}"
if [ ! -d "$APP_DIR" ]; then
    sudo mkdir -p /var/www
    sudo git clone $REPO_URL $APP_DIR
else
    cd $APP_DIR
    sudo git pull
fi

echo -e "${BLUE}🐍 Step 3: Setting up Python virtual environment...${NC}"
cd $APP_DIR
if [ ! -d "$VENV_DIR" ]; then
    sudo python3 -m venv $VENV_DIR
fi

sudo $VENV_DIR/bin/pip install --upgrade pip
sudo $VENV_DIR/bin/pip install -r requirements.txt
sudo $VENV_DIR/bin/pip install uvicorn fastapi python-multipart

echo -e "${BLUE}⚙️ Step 4: Setting up environment variables...${NC}"
if [ ! -f "$APP_DIR/.env" ]; then
    sudo cp $APP_DIR/.env.example $APP_DIR/.env
    echo -e "${GREEN}✅ Created .env file. Please edit it with your API keys!${NC}"
fi

echo -e "${BLUE}📁 Step 5: Creating output directories...${NC}"
sudo mkdir -p $APP_DIR/output
sudo mkdir -p $APP_DIR/temp
sudo mkdir -p $APP_DIR/static

echo -e "${BLUE}🔐 Step 6: Setting permissions...${NC}"
sudo chown -R www-data:www-data $APP_DIR
sudo chmod -R 755 $APP_DIR

echo -e "${BLUE}🔧 Step 7: Configuring systemd service...${NC}"
sudo cp $APP_DIR/deployment/video-generator.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable video-generator
sudo systemctl restart video-generator

echo -e "${BLUE}🌐 Step 8: Configuring nginx...${NC}"
sudo cp $APP_DIR/deployment/nginx.conf /etc/nginx/sites-available/video-generator
sudo ln -sf /etc/nginx/sites-available/video-generator /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "${BLUE}Service status:${NC}"
sudo systemctl status video-generator --no-pager

echo -e "\n${GREEN}🎉 Your app is now running!${NC}"
echo -e "Access it at: http://your-server-ip"
echo -e "\nTo view logs: sudo journalctl -u video-generator -f"
echo -e "To restart: sudo systemctl restart video-generator"
