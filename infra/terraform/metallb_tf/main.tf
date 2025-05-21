resource "helm_release" "metallb" {

  name             = "metallb"
  repository       = "https://metallb.github.io/metallb"
  chart            = "metallb"
  namespace        = "metallb"
  create_namespace = true
  version          = "0.14.9"
}

