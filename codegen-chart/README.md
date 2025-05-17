# CodeGen Helm Chart

This Helm chart deploys the S4E Internship Code Generator application and its dependencies to a Kubernetes cluster.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- A Kubernetes cluster with access to Docker images

## Getting Started

### Install the Chart

To install the chart with the release name `my-codegen`:

```bash
helm install my-codegen ./codegen-chart
```

The command deploys the application on the Kubernetes cluster with default configuration. The [Parameters](#parameters) section lists the parameters that can be configured during installation.

### Uninstall the Chart

To uninstall/delete the `my-codegen` deployment:

```bash
helm uninstall my-codegen
```

## Parameters

### Global Parameters

| Name                   | Description                                     | Value     |
|------------------------|-------------------------------------------------|-----------|
| `nameOverride`         | Override the name of the chart                  | `""`      |
| `fullnameOverride`     | Override the full name of the chart             | `""`      |

### Namespace Configuration

| Name                   | Description                                     | Value     |
|------------------------|-------------------------------------------------|-----------|
| `namespace.create`     | Create the namespace                            | `true`    |
| `namespace.name`       | Name of the namespace                           | `codegen` |

### Code Generator Application Parameters

| Name                            | Description                                             | Value                           |
|---------------------------------|---------------------------------------------------------|---------------------------------|
| `app.name`                      | Name of the application                                 | `code-generator`                |
| `app.image.repository`          | Code generator image repository                         | `code-generator`                |
| `app.image.tag`                 | Code generator image tag                                | `latest`                        |
| `app.image.pullPolicy`          | Code generator image pull policy                        | `Never`                         |
| `app.replicas`                  | Number of code generator replicas                       | `2`                             |
| `app.service.type`              | Kubernetes Service type                                 | `LoadBalancer`                  |
| `app.service.port`              | Service port                                            | `80`                            |
| `app.service.targetPort`        | Port exposed by the container                           | `8080`                          |
| `app.resources.requests.memory` | Requested memory                                        | `256Mi`                         |
| `app.resources.requests.cpu`    | Requested CPU                                           | `200m`                          |
| `app.resources.limits.memory`   | Memory limit                                            | `512Mi`                         |
| `app.resources.limits.cpu`      | CPU limit                                               | `500m`                          |
| `app.env.OLLAMA_BASE_URL`       | URL to the Ollama service                               | `http://ollama-service:11434`   |
| `app.env.LLM_MODEL`             | LLM model to use                                        | `llama3.2:latest`               |
| `app.env.FLASK_ENV`             | Flask environment                                       | `production`                    |

### Ollama Parameters

| Name                              | Description                                           | Value                           |
|-----------------------------------|-------------------------------------------------------|----------------------------------|
| `ollama.name`                     | Name of the Ollama service                            | `ollama`                         |
| `ollama.image.repository`         | Ollama image repository                               | `ollama/ollama`                  |
| `ollama.image.tag`                | Ollama image tag                                      | `latest`                         |
| `ollama.image.pullPolicy`         | Ollama image pull policy                              | `IfNotPresent`                   |
| `ollama.replicas`                 | Number of Ollama replicas                             | `1`                              |
| `ollama.service.type`             | Kubernetes Service type                               | `ClusterIP`                      |
| `ollama.service.port`             | Service port                                          | `11434`                          |
| `ollama.service.targetPort`       | Port exposed by the container                         | `11434`                          |
| `ollama.resources.requests.memory`| Requested memory                                      | `2Gi`                            |
| `ollama.resources.requests.cpu`   | Requested CPU                                         | `500m`                           |
| `ollama.resources.limits.memory`  | Memory limit                                          | `4Gi`                            |
| `ollama.resources.limits.cpu`     | CPU limit                                             | `1000m`                          |
| `ollama.storage.size`             | Size of persistent storage                            | `10Gi`                           | 