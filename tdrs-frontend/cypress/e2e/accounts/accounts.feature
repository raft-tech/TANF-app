Feature: Users can create and manage their accounts
    Scenario: A user can log in
        When The user visits the home page
        And The new user logs in
        Then I see a Request Access form
    Scenario: A new user is put in the pending state
        Given The admin logs in
        And The user is in begin state
        When The user visits the home page
        And The user logs in
        And The user requests access
        And The admin puts the user in pending
        Then The user sees the request still submitted
    Scenario: A new user is approved and can see the app homepage
        Given The admin logs in
        And The user is in begin state
        When The user visits the home page
        And The user logs in
        And The user requests access
        And The admin approves the user
        Then The user can see the hompage
    Scenario: A new user is denied access
        Given The admin logs in
        And The user is in begin state
        When The user visits the home page
        And The user logs in
        And The user requests access
        And The admin denies the user
        Then The user sees request page again
    Scenario: A user account is deactivated
        Given The admin logs in
        And The user is in begin state
        When The user visits the home page
        And The user logs in
        And The user requests access
        And The admin approves the user
        And The user can see the hompage
        And The admin deactivates the user account
        Then The user cannot log in


