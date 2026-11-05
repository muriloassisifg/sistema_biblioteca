# A receita do app, em duas etapas. O resultado leva só os arquivos prontos e o
# Nginx: o Flutter, que é grande, fica de fora da imagem final.

# Etapa 1: um Flutter já instalado constrói o app.
FROM ghcr.io/cirruslabs/flutter:stable AS construcao
WORKDIR /codigo
COPY . .
# O endereço da API vem de fora, na hora de construir.
ARG API_URL
RUN flutter pub get && flutter build web --dart-define=API_URL=$API_URL

# Etapa 2: um Nginx entrega os arquivos prontos ao navegador.
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=construcao /codigo/build/web /usr/share/nginx/html
EXPOSE 80
