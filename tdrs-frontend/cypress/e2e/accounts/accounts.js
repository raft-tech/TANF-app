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
      cy.changeUserAccountStatus(`${cypressUser.selector.id}`, `${csrfToken}`, 'Approved')
    })
  })
})

Then('The admin logs out', () => {
  let options = {
    method: 'GET',
    url: 'http://localhost:8080/admin/logout/',
  }
  cy.adminApiRequest(options)
  cy.visit("http://localhost:3000/") // Need a better way to enforce the logout so cypress user can log in
})

When('The new user logs in', () => {
  cy.login('new-cypress@teamraft.com')
})

Then('The new user can see everything', () => {

})

When('The cypress user is in begin state', () => {
  cy.adminLogin('cypress-admin@teamraft.com')
  cy.get('@cypressUser').then((cypressUser) => {
    cy.get('@adminCsrfToken').then((csrfToken) => {
      cy.changeUserAccountStatus(`${cypressUser.selector.id}`, `${csrfToken}`, 'Initial')
    })
  })
})
