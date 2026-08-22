FROM nginx:1.26.2-alpine-slim AS validator

COPY index.html /usr/share/nginx/html/index.html
COPY nginx.conf /etc/nginx/conf.d/default.conf

RUN nginx -t
RUN test -s /usr/share/nginx/html/index.html

FROM nginx:1.26.2-alpine-slim

COPY --from=validator /usr/share/nginx/html/index.html /usr/share/nginx/html/index.html
COPY --from=validator /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://127.0.0.1 || exit 1

ENTRYPOINT [ "/entrypoint.sh" ]