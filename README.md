# Kubernetes Data Demo

A GitOps demonstration project showcasing ETL workflows on Kubernetes using ArgoCD.

## Tech Stack

- **K3d** - Lightweight Kubernetes cluster with Docker
- **Helm** - Kubernetes package manager
- **ArgoCD** - GitOps continuous deployment
- **PostgreSQL** - Relational database
- **Python** - ETL processing (pandas, psycopg2)
- **GitHub Actions** - CI/CD pipeline

## Prerequisites

- Docker
- k3d
- kubectl
- helm

## Quick Start

### 1. Create K3d Cluster
```bash
k3d cluster create demo --servers 1 --agents 2
kubectl cluster-info
```

### 2. Install ArgoCD
```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
helm install argo-cd argo/argo-cd -n argocd --create-namespace
```

### 3. Deploy Applications
```bash
kubectl apply -f kubernetes/argocd/prod/
```

### 4. Access PostgreSQL
```bash
# Port forward
kubectl port-forward --namespace etl-app svc/postgresql 5431:5432 &

# Get password and connect
export POSTGRES_PASSWORD=$(kubectl get secret --namespace etl-app postgresql -o jsonpath="{.data.postgres-password}" | base64 -d)
PGPASSWORD="$POSTGRES_PASSWORD" psql --host 127.0.0.1 -U postgres -d postgres -p 5431
```

## Workflow

1. **CI/CD**: GitHub Actions builds and pushes Docker images to Docker Hub
2. **GitOps**: ArgoCD monitors this repository and auto-syncs changes
3. **Scheduling**: CronJob runs ETL pipeline hourly (`0 * * * *`)
4. **Processing**: Python script extracts, transforms, and loads data into PostgreSQL

## Cleanup

```bash
k3d cluster delete demo
```