resource "helm_release" "tracing" {
  name       = "jaeger"
  namespace  = "monitoring"
  chart      = "jaeger"
  repository = "oci://registry-1.docker.io/bitnamicharts"
  version    = "6.0.5" # Replace with the latest stable version

  create_namespace = true
  values           = [file("${path.module}/values.yaml")]
  timeout          = 600

}
