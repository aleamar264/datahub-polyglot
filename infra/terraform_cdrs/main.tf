resource "kubernetes_manifest" "metallb_ip_pool" {
  manifest = {
    apiVersion = "metallb.io/v1beta1"
    kind       = "IPAddressPool"
    metadata = {
      namespace = "metallb"
      name      = "my-pool"
    }
    spec = {
      addresses = [
        "192.168.1.240-192.168.1.250",
      ]
    }
  }
}

resource "kubernetes_manifest" "metallb_l2_advert" {
  manifest = {
    apiVersion = "metallb.io/v1beta1"
    kind       = "L2Advertisement"
    metadata = {
      namespace = "metallb"
      name      = "l2-adv"
    }
    spec = {
      ipAddressPools = ["my-pool"]
    }
  }

}
