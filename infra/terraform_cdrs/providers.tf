terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.0.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = ">= 2.0.0"
    }
    time = {
      source  = "hashicorp/time"
      version = ">= 0.7.0"
    }
  }
}

# Configure the Kubernetes provider to use your local kubeconfig
provider "kubernetes" {
  config_path    = "~/.kube/config"
  config_context = "kind-desktop" # optional, defaults to current-context
}

# Configure the Helm provider to talk to the same cluster
provider "helm" {
  kubernetes = {
    config_path    = "~/.kube/config"
    config_context = "kind-desktop" # optional
  }
}
