Feature: Users can create and manage their accounts
  # Scenario: A user can log in
  #     When I visit the home page
  #     And I log in as a new user
  #     Then I see a Request Access form
  Scenario: A new user is approved and can see everything
    Given The admin logs in
    And The user is in begin state
    When I visit the home page
    And The user logs in
    And The user requests access
    And The admin approves the user
    Then The user can see the hompage
