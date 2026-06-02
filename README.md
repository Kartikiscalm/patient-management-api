# 🏥 FastAPI Patient Management API

A lightweight **FastAPI** project for managing patient records using a local `patients.json` file. The app is containerized with Docker and can be deployed on a local Kubernetes cluster using **Kind**.

## ✨ What This Project Does

- Stores and manages patient data
- Calculates BMI and health verdict automatically
- Supports create, view, update, delete, and sort operations
- Runs inside Kubernetes with multiple replicas for better availability

## 🚀 Run With Docker

```bash
docker build -t fastapi-app:v1.0 .
docker run -p 8000:8000 fastapi-app:v1.0
```

Open:

```text
http://localhost:8000
```

## ☸️ Deploy With Kubernetes / Kind

```bash
kind create cluster --config kind-config.yaml
kind load docker-image fastapi-app:v1.0
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f pdb.yaml
```

Access the API using port forwarding:

```bash
kubectl port-forward service/fastapi-service 8000:80
```

Then open:

```text
http://localhost:8000
```

## 🔗 Useful Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | API welcome message |
| `GET` | `/about` | About the API |
| `GET` | `/view` | View all patients |
| `GET` | `/patient/{patient_id}` | View one patient |
| `GET` | `/sort?sort_by=bmi&order=asc` | Sort patients |
| `POST` | `/create` | Create a patient |
| `PUT` | `/edit/{patient_id}` | Update a patient |
| `DELETE` | `/delete/{patient_id}` | Delete a patient |

## 📈 Horizontal Scaling

The deployment currently runs multiple pods using:

```yaml
replicas: 3
```

To improve performance and handle more traffic, increase the number of pods:

```bash
kubectl scale deployment fastapi-app --replicas=5
```

Check running pods:

```bash
kubectl get pods
```

More pods help distribute requests across replicas, improving availability and response capacity.

