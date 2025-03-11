#!/bin/bash

# Variables
RESOURCE_GROUP="dcatryRG"
CONTAINER_NAME="fastapi-app"
ACR_NAME="dcatryregistry"
ACR_IMAGE="fastapi_app"
ACR_URL="$ACR_NAME.azurecr.io"
CPU="1"
MEMORY="4"
PORT="8001"
IP_ADDRESS="Public"
DNS_LABEL="API-LoanRequest"
OS_TYPE="Linux"

# Vérification et chargement des variables d'environnement
if [ -f .env ]; then
    echo "✅ .env file found. Loading environment variables..."
    set -o allexport
    source .env
    set +o allexport
else
    echo "❌ .env file not found!"
    exit 1
fi

# Récupération des identifiants ACR
ACR_USERNAME=$(az acr credential show --name "$ACR_NAME" --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --name "$ACR_NAME" --query "passwords[0].value" -o tsv)

# Suppression du conteneur existant (si présent)
echo "🗑️  Deleting existing container (if exists)..."
az container delete --name "$CONTAINER_NAME" --resource-group "$RESOURCE_GROUP" --yes

# Déploiement du conteneur sur Azure Container Instances
echo "🚀 Deploying container to Azure Container Instances..."
az container create \
  --name "$CONTAINER_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --image "$ACR_URL/$ACR_IMAGE" \
  --cpu "$CPU" \
  --memory "$MEMORY" \
  --registry-login-server "$ACR_URL" \
  --registry-username "$ACR_USERNAME" \
  --registry-password "$ACR_PASSWORD" \
  --ports "$PORT" \
  --ip-address "$IP_ADDRESS" \
  --dns-name-label "$DNS_LABEL" \
  --os-type "$OS_TYPE" \
  --environment-variables ENV="$ENV" DATABASE_URL="$DATABASE_URL"

# Affichage des informations de déploiement
if [ $? -eq 0 ]; then
    echo "✅ Deployment succeeded!"
    echo "🌍 Container URL: http://$DNS_LABEL.$IP_ADDRESS.azurecontainer.io:$PORT"
else
    echo "❌ Deployment failed!"
    exit 1
fi
