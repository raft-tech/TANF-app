ARG NODE_VERSION=22-alpine

FROM node:${NODE_VERSION} AS base
WORKDIR /home/node/app
ENV NEXT_TELEMETRY_DISABLED=1
RUN chown -R node:node /home/node
USER node
COPY --chown=node:node package*.json ./

FROM base AS deps
RUN npm ci

FROM deps AS localdev
COPY --chown=node:node . .
CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0", "--port", "3000"]

FROM deps AS build
COPY --chown=node:node . .
RUN npm run build

FROM node:${NODE_VERSION} AS runtime
WORKDIR /home/node/app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
RUN chown -R node:node /home/node
USER node
COPY --from=build --chown=node:node /home/node/app/.next ./.next
COPY --from=build --chown=node:node /home/node/app/public ./public
COPY --from=build --chown=node:node /home/node/app/package*.json ./
COPY --from=build --chown=node:node /home/node/app/next.config.ts ./next.config.ts
COPY --from=build --chown=node:node /home/node/app/node_modules ./node_modules
EXPOSE 3000
CMD ["npm", "run", "start", "--", "--hostname", "0.0.0.0", "--port", "3000"]
