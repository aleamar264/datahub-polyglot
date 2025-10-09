resource "helm_release" "mongodb" {
  name = "mongodb"

  repository       = "oci://registry-1.docker.io/bitnamicharts"
  chart            = "mongodb"
  namespace        = "mongodb"
  version          = "18.0.5"
  create_namespace = true
  values           = [file("${path.module}/values.yaml")]
}
