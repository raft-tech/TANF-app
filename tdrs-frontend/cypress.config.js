const { defineConfig } = require('cypress')
const webpack = require('@cypress/webpack-preprocessor')
const preprocessor = require('@badeball/cypress-cucumber-preprocessor')

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    specPattern: '**/*.feature',
    experimentalSessionAndOrigin: true,

    env: {
      apiUrl: 'http://localhost:8080/v1',
      cypressToken: 'local-cypress-token',
      cypressName: 'cypress',
      cypressStt: '6',
      cypressSttName: 'Colorado',
      cypressGroup: '2',
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
