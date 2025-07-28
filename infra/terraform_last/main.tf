module "traefik_module" {
  source = "./traefik_module"
}

module "prom" {
  source = "./tracing"
  depends_on = [ module.traefik_module ]
}