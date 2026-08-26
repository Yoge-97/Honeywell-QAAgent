```karate
@QA-1234
# Reviewers: shrilekha-s, kiruthika-knack26
Feature: Guest Booking Form Submission for Dream Journey

  As a Guest visiting the Dream Journey site
  I want to fill out and submit the booking form
  So that I can reserve my selected travel package and see a confirmation

  Background:
    * url baseUrl
    * path '/api/bookings'
    * header Content-Type = 'application/json'

  @positive
  Scenario: Successfully submit booking form with all required details
    Given request
      """
      {
        "name": "John Doe",
        "number": "9876543210",
        "place": "Paris",
        "address": "123 Main Street"
      }
      """
    When method post
    Then status 200
    And match response == { status: 'Success', message: '#present' }

  @negative
  Scenario Outline: Incomplete submission missing <field> fails and does not show Success
    Given request <payload>
    When method post
    Then status 400
    And match response.status != 'Success'

    Examples:
      | field   | payload                                                                         |
      | name    | { "number": "9876543210", "place": "Paris", "address": "123 Main Street" }      |
      | number  | { "name": "John Doe", "place": "Paris", "address": "123 Main Street" }          |
      | place   | { "name": "John Doe", "number": "9876543210", "address": "123 Main Street" }    |
      | address | { "name": "John Doe", "number": "9876543210", "place": "Paris" }                |
```