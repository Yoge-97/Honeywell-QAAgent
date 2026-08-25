Feature: QA-1234 Guest Booking Form Submission
  As a guest, I want to submit the booking form so that I can complete my booking.

  Background:
    * def bookingFormUrl = '/booking'

  @TC-001
  Scenario: TC-001 - Fill all mandatory fields and submit the booking form
    Given I am on the booking form page
    When I fill in all mandatory fields
    And I submit the booking form
    Then success message should be displayed

  @TC-002
  Scenario: TC-002 - Leave the Name field empty and submit the booking form
    Given I am on the booking form page
    When I leave the Name field empty
    And I submit the booking form
    Then success message should not be displayed

  @TC-003
  Scenario: TC-003 - Leave the Number field empty and submit the booking form
    Given I am on the booking form page
    When I leave the Number field empty
    And I submit the booking form
    Then success message should not be displayed