Feature: Users can create and manage their accounts
  # Scenario: A user can log in
  #     When I visit the home page
  #     And I log in as a new user
  #     Then I see a Request Access form
  Scenario: A new user is approved and can see everything
    Given The admin logs in
    And The cypress user is in begin state
    # Given The admin logs out
    When I visit the home page
    And The new user logs in
    And The cypress user requests access
    # When The admin logs in
    And The admin approves a new user
    # Then The admin logs out
    Then The new user can see everything
