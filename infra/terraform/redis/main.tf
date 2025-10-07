resource "helm_release" "redis" {
  name             = "redis"
  version          = "22.0.0"
  repository       = "oci://registry-1.docker.io/bitnamicharts"
  chart            = "redis"
  namespace        = "redis"
  create_namespace = true
  values           = [file("${path.module}/values.yaml")]
}
