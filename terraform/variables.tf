variable "do_token" {
  description = "DigitalOcean API token"
  type        = string
  sensitive   = true
}

variable "region" {
  description = "DigitalOcean region"
  type        = string
  default     = "sgp1"  # Singapore region
}

variable "app_size" {
  description = "App Platform instance size for main application"
  type        = string
  default     = "basic-xs"  # 512MB RAM, $5/month per instance
  validation {
    condition = contains([
      "basic-xxs",  # 256MB RAM, $5/month
      "basic-xs",   # 512MB RAM, $7/month  
      "basic-s",    # 1GB RAM, $12/month
      "basic-m",    # 2GB RAM, $24/month
      "basic-l"     # 4GB RAM, $48/month
    ], var.app_size)
    error_message = "App size must be one of: basic-xxs, basic-xs, basic-s, basic-m, basic-l"
  }
}

variable "db_size" {
  description = "Managed database size"
  type        = string
  default     = "db-s-1vcpu-1gb"  # $15/month
  validation {
    condition = contains([
      "db-s-1vcpu-1gb",   # $15/month
      "db-s-1vcpu-2gb",   # $30/month
      "db-s-1vcpu-3gb",   # $45/month
      "db-s-2vcpu-4gb",   # $90/month
      "db-s-4vcpu-8gb"    # $180/month
    ], var.db_size)
    error_message = "Database size must be one of the supported managed database sizes"
  }
}

variable "github_repo" {
  description = "GitHub repository in format 'owner/repo'"
  type        = string
  default     = "yourusername/n8n-fireflies"
  validation {
    condition     = can(regex("^[^/]+/[^/]+$", var.github_repo))
    error_message = "GitHub repo must be in format 'owner/repository'"
  }
}

variable "github_branch" {
  description = "GitHub branch to deploy from"
  type        = string
  default     = "main"
}

variable "domain_name" {
  description = "Domain name for the application (leave empty to skip DNS)"
  type        = string
  default     = ""
}

variable "environment" {
  description = "Environment name (production, staging, etc.)"
  type        = string
  default     = "production"
} 