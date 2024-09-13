const { defineConfig } = require('cypress')
const webpack = require('@cypress/webpack-preprocessor')
const preprocessor = require('@badeball/cypress-cucumber-preprocessor')

module.exports = defineConfig({
  defaultCommandTimeout: 10000,
  e2e: {
    baseUrl: 'https://tdp-frontend-develop.acf.hhs.gov', //'http://localhost:3000',
    specPattern: '**/*.feature',

    env: {
      apiUrl: 'https://tdp-frontend-develop.acf.hhs.gov/v1', //'http://localhost:3000/v1',
      adminUrl: 'https://tdp-frontend-develop.acf.hhs.gov/admin', //'http://localhost:3000/admin',
      cypressToken: 'VPryEbqCsudfVCgen2kk', //'local-cypress-token',
    },

    async setupNodeEvents(on, config) {
      // implement node event listeners here
      await preprocessor.addCucumberPreprocessorPlugin(on, config)

      const webpackOptions = {
        resolve: {
          extensions: ['.ts', '.js'],
        },
        module: {
          rules: [
            {
              test: /\.feature$/,
              use: [
                {
                  loader: '@badeball/cypress-cucumber-preprocessor/webpack',
                  options: config,
                },
              ],
            },
          ],
        },
      }

      on('file:preprocessor', webpack({ webpackOptions }))

      return config
    },
  },
})
