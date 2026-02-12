terraform {
    required_providers {
        kafka = {
            source = "github.com/Mongey/kafka"
            version = "0.13.1"
        }
    }
}

provider "kafka" {
    bootstrap_servers = var.bootstrap_servers
    tls_enabled = false
}

