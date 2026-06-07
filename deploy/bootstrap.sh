#!/usr/bin/env bash
# Bootstrap a fresh VPS for chromatic-matroids.
#
# Run as root (or with sudo) on a fresh Ubuntu/Debian server:
#
#   curl -fsSL https://raw.githubusercontent.com/raulpenaguiao/chromatic-matroids/main/deploy/bootstrap.sh | sudo bash
#
# Or, after cloning the repo:
#
#   sudo bash deploy/bootstrap.sh
#
# After this runs, add the GitHub Actions SSH public key to
# ~/.ssh/authorized_keys for the deploy user, then future deploys
# happen automatically when you push the 'frontend' git tag.
set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
DEPLOY_USER="${DEPLOY_USER:-root}"
APP_DIR="/var/www/chromatic-matroids"
REPO_URL="https://github.com/raulpenaguiao/chromatic-matroids.git"
SERVICE="chromatic-matroids"

# ── Must run as root ──────────────────────────────────────────────────────────
[[ $(id -u) -eq 0 ]] || { echo "Error: run as root or with sudo"; exit 1; }

echo "=== 1/7  System packages ==="
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq python3 python3-venv git nginx

echo "=== 2/7  App directory ==="
mkdir -p "$APP_DIR"
# If the deploy user doesn't exist yet, create it
id "$DEPLOY_USER" &>/dev/null || useradd -m -s /bin/bash "$DEPLOY_USER"
chown "$DEPLOY_USER:$DEPLOY_USER" "$APP_DIR"

echo "=== 3/7  Clone / update repo ==="
if [ -d "$APP_DIR/.git" ]; then
    sudo -u "$DEPLOY_USER" git -C "$APP_DIR" fetch origin
    sudo -u "$DEPLOY_USER" git -C "$APP_DIR" checkout main
    sudo -u "$DEPLOY_USER" git -C "$APP_DIR" pull origin main
else
    sudo -u "$DEPLOY_USER" git clone "$REPO_URL" "$APP_DIR"
fi

echo "=== 4/7  Python environment ==="
[ -d "$APP_DIR/.venv" ] || sudo -u "$DEPLOY_USER" python3 -m venv "$APP_DIR/.venv"
sudo -u "$DEPLOY_USER" "$APP_DIR/.venv/bin/pip" install \
    -e "$APP_DIR/package" flask gunicorn numpy --quiet

echo "=== 5/7  Systemd service ==="
cp "$APP_DIR/chromatic-matroids.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable "$SERVICE"
systemctl restart "$SERVICE"

echo "=== 6/7  Nginx ==="
cp "$APP_DIR/deploy/nginx-chromatic-matroids.conf" /etc/nginx/sites-available/chromatic-matroids
ln -sf /etc/nginx/sites-available/chromatic-matroids /etc/nginx/sites-enabled/chromatic-matroids
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

echo "=== 7/7  Sudoers (passwordless service management for $DEPLOY_USER) ==="
cat > /etc/sudoers.d/chromatic-matroids << EOF
$DEPLOY_USER ALL=(ALL) NOPASSWD: \\
    /bin/systemctl daemon-reload, \\
    /usr/bin/systemctl daemon-reload, \\
    /bin/systemctl enable $SERVICE, \\
    /usr/bin/systemctl enable $SERVICE, \\
    /bin/systemctl restart $SERVICE, \\
    /usr/bin/systemctl restart $SERVICE, \\
    /bin/systemctl reload nginx, \\
    /usr/bin/systemctl reload nginx, \\
    /usr/bin/tee /etc/systemd/system/$SERVICE.service
EOF
chmod 440 /etc/sudoers.d/chromatic-matroids

echo ""
echo "=== Bootstrap complete ==="
IP=$(hostname -I | awk '{print $1}')
echo "  App:  http://$IP/chromatic-matroids/"
echo ""
echo "Next step: add the GitHub Actions SSH public key for automated deploys:"
echo "  echo '<pubkey>' | sudo -u $DEPLOY_USER tee -a /home/$DEPLOY_USER/.ssh/authorized_keys"
