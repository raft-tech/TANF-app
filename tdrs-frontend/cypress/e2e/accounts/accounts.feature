Feature: Users can create and manage their accounts
    # Scenario: A user can log in
    #     When I visit the home page
    #     And I log in as a new user
    #     Then I see a Request Access form
    Scenario: A new user is approved and can see everything
      Given The cypress user is in begin state
      Given The cypress user is in request state
      When The admin logs in
      And The admin approves a new user
      Then The admin logs out
      And The new user logs in
      Then The new user can see everything
