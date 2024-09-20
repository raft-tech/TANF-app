Feature: Users can create and manage their accounts
    Scenario: A user can log in
      Given The admin logs in
        And 'new-cypress@teamraft.com' is in begin state
        When 'new-cypress@teamraft.com' visits the home page
        And 'new-cypress@teamraft.com' logs in
        Then 'new-cypress@teamraft.com' sees a Request Access form
    Scenario: A new user is put in the pending state
        Given The admin logs in
        And 'new-cypress@teamraft.com' is in begin state
        When 'new-cypress@teamraft.com' visits the home page
        And 'new-cypress@teamraft.com' logs in
        Then 'new-cypress@teamraft.com' requests access
        And The admin sets the approval status of 'new-cypress@teamraft.com' to 'Pending'
        Then 'new-cypress@teamraft.com' sees the request still submitted
    Scenario: A new user requests access
        Given The admin logs in
        And 'new-cypress@teamraft.com' is in begin state
        When 'new-cypress@teamraft.com' visits the home page
        And 'new-cypress@teamraft.com' logs in
        When 'new-cypress@teamraft.com' requests access
        Then 'new-cypress@teamraft.com' sees the request still submitted
    Scenario: A new user is approved and can see the app homepage
        Given The admin logs in
        When 'new-cypress@teamraft.com' visits the home page
        Then The admin sets the approval status of 'new-cypress@teamraft.com' to 'Approved'
        And 'new-cypress@teamraft.com' logs in
        Then 'new-cypress@teamraft.com' can see the hompage
    Scenario: A new user is denied access
        Given The admin logs in
        And 'new-cypress@teamraft.com' is in begin state
        When 'new-cypress@teamraft.com' visits the home page
        And 'new-cypress@teamraft.com' logs in
        Then 'new-cypress@teamraft.com' requests access
        And The admin sets the approval status of 'new-cypress@teamraft.com' to 'Denied'
        Then 'new-cypress@teamraft.com' sees request page again
    Scenario: A deactived user account setup
        Given The admin logs in
        And 'new-cypress@teamraft.com' is in approved state
        When 'new-cypress@teamraft.com' visits the home page
        When 'new-cypress@teamraft.com' logs in
    Scenario: User account is deactivated
        Given The admin logs in
        When The admin sets the approval status of 'new-cypress@teamraft.com' to 'Deactivated'
        Then 'new-cypress@teamraft.com' fails to log in
