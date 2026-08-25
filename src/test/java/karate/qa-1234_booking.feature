Feature: QA-1234 - Booking Form Submission

  Background:
    Given the user opens the booking form

  Scenario: TC-001 - Fill all mandatory fields and submit the booking form
    When the user fills all mandatory fields
    And submits the booking form
    Then the success message should be displayed

  Scenario: TC-002 - Leave the Name field empty and submit the booking form
    When the user leaves the Name field empty
    And submits the booking form
    Then the success message should not be displayed

  Scenario: TC-003 - Leave the Number field empty and submit the booking form
    When the user leaves the Number field empty
    And submits the booking form
    Then the success message should not be displayed