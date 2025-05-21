resource "helm_release" "traefik" {


  name             = "traefik"
  repository       = "https://traefik.github.io/charts"
  chart            = "traefik"
  namespace        = "traefik"
  create_namespace = true
  version          = "35.0.0"

  values = ["${file("${path.module}/traefik.yaml")}"]

}
