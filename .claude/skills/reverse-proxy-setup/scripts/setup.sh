#!/bin/bash
# Automated Nginx Reverse Proxy Setup with SSL
# Usage: ./setup.sh <domain> <port1> <port2> <port3>
# Example: ./setup.sh example.com 2024 8123 3000

set -e

DOMAIN="$1"
PORT1="$2"
PORT2="$3"
PORT3="$4"

# Validate inputs
if [ -z "$DOMAIN" ] || [ -z "$PORT1" ]; then
    echo "Usage: $0 <domain> <port1> [port2] [port3]"
    echo "Example: $0 example.com 2024 8123 3000"
    exit 1
fi

echo "=========================================="
echo "Nginx Reverse Proxy Setup for $DOMAIN"
echo "=========================================="
echo ""

# Step 1: Update system and install Nginx
echo "[1/6] Installing Nginx and certbot..."
apt-get update -qq
apt-get install -y nginx certbot python3-certbot-nginx

# Step 2: Copy and customize Nginx configuration
echo "[2/6] Configuring Nginx..."
CONFIG_FILE="/etc/nginx/sites-available/$DOMAIN"
cp nginx-template.conf "$CONFIG_FILE"

# Replace placeholders
sed -i "s/{DOMAIN}/$DOMAIN/g" "$CONFIG_FILE"
sed -i "s/{PORT1}/${PORT1}/g" "$CONFIG_FILE"
if [ -n "$PORT2" ]; then
    sed -i "s/{PORT2}/${PORT2}/g" "$CONFIG_FILE"
fi
if [ -n "$PORT3" ]; then
    sed -i "s/{PORT3}/${PORT3}/g" "$CONFIG_FILE"
fi

# Remove unused service blocks if ports not provided
if [ -z "$PORT2" ]; then
    sed -i '/# Service 2:/,/}/d' "$CONFIG_FILE"
fi
if [ -z "$PORT3" ]; then
    sed -i '/# Service 3:/,/}/d' "$CONFIG_FILE"
fi

# Step 3: Create symbolic link to enable site
echo "[3/6] Enabling site configuration..."
ln -sf "$CONFIG_FILE" "/etc/nginx/sites-enabled/$DOMAIN"
rm -f /etc/nginx/sites-enabled/default

# Step 4: Create HTTP-only version for initial SSL setup
echo "[4/6] Creating HTTP-only configuration for SSL setup..."
cat > "$CONFIG_FILE.http" << 'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name DOMAIN_PLACEHOLDER www.DOMAIN_PLACEHOLDER;
    client_max_body_size 100M;
    location / { proxy_pass http://127.0.0.1:PORT_PLACEHOLDER; }
}
EOF
sed -i "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" "$CONFIG_FILE.http"
sed -i "s/PORT_PLACEHOLDER/$PORT1/g" "$CONFIG_FILE.http"
cp "$CONFIG_FILE.http" "$CONFIG_FILE"

# Step 5: Test Nginx configuration
echo "[5/6] Testing Nginx configuration..."
nginx -t

# Step 6: Start Nginx
systemctl start nginx
systemctl enable nginx

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Nginx is running on HTTP (port 80)."
echo ""
echo "Next steps:"
echo "1. Ensure DNS A records exist:"
echo "   - $DOMAIN → $(curl -s ifconfig.me)"
echo "   - www.$DOMAIN → $(curl -s ifconfig.me)"
echo ""
echo "2. Obtain SSL certificate:"
echo "   sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
echo ""
echo "3. Your services will be accessible at:"
echo "   - https://$DOMAIN/"
echo "   - https://www.$DOMAIN/"
