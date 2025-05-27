output "droplet_ip" {
  description = "The public IP address of the droplet"
  value       = digitalocean_droplet.fireflies.ipv4_address
}

output "droplet_private_ip" {
  description = "The private IP address of the droplet"
  value       = digitalocean_droplet.fireflies.ipv4_address_private
}

output "ssh_connection" {
  description = "SSH connection string"
  value       = "ssh root@${digitalocean_droplet.fireflies.ipv4_address}"
}

output "app_urls" {
  description = "Application access URLs"
  value = {
    main_app     = "http://${digitalocean_droplet.fireflies.ipv4_address}:8090"
    adminer      = "http://${digitalocean_droplet.fireflies.ipv4_address}:8090/adminer"
    health_check = "http://${digitalocean_droplet.fireflies.ipv4_address}:8090/health"
    streamlit    = "http://${digitalocean_droplet.fireflies.ipv4_address}:8501"
  }
}

output "domain_urls" {
  description = "Domain-based URLs (if domain configured)"
  value = var.domain_name != "" ? {
    main_app     = "http://${var.domain_name}:8090"
    staging      = "http://staging.${var.domain_name}:8090"
    adminer      = "http://${var.domain_name}:8090/adminer"
    health_check = "http://${var.domain_name}:8090/health"
  } : null
}

output "app_url" {
  description = "The main application URL"
  value       = "https://${digitalocean_app.fireflies.default_ingress}"
}

output "adminer_url" {
  description = "Database management interface URL"
  value       = "https://${digitalocean_app.fireflies.default_ingress}/adminer"
}

output "custom_domain_url" {
  description = "Custom domain URL (if configured)"
  value       = var.domain_name != "" ? "https://${var.domain_name}" : "Custom domain not configured"
}

output "database_info" {
  description = "Managed database connection information"
  value = {
    cluster_name = digitalocean_database_cluster.fireflies_db.name
    host         = digitalocean_database_cluster.fireflies_db.host
    private_host = digitalocean_database_cluster.fireflies_db.private_host
    port         = digitalocean_database_cluster.fireflies_db.port
    database     = digitalocean_database_db.fireflies_main.name
    username     = digitalocean_database_user.fireflies_user.name
    ssl_mode     = "require"
  }
  sensitive = false
}

output "database_connection_string" {
  description = "Database connection string for external tools"
  value       = digitalocean_database_cluster.fireflies_db.uri
  sensitive   = true
}

output "app_info" {
  description = "App Platform deployment information"
  value = {
    app_name    = digitalocean_app.fireflies.spec[0].name
    app_id      = digitalocean_app.fireflies.id
    region      = var.region
    environment = var.environment
    github_repo = var.github_repo
    github_branch = var.github_branch
  }
}

output "cost_estimate" {
  description = "Monthly cost estimate (USD)"
  value = {
    app_platform_basic_xs = "$7/month (main app)"
    app_platform_basic_xxs = "$5/month (adminer)"
    managed_database = "$15/month (1GB)"
    total_estimated = "$27/month"
    note = "Prices are estimates and may vary"
  }
}

output "volume_info" {
  description = "Volume information"
  value = {
    volume_id   = digitalocean_volume.fireflies_data.id
    volume_name = digitalocean_volume.fireflies_data.name
    size_gb     = digitalocean_volume.fireflies_data.size
  }
} 