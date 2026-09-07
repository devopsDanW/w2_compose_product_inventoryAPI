FROM nginx:1.26.2-alpine-slim AS validator

COPY index.html /usr/share/nginx/html/index.html
COPY nginx.conf /etc/nginx/conf.d/default.conf

RUN nginx -t && test -s /usr/share/nginx/html/index.html

FROM nginx:1.26.2-alpine-slim

COPY --from=validator /usr/share/nginx/html/index.html /usr/share/nginx/html/index.html
COPY --from=validator /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

## fix error "catalogue-web-1  | nginx: [emerg] mkdir() "/var/cache/nginx/client_temp" failed (13: Permission denied)"
## fix error nginx: [emerg] open() "/var/run/nginx.pid" failed (13: Permission denied)
RUN chown nginx:nginx /var/cache/nginx \
    && touch /var/run/nginx.pid \
    && chown nginx:nginx /var/run/nginx.pid

## user nginx UID 101
USER 101

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD ["wget", "--no-verbose", "--tries=1", "--spider", "http://127.0.0.1"]

ENTRYPOINT [ "/entrypoint.sh" ]