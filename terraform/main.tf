# Configure the DigitalOcean Provider
terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

# Configure the DigitalOcean Provider
provider "digitalocean" {
  token = var.do_token
}

# Create a managed PostgreSQL database
resource "digitalocean_database_cluster" "fireflies_db" {
  name       = "fireflies-postgres"
  engine     = "pg"
  version    = "15"
  size       = var.db_size
  region     = var.region
  node_count = 1

  tags = ["fireflies", "production"]
}

# Create the main database
resource "digitalocean_database_db" "fireflies_main" {
  cluster_id = digitalocean_database_cluster.fireflies_db.id
  name       = "firefliesdb"
}

# Create database user
resource "digitalocean_database_user" "fireflies_user" {
  cluster_id = digitalocean_database_cluster.fireflies_db.id
  name       = "firefliesuser"
}

# Create App Platform application
resource "digitalocean_app" "fireflies" {
  spec {
    name   = "fireflies-app"
    region = var.region

    # Main Streamlit service
    service {
      name               = "web"
      environment_slug   = "docker"
      instance_count     = 1
      instance_size_slug = var.app_size

      github {
        repo           = var.github_repo
        branch         = var.github_branch
        deploy_on_push = true
      }

      dockerfile_path = "Dockerfile"

      http_port = 8501

      health_check {
        http_path = "/"
      }

      env {
        key   = "DB_HOST"
        value = digitalocean_database_cluster.fireflies_db.private_host
      }

      env {
        key   = "DB_PORT"
        value = digitalocean_database_cluster.fireflies_db.port
      }

      env {
        key   = "DB_NAME"
        value = digitalocean_database_db.fireflies_main.name
      }

      env {
        key   = "DB_USER"
        value = digitalocean_database_user.fireflies_user.name
      }

      env {
        key   = "DB_PASSWORD"
        value = digitalocean_database_user.fireflies_user.password
        type  = "SECRET"
      }

      env {
        key   = "DATABASE_URL"
        value = digitalocean_database_cluster.fireflies_db.private_uri
        type  = "SECRET"
      }

      routes {
        path = "/"
      }
    }

    # Adminer service for database management
    service {
      name               = "adminer"
      environment_slug   = "docker"
      instance_count     = 1
      instance_size_slug = "basic-xxs"

      image {
        registry_type = "DOCKER_HUB"
        repository    = "adminer"
        tag           = "latest"
      }

      http_port = 8080

      env {
        key   = "ADMINER_DEFAULT_SERVER"
        value = digitalocean_database_cluster.fireflies_db.private_host
      }

      env {
        key   = "ADMINER_DESIGN"
        value = "hydra"
      }

      routes {
        path = "/adminer"
      }
    }
  }
}

# Create a project to organize resources
resource "digitalocean_project" "fireflies" {
  name        = "Fireflies App"
  description = "Fireflies transcription management application"
  purpose     = "Web Application"
  environment = title(var.environment)

  resources = [
    digitalocean_database_cluster.fireflies_db.urn,
    digitalocean_app.fireflies.urn
  ]
}

# Optional: Custom domain
resource "digitalocean_domain" "fireflies" {
  count = var.domain_name != "" ? 1 : 0
  name  = var.domain_name
}

resource "digitalocean_record" "fireflies_cname" {
  count  = var.domain_name != "" ? 1 : 0
  domain = digitalocean_domain.fireflies[0].name
  type   = "CNAME"
  name   = "@"
  value  = digitalocean_app.fireflies.default_ingress
}

resource "digitalocean_record" "fireflies_www" {
  count  = var.domain_name != "" ? 1 : 0
  domain = digitalocean_domain.fireflies[0].name
  type   = "CNAME"
  name   = "www"
  value  = digitalocean_app.fireflies.default_ingress
} 