resource "helm_release" "prom" {
  name             = "kube-prometheus-stackr"
  version          = "70.6.0"
  repository       = "https://prometheus-community.github.io/helm-charts"
  chart            = "kube-prometheus-stack"
  namespace        = "monitoring"
  create_namespace = true
  values           = [file("${path.module}/values.yaml")]
}
