
resource "helm_release" "strimzi-kafka-operator" {
  name = "strimzi-kafka-operator"

  repository       = "oci://quay.io/strimzi-helm"
  chart            = "strimzi-kafka-operator"
  namespace        = "kafka"
  version          = "0.48.0"
  create_namespace = true
  values           = [file("${path.module}/values.yaml")]
}
