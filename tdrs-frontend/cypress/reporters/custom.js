// cypress/reporters/custom.js

const MochaJUnitReporter = require('mocha-junit-reporter');
const fs = require('fs');
const path = require('path');

class CustomJUnitReporter extends MochaJUnitReporter {
  constructor(runner, options) {
    super(runner, options);

    // Access reporter options
    this.options = options.reporterOptions;

    // Listen for the 'end' event to perform actions after all tests are run
    runner.on('end', () => {
      this.generateCustomXml();
    });
  }

  generateCustomXml() {
    // Call the original generateXml function from MochaJUnitReporter
    // This will create the standard JUnit XML file

    // Now, you can load the generated XML and modify it or add custom data
    const xmlFilePath = this.options.mochaFile || path.join(process.cwd(), 'test-results.xml'); // Default path

    if (fs.existsSync(xmlFilePath)) {
      let xmlContent = fs.readFileSync(xmlFilePath, 'utf8');

      // Example: Add a custom attribute to the <testsuite> tag
      xmlContent = xmlContent.replace('<testsuite ', '<testsuite customAttribute="yourValue" ');

      // Example: You could also parse the XML, modify specific elements, and then re-serialize it.
      // For more complex XML manipulation, consider using a library like 'xml2js' or 'fast-xml-parser'.

      fs.writeFileSync(xmlFilePath, xmlContent, 'utf8');
      console.log(`Custom XML generated at: ${xmlFilePath}`);
    } else {
      console.warn(`Could not find JUnit XML file at ${xmlFilePath} to customize.`);
    }
  }
}

module.exports = CustomJUnitReporter;
