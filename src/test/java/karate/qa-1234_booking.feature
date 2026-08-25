Feature: QA-1234 Guest Booking Form Submission
  As a guest, I want to submit the booking form so that I can complete my booking.

  Background:
    Given the guest is on the booking form page

  Scenario: TC-001: Fill all mandatory fields and submit the booking form
    Given all mandatory fields are filled
    When the guest submits the booking form
    Then the success message should be displayed

  Scenario: TC-002: Leave the Name field empty and submit the booking form
    Given the Name field is left empty
    When the guest submits the booking form
    Then the success message should not be displayed

  Scenario: TC-003: Leave the Number field empty and submit the booking form
    Given the Number field is left empty
    When the guest submits the booking form
    Then the success message should not be displayed