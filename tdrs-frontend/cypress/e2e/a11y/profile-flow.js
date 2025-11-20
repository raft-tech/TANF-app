/// <reference types="cypress" />

import { ACTORS, clearCookies } from '../common-steps/common-steps'

function terminalLog(violations) {
  cy.task(
    'log',
    `${violations.length} accessibility violation${
      violations.length === 1 ? '' : 's'
    } ${violations.length === 1 ? 'was' : 'were'} detected`
  )

  const violationData = violations.map(
    ({ id, impact, description, nodes }) => ({
      id,
      impact,
      description,
      nodes: nodes.length,
    })
  )

  cy.task('table', violationData)
}

/**
 * Log in once as Data Analyst Stefani, like the Cucumber `{string} logs in` step.
 */
const loginAsDataAnalystStefani = () => {
  clearCookies()

  cy.visit('/')
  cy.adminLogin('cypress-admin-alex@teamraft.com')

  const username = ACTORS['Data Analyst Stefani'].username
  cy.contains('Sign into TANF Data Portal', { timeout: 30000 })
  cy.login(username)
}

/* ───────────── Profile flow accessibility ───────────── */

describe('Profile flow accessibility', () => {
  before(() => {
    loginAsDataAnalystStefani()
  })

  it('is accessible when viewing profile', () => {
    cy.visit('/profile')

    // make sure we are on the profile page
    cy.url().should('include', '/profile')
    cy.get('main').should('exist')

    cy.injectAxe()

    cy.checkA11y(
      'main',
      {
        includedImpacts: ['critical', 'serious'],
      },
      terminalLog
    )
  })
})
