
module "metallb" {
  source = "./metallb_tf"

}

module "prom" {
  source = "./prom"

}

# module "tracing" {
#   source = "./tracing"

# }

module "metrics" {
  source = "./metrics"

}

module "postgresql" {
  source = "./postgresql"

}

module "kafka" {
  source = "./strimzi"
  depends_on = [ module.prom ]

}

module "redis" {
  source = "./redis"
  depends_on = [ module.prom ]
}

module "mongo" {
  source = "./mongodb"
  depends_on = [ module.prom ]
}