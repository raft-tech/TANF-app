FROM nginx:1.25-alpine

COPY nginx/local/nginx.conf /etc/nginx/nginx.conf
COPY nginx/local/conf.d/default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
