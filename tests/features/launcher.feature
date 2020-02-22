# Created by Flavio Garcia at 01/17/2020
Feature: Launcher
  # A Firenado application is started by a launcher. Here we tests important
  # scenarios related to launchers.

  Scenario: Start and stop a Process launcher
    # Enter steps here
    Given: We have a Firenado Application
    When: We launch the application using a process launcher
      And: The application is running correctly
    Then: We stop the application shutdown the launcher
      And: The application stops
