import { When } from '@badeball/cypress-cucumber-preprocessor'

When('The user visits the home page', () => {
  cy.visit('/')
  cy.contains('Sign into TANF Data Portal', { timeout: 30000 })
})

When('The admin logs in', () => {
  cy.adminLogin('cypress-admin@teamraft.com')
})

When('{string} logs in', (username) => {
  cy.login(username)
})

When('The admin sets the approval status of {string} to {string}', (username, status) => {
  cy.get('@cypressUser').then((cypressUser) => {
    cy.get('@adminCsrfToken').then((csrfToken) => {
      cy.changeUserInfo(`${cypressUser.selector.id}`, `${csrfToken}`, username, '6', '2', status)
    })
  })
})