```karate
@QA-1234
Feature: Dream Journey Booking Form Submission

  Background:
    * url baseUrl
    * path '/api/v1/bookings'

  Scenario: Successfully submit booking form with all required fields
    Given request
      """
      {
        "name": "John Doe",
        "number": "+1234567890",
        "place": "Paris",
        "address": "123 Travel Lane, City"
      }
      """
    When method post
    Then status 200
    And match response == { status: "Success", bookingId: "#present", message: "#present" }

  Scenario Outline: Incomplete submission fails when missing standard required field '<missingField>'
    Given request <requestPayload>
    When method post
    Then status 400
    And match response.status != "Success"

    Examples:
      | missingField | requestPayload                                                                                    |
      | name         | { "number": "+1234567890", "place": "Paris", "address": "123 Travel Lane, City" }                 |
      | number       | { "name": "John Doe", "place": "Paris", "address": "123 Travel Lane, City" }                      |
      | place        | { "name": "John Doe", "number": "+1234567890", "address": "123 Travel Lane, City" }               |
      | address      | { "name": "John Doe", "number": "+1234567890", "place": "Paris" }                                 |
```