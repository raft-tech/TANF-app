# Cypress Integration Testing

This documents the findings from Spike ticket [#377](https://github.com/raft-tech/TANF-app/issues/377)

## Mocking Requests

In order to implement integration testing with Cypress, we can mock these requests and make it seem as if we did the login through login.gov, by mocking the `authenticated` field on the check auth endpoint.

+ This will not actually hit login.gov
	+ is not dependent on login.gov servers 
	+ will not confirm if the login.gov integration is functioning correctly.
+ Will fool client into thinking we are authorized, because our mock data `authenticated` flag will be true.
+ Allows us to run Cypress integration tests on the rest of the app


### Approach

+ Create a stub for every django endpoint we expect the client to be able to hit
+ During the normal authorization process, instead of redirecting to login.gov, the target will be the default landing page after login (currently this is `/edit-profile`)
+ `/v1/auth_check` will hand the authorized flag over to redux state
+ We can view app from with in our tests as if we'd authorized through login.gov

### Considerations

+ Will allow us to move forward with a robust integration testing suite

### Useful resources

https://docs.cypress.io/guides/guides/network-requests.html#Testing-Strategies
https://developers.login.gov/testing/
