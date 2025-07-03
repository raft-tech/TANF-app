Vault Agent Configuration
vault {
  address = "http://vault:8200"
}

# Authentication using token file
auto_auth {
  method "token_file" {
    config = {
      token_file_path = "/tmp/vault-token"
    }
  }
  
  sink "file" {
    config = {
      path = "/tmp/vault-token-sink"
    }
  }
}

# Template configuration
template {
  source      = "/vault_agent/templates/database.json.tpl"
  destination = "/vault/secrets/database.json"
  perms       = 0644
}

listener "tcp" {
  address = "127.0.0.1:8200"
  tls_disable = true
}