
module "metallb" {
  source = "./metallb_tf"

}

module "prom" {
  source = "./prom"

}


module "tracing" {
  source = "./tracing"

}

module "metrics" {
  source = "./metrics"

}


module "traefik" {
  source     = "./traefik_tf"
  depends_on = [module.metallb, module.prom, module.tracing]

}

module "postgresql" {
  source = "./postgresql"

}

module "kafka" {
  source = "./strimzi"

}
