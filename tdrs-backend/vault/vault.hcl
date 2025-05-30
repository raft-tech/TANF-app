# Enable Vault's web UI
ui = true
log_level = "Info"

# Use file-based storage in /tmp (for development)
storage "file" {
  path = "/tmp/vault-data"
}

# Configure Vault to listen on all interfaces (development only)
listener "tcp" {
  address = "0.0.0.0:8200"
  tls_disable = true  # WARNING: Only for development
}

# API and cluster configuration
api_addr = "http://0.0.0.0:8200"
cluster_addr = "http://0.0.0.0:8201"
disable_mlock = true  # Disable memory locking for containerized environments