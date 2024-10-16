# Cypress E2E

**Audience**: TDP Software Engineers <br>
**Subject**:  Cypress Refactor <br>
**Date**:     October 16th, 2024 <br>

## Summary
Digging into our pipeline failures associated in ticket #3141, it was found that our cypress code is not easily extensible and has bugs associated with lack of session management and compartmentilization.

## Background (Optional)
Speak to splitting up gherkin tests, 30 sec wait for `authcheck`, etc.

## Out of Scope
* Any changes to frontend ReactJS and Nginx apps
* Significant changes to backend authentication
* New Cypress workflows beyond our end-to-end test against deployed develop branch

## Method/Design
This section should contain sub sections that provide general implementation details surrounding key components required to implement the feature.

### Abstracted Gherkin Steps
sub header content describing component.

### Session Management Documentation
https://github.com/cypress-io/cypress/issues/16975
https://docs.cypress.io/api/commands/session#Switching-sessions-inside-tests
https://docs.cypress.io/api/commands/intercept

What do these cypress? How will they help us manage sessions?


### Abstracted utility authentication functions



## Affected Systems
Existing Django CypressAuth class, django middleware, and existing Nginx implementation.

## Use and Test cases to consider
provide a list of use cases and test cases to be considered when the feature is being implemented.
