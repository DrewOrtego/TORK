<p align="center">
    <img src="https://github.com/DrewOrtego/TORK/blob/master/Doc/Images/tork.PNG">
</p>

<p align="center">
<h3>Automate your web-based UI testing using simple, text-based commands</h3>
</p>

## What is TORK?
TORK is a Python framework which eases the process of creating and automating UI tests.
The syntax which TORK recognizes is similar to text-based games like Zork, and is easily customized.
In addition, Python developers with any level of experience can build new commands or edit existing ones by leveraging the intuitive design of TORK.

## Why use TORK?
The goal of TORK is to ease the process of development as well as test writing.
TORK compartmentalizes the three components of UI testing:

1. Test files, for testers and developers
2. Commands, for XPath developers
3. TORK's engine/framework, for Python developers

By using this modular design, a full understanding of TORK is not required to make use of it.
Thus, the tasks involved with UI testing can be distributed based on skill set's, making everyone's job easier.

Additionally, TORK solves quite a few common UI-testing problems:

### Minimal test file management
Many people turn to "automated" test-writing frameworks such as Katalon to record their clicks and keystrokes.
These frameworks are great for making a quick test without needing to learn a new language, but as soon as a major change is implemented in your UI, the tests need to be re-recorded.
TORK avoids this extra work and let's you keep your test files in-tact from release to release, so testers never have to update a test file after they create it, even if the UI changes.

### Tests can remain consistent while changes are implemented in the UI
Since TORK turns XPath expressions (strings used to find DOM elements) into commands, you can update an XPath expression without changing its associated command.
Therefore, a test file which contains the command ```click start-button``` never needs to be changed even if the HTML for the ```start-button``` DOM element does.
In other words, the ```start-button``` XPath can be updated to reflect its current DOM structure without changing the aforementioned commands in the test file.

### Anyone can understand (and write) a test file
No programming knowledge is required to write a test file.
If you can understand a text-based game's syntax, you can understand how to write a test file for TORK.
TORK users have reported a gentle learning curve, and the Wiki documentation expedites the learning process.

### Straightforward design
Debugging and developing only requires knowledge of Python, Selenium, and XPath.
Most concepts utilized in TORK can be understood with a quick Google search, and all functions are documented.

### Built-in reporting
Reviewing the results of an automated test run has two options: you can review a log file, or update a SQLite database which is used to populate a Flask-made website.
Either way, sharing the results of a local test run with your organization is simple, and effective.

## Quick Start Guide

For more information on using TORK, refer to the [Testing-related Wiki pages](https://github.com/DrewOrtego/TORK/wiki#for-testers-and-test-writers).

1. Install Python 3.5 or higher.

2. Install the following modules using a package manager and the optional [requirements.txt]() file.
You'll need Python 3.5 or higher to run the framework, and the following modules:

- decorator 4.3.0 (or later)
- flask 0.12.1 (or later)
- flask_sqlalchemy 2.2 (or later)
- selenium 3.13.0 (or later)

3. Download a webdriver. Firefox is the most dependable browser at this time. Save this file to the root directory of this project.
http://selenium-python.readthedocs.io/installation.html#drivers

4. Run main.py using the following command in your Command Line Interface or IDE:
```-i firefox https://arcgis.com```

5. Once the console and browser are both running, you can start entering commands.
Start by using ```help``` to give you a list of all available commands.
Include an optional argument such as ```help page``` to see all the page-specific available commands.

## How does TORK work?

TORK uses Selenium to run UI-manipulation commands.
Although Selenium has its own commands, TORK can combine multiple commands into one, effectively creating a custom API for UI testers.
Likewise, single Selenium commands can easily become TORK commands, such as ```click``` and ```fill```.

Since TORK recognizes Python functions as commands, developers can write lengthy Selenium or ActionChain work flows into a single function.
TORK turns that function into a text-based command, thus obfuscating complex instructions for anyone who doesn't code, and allowing dev's the ability to quickly implement requested functionality.

TORK uses a simple approach to testing: check the current web page, and make any existing commands for it accessible.

The main algorithm works like this:
1. The current page in the browser is checked for its own Page Object, a code-representation of that page.
2. If found, the commands written for that page are made available to the user.
3. The page is then scanned for additional windows or pop-up's to ensure commands associated with those are made available too.
4. Once all the commands are found, the user is prompted for input.
5. The input is parsed and any errors are reported.
6. If no errors are found, the input is executed, the associated action in the browser executed.
7. Repeat! A while loop continues, restarting at step 1.

## [Wiki Table of Contents](https://github.com/DrewOrtego/TORK/wiki)

### Intro to TORK

[What Is TORK?](https://github.com/DrewOrtego/TORK/wiki/What-Is-TORK%3F)

[Getting the System Requirements](https://github.com/DrewOrtego/TORK/wiki/Getting-the-System-Requirements)

### Testers Reference

[Commands](https://github.com/DrewOrtego/TORK/wiki/Commands)

[Running TORK for the First Time](https://github.com/DrewOrtego/TORK/wiki/Running-TORK-for-the-First-Time)

[Using Interactive Mode to Design and Write Test Files](https://github.com/DrewOrtego/TORK/wiki/Using-Interactive-Mode-to-Design-and-Write-Test-Files)

[Using Automated Mode to Run Test Files](https://github.com/DrewOrtego/TORK/wiki/Using-Automated-Mode-to-Run-Test-Files)

[Writing a Complete Sanity Test File](https://github.com/DrewOrtego/TORK/wiki/Writing-a-Complete-Sanity-Test-File)

[Saving Test Files to GitHub](https://github.com/DrewOrtego/TORK/wiki/Saving-Test-Files-on-GitHub)

### Developers Reference

[Learning XPath](https://github.com/DrewOrtego/TORK/wiki/Learning-XPath)

[Creating and Testing Page Objects and Commands](https://github.com/DrewOrtego/TORK/wiki/Creating-and-Testing-New-Page-Objects-and-Commands)

[Understanding the Page Object Class](https://github.com/DrewOrtego/TORK/wiki/Understanding-the-Page-Object-Class)

[Understanding the Dynamic Element Attribute](https://github.com/DrewOrtego/TORK/wiki/Understanding-the-Dynamic-Element-Attribute)

