# Estágio 1: Build
FROM node:22-alpine AS builder
WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Estágio 2: Produção
FROM node:22-alpine
WORKDIR /usr/src/app

# Copia apenas o necessário para produção
COPY package*.json ./
#   RUN npm install --only=production retirado pois apenas dockerfile de prd precisa dessa linha
RUN npm install

COPY --from=builder /usr/src/app/dist ./dist

# Comando para iniciar o serviço
CMD ["node", "dist/main"]