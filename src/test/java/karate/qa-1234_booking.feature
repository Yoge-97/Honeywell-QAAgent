Feature: Booking Form Submission

  Background:
    Given I am on the booking form

  Scenario: TC-001 - Fill all mandatory fields and submit the booking form
    When I fill all mandatory fields
    And I submit the booking form
    Then the success message should be displayed

  Scenario: TC-002 - Leave the Name field empty and submit the booking form
    When I leave the Name field empty
    And I submit the booking form
    Then the success message should not be displayed

  Scenario: TC-003 - Leave the Number field empty and submit the booking form
    When I leave the Number field empty
    And I submit the booking form
    Then the success message should not be displayed