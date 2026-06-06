FROM node:20-alpine

RUN npm install -g @nestjs/cli

WORKDIR /app

COPY package*.json tsconfig*.json tsconfig.build.json ./

RUN npm install

COPY src ./src

# Executa o build
RUN npm run build

EXPOSE 3000

CMD ["node", "dist/main"]