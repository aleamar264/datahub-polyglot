resource "helm_release" "redis" {
  name             = "redis"
  version          = "21.2.11"
  repository       = "oci://registry-1.docker.io/bitnamicharts"
  chart            = "redis"
  namespace        = "redis"
  create_namespace = true
  values           = [file("${path.module}/values.yaml")]
}
