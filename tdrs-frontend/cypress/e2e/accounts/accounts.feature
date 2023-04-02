Feature: Users can create and manage their accounts
    Scenario: A user can log in
        When The user visits the home page
        And 'new-cypress@teamraft.com' logs in
        Then I see a Request Access form
    Scenario: A new user is put in the pending state
        Given The admin logs in
        And The user is in begin state
        When The user visits the home page
        And 'new-cypress@teamraft.com' logs in
        And The user requests access
        And The admin sets the approval status of 'new-cypress@teamraft.com' to 'Pending'
        Then The user sees the request still submitted
    Scenario: A new user is approved and can see the app homepage
        Given The admin logs in
        And The user is in begin state
        When The user visits the home page
        And 'new-cypress@teamraft.com' logs in
        And The user requests access
        And The admin sets the approval status of 'new-cypress@teamraft.com' to 'Approved'
        Then The user can see the hompage
    Scenario: A new user is denied access
        Given The admin logs in
        And The user is in begin state
        When The user visits the home page
        And 'new-cypress@teamraft.com' logs in
        And The user requests access
        And The admin sets the approval status of 'new-cypress@teamraft.com' to 'Denied'
        Then The user sees request page again
    Scenario: A user account is deactivated
        Given The admin logs in
        And The user is in begin state
        When The user visits the home page
        And 'new-cypress@teamraft.com' logs in
        And The user requests access
        And The admin sets the approval status of 'new-cypress@teamraft.com' to 'Approved'
        And The user can see the hompage
        And The admin sets the approval status of 'new-cypress@teamraft.com' to 'Deactivated'
        Then The user cannot log in


