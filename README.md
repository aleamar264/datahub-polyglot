When is installing MetalLB in kubernetes and terraform throw some error, this can help

```shell
 kubectl delete validatingwebhookconfigurations.admissionregistration.k8s.io metallb-webhook-configuration
```

## Kubernetes in Docker (KinD)

When you start the cluster with `N` nodes, and you want to start using kubectl, the first thing that you need to do is export the configuration from KinD to kubectl

```shell
kind export kubeconfig --name desktop
```

After that, export the kubeconfig with `export KUBECONFIG=~/.kube/config`

Now you can use [[Infrastructure/Kubernetes#Commands|Kubernetes Commands]]

## Terraform

In this project we are to deploy all the services using Terraform and Helm.

In this case the Infrastructure folder is:

```shell
.
├── variables.tf
├── postgres.tf
├── traefik_tf
│   ├── traefik.tf
│   └── traefik.yaml
├── metallb_tf
│   └── main.tf
├── prom
│   ├── main.tf
│   └── values.yaml
├── tracing
│   ├── values.yaml
│   └── main.tf
├── providers.tf
├── metrics
│   ├── values.yaml
│   └── main.tf
├── main.tf
└── terraform.tfstate
```

Where we are using:

- Traefik
- MetalLB
- Prometheus Stack with Grafana
- Tracing (Jaeger)
- Kubernetes metrics
- PostgreSQL

### Traefik

Traefik is a reverse proxy write in go. This is able to create replicas of the loadbalancers. In this moment like we are running this locally, we are using MetalLB. In the values.yaml file in the part of services we put some annotations, in the moment that we use a cloud like AWS, Azure or Google we only need to change for the values of the cloud. Also, in every single part that said _localhost_ for the actual domain.

```yaml

---
service:
  type: LoadBalancer
  externalTrafficPolicy: Local
  annotations:
    metallb.universe.tf/address-pool: "my-pool"
    metallb.universe.tf/allow-shared-ip: "traefik-shared"
---
ingressRoute:
  dashboard:
    enabled: true
    # Custom match rule with host domain
    matchRule: "Host(`localhost`) && (PathPrefix(`/api`) || PathPrefix(`/dashboard`))"
    entryPoints: ["web", "test-port"]
    # Add custom middlewares : authentication and redirection
    middlewares:
      - name: traefik-dashboard-auth
```

If you run this the first time, this will throw an error, because _my-pool_ not exist yet until you run the **k8s** file that create this pool.;

### MetalLB

> MetalLB is a load-balancer implementation for bare metal [Kubernetes](https://kubernetes.io/) clusters, using standard routing protocols.
>
> ## Why?
>
> Kubernetes does not offer an implementation of network load balancers ([Services of type LoadBalancer](https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/)) for bare-metal clusters. The implementations of network load balancers that Kubernetes does ship with are all glue code that calls out to various IaaS platforms (GCP, AWS, Azure…). If you’re not running on a supported IaaS platform (GCP, AWS, Azure…), LoadBalancers will remain in the “pending” state indefinitely when created.
>
> Bare-metal cluster operators are left with two lesser tools to bring user traffic into their clusters, “NodePort” and “externalIPs” services. Both of these options have significant downsides for production use, which makes bare-metal clusters second-class citizens in the Kubernetes ecosystem.
>
> MetalLB aims to redress this imbalance by offering a network load balancer implementation that integrates with standard network equipment, so that external services on bare-metal clusters also “just work” as much as possible.
> [MetalLB :: MetalLB, bare metal load-balancer for Kubernetes](https://metallb.io/)

With this, we only need to get the chart of helm and run. The only one thing that we need to do is create a yaml file with the range address and pool for IP.

```yaml
---
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: my-pool
  namespace: metallb
spec:
  addresses:
    - 192.168.10.0/24
    - 192.168.1.240-192.168.1.250
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: example
  namespace: metallb
spec:
  ipAddressPools:
    - my-pool
```

When we apply this file, we can run the traefik terraform file, this time, doesn't fail.

### Prometheus Stack with Grafana

This stack bring together prometheus and grafana in a single package.

The most important thing here is the value.yaml file

```yaml
grafana:
  persistence:
    type: pvc
    enabled: true
    storageClassName: standard
    accessModes:
      - ReadWriteOnce
    size: 1Gi
    finalizers:
      - kubernetes.io/pvc-protection
  grafana.ini:
    server:
      domain: localhost
      root_url: "https://%(domain)s/grafana"
      serve_from_sub_path: true
  sidecar:
    dashboards:
      enabled: true
      label: grafana_dashboard
      labelValue: "1"
prometheus:
  prometheusSpec:
    externalUrl: https://localhost/prometheus
    routePrefix: /prometheus
    additionalScrapeConfigs:
      - job_name: traefik
        metrics_path: "/metrics"
        scrape_interval: 10s
        scrape_timeout: 5s
        scheme: http
        static_configs:
          - targets:
              - "traefik.traefik.svc.cluster.local:9100"
      - job_name: jaeger-collector
        metrics_path: "/metrics"
        scrape_interval: 10s
        scrape_timeout: 5s
        scheme: http
        static_configs:
          - targets:
              - "jaeger-collector.monitoring.svc.cluster.local:14269"
      - job_name: jaeger-query
        metrics_path: "/metrics"
        scrape_interval: 10s
        scrape_timeout: 5s
        scheme: http
        static_configs:
          - targets:
              - "jaeger-query.monitoring.svc.cluster.local:16687"
# prometheus.prometheusSpec.routePrefix
prometheus-node-exporter:
  hostRootFsMount:
    enabled: false
    mountPropagation: HostToContainer
```

This part let to know to grafana that can use some persistence storage to save data. The _storageClassName_ is from the pvc and pv from kubernetes, like this time is from local we use standard, in other case could be _gp2_ or the storage in that moment.

To know which storage class you have, you can use

```shell
$ kubectl get storageclass --all-namespaces
NAME                 PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
hostpath             rancher.io/local-path   Delete          WaitForFirstConsumer   false                  3h40m
standard (default)   rancher.io/local-path   Delete          WaitForFirstConsumer   false                  3h40m
```

```yaml
grafana:
	  persistence:
	    type: pvc
	    enabled: true
	    storageClassName: standard
	    accessModes:
	      - ReadWriteOnce
	    size: 1Gi
	    finalizers:
	      - kubernetes.io/pvc-protection
```

When you change to your own domain, change localhost for the domain name

```yaml
grafana.ini:
  server:
    domain: localhost
    root_url: "https://%(domain)s/grafana"
    serve_from_sub_path: true
```

And the last part, is only for local, comment or delete this when is deployed in cloud.

```yaml
prometheus-node-exporter:
  hostRootFsMount:
    enabled: false
    mountPropagation: HostToContainer
```

### Tracing (Jaeger)

In this part, the only thing that is valuable to tell is change the type of storageClass when is deployed in cloud.

### Metrics

This yaml is for local purpose

```yaml
---
defaultArgs:
  - --cert-dir=/tmp
  - --kubelet-insecure-tls # Bypass self-signed cert verification
  - --kubelet-preferred-address-types=InternalIP,Hostname
  - --kubelet-use-node-status-port # Use node status port for metrics
  - --metric-resolution=15s # Set metrics resolution
  - --secure-port=10250 # Use kubelet secure port
```

For production use this

```yaml
---
defaultArgs:
  - --cert-dir=/tmp
  - --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname
  - --kubelet-use-node-status-port
  - --metric-resolution=15s
```
