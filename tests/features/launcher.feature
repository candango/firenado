# Created by Flavio Garcia at 01/17/2020
Feature: Launcher
  # A Firenado application is started by a launcher. Here we tests important
  # scenarios related to launchers.

  Scenario: Start and stop a Process launcher
    # Enter steps here
    Given We launch launcherapp application using process launcher at 128393 port
    When The application is running correctly at 128393 port
    Then We shutdown the process launcher
      And The application stops successfully
