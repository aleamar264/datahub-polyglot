

resource "helm_release" "postgresql" {
  name = "postgresql"

  repository       = "oci://registry-1.docker.io/bitnamicharts"
  chart            = "postgresql"
  namespace        = "postgresql"
  version          = "18.0.7"
  create_namespace = true
  values           = [file("${path.module}/values.yaml")]
}
