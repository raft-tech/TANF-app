/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'

When('I log in as a new user', () => {
  cy.login('new-cypress@teamraft.com')
})

Then('I see a Request Access form', () => {
  cy.contains('Welcome').should('exist')
  cy.get('button').contains('Request Access').should('exist')
})

When('The admin logs in', () => {
  cy.adminLogin('cypress-admin@teamraft.com')
})

When('The admin approves a new user', () => {
  cy.get('@cypressUser').then((cypressUser) => {
    cy.get('@adminCsrfToken').then((csrfToken) => {
      let options = {
        method: 'POST',
        url: `http://localhost:8080/admin/users/user/${cypressUser.selector.id}/change`,
        headers: { 'X_CSRFTOKEN': `${csrfToken}` },
        body: {
          username: `${cypressUser}`,
          account_approval_status: 'Approved',
          _save: 'Save'
        },
      }
      cy.adminApiRequest(options)
    })
  })
})

Then('The new user can access everything', () => {
  cy.login('new-cypress@teamraft.com')
})