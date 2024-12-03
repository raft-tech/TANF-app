# TITLE

**Audience**: TDP Software Engineers <br>
**Subject**:  Upgrading frontend dependencies - React Scripts v5 upgrade <br>
**Date**:     Dec 2, 2024 <br>

## Summary
This technical memorandum focuses on the effort required to upgrade react-scripts (create-react-app) from v3 to v5. This update contains breaking changes, which are described, along with the changes required to fix them, below.

1. Webpack changes
2. SASS updates
3. USWDS
4. Browser vs Node runtime (file-type)

## Background (Optional)
Background for the feature if necessary.

## Out of Scope
Call out what is out of scope for this technical memorandum and should be considered in a different technical memorandum.

* refactor frontend to VC display/logic components paradigm + context api

## Method/Design
This section should contain sub sections that provide general implementation details surrounding key components required to implement the feature.
≠
1. Update all the deps using `npm-check-updates`
    ```bash
    npx npm-check-updates -u
    npm install
    ```
   * This will bump every package version to the latest available. However, since certain dependencies require specific versions of other packages, this step is not complete until dependency conflicts are resolved. Compile and run the application, and downgrade/pin any dependency versions that are in conflict.
2. Update the linter rules to allow trailing commas 
    * `.eslintrc.json`, add
        ```json
        "comma-dangle": 0,
        ```
    * `.prettierrc.json`, add
        ```json
        "singleQuote": true,
        "trailingComma": "es5"
        ```
3. Remove SASS_PATH from env - This line appears in the `.env` files, as well as the dockerfile. It will be replaced in step 7 (upgrade USWDS)
    ```bash
    ENV SASS_PATH=node_modules:src
    ```
4. Implement React 18 changes
    * In `src/index.js` the root component should now look like this
        ```javascript
        import React from 'react'
        import { createRoot } from 'react-dom/client'

        // ... other stuff, all the same

        const container = document.getElementById('root')
        const root = createRoot(container)
        root.render(
            <Provider store={store}>
                <Router store={store} history={history}>
                <App />
                </Router>
            </Provider>
        )
        ```
5. Update library imports
    * Some library imports changed. The new paths are generally included in the error message when compiling/bundling. If they aren't, consult the library's documentation for the new version. If they STILL aren't (yes, it happens), you can go into `node_modules/{package name}/package.json` and find the `exports` section, which lists the export paths. From there, you can dig through the files to find what you're looking for.
    * One example is `thunk`, which had some minor export changes
        ```javascript
        import thunkMiddleware from 'redux-thunk' // old way

        import { thunk } from 'redux-thunk' // new way
        ```
    * Named exports (e.g., `import { thunk } from 'redux-thunk'`) can be renamed so that the code doesn't have to be further changed by using the `as` keyword
        ```javascript
        import { thunk as thunkMiddleware } from 'redux-thunk'
        ```
6. Update SASS import syntax
    1. In `src/index.scss` `@import` becomes `@forward`
        ```scss
        @forward "src/assets/uswds/_uswds-theme-general";

        @forward "uswds";

        @forward 'src/assets/App';
        @forward 'src/assets/GovBanner';
        @forward 'src/assets/Header';
        // etc
        ```
7. Implement USWDS v3
    * `package.json` - `start` and `build` need the following pre-pended to the react-scripts command
        ```bash
        SASS_PATH=\"`cd \"./src\";pwd`:./node_modules/@uswds:./node_modules/@uswds/uswds/packages\"
        ```
    * eg
        ```bash
        "start": "SASS_PATH=\"`cd \"./src\";pwd`:./node_modules/@uswds:./node_modules/@uswds/uswds/packages\" react-scripts start",
        "build": "sh -ac '. ./.env.${REACT_APP_ENV}; SASS_PATH=\"`cd \"./src\";pwd`:./node_modules/@uswds:./node_modules/@uswds/uswds/packages\" react-scripts build'",
        ```
    * theme customizations in a single file (imported once in `src/index.scss`)
        * critical that all variables customized must have matching default in uswds config. if not, you will get weird import errors. `SassError: This module was already loaded, so it can't be configured using "with".`
        * todo: remove customizations that retain the default so file is not so large.
    * variables in a separate file `src/assets/uswds/_variables.scss`
        ```scss
        $disabled-button-color: #4A4A4A;
        $gov-banner-background: #122E51;
        ```
        * imported by `@use "./assets/uswds/_variables" as *;` in custom scss files
    * imports changed slightly
        * components
            ```javascript
            import { fileInput } from '@uswds/uswds/src/js/components'
            ```
        * sass files
            ```scss
            @use "uswds-core" as *;
            @use "./assets/uswds/_variables" as *;
            @use 'include-media/dist/include-media' as *;
            ```
    * need to test that all components still work from a11y perspective
    * still contains a number of deprecations. these happen when webpack compiles the SASS. will need to update uswds again at some point
        ```bash
        <w> Deprecation color.lightness() is deprecated. Suggestion:
        <w> 
        <w> color.channel($color, "lightness", $space: hsl)
        <w> 
        <w> More info: https://sass-lang.com/d/color-functions
        <w> 
        <w> node_modules/@uswds/uswds/packages/uswds-core/src/styles/mixins/helpers/checkbox-and-radio-colors.scss 68:5  -checkbox-and-radio-colors()
        <w> node_modules/@uswds/uswds/packages/uswds-core/src/styles/mixins/helpers/checkbox-and-radio-colors.scss 12:3  checkbox-colors()
        <w> node_modules/@uswds/uswds/packages/usa-checkbox/src/styles/_usa-checkbox.scss 5:1                            @forward
        <w> node_modules/@uswds/uswds/packages/usa-checkbox/src/styles/_index.scss 4:1                                   @forward
        <w> node_modules/@uswds/uswds/packages/usa-checkbox/_index.scss 8:1                                              @forward
        <w> node_modules/@uswds/uswds/packages/uswds-form-controls/_index.scss 4:1                                       @forward
        <w> node_modules/@uswds/uswds/packages/uswds/_index.scss 51:1                                                    @forward
        <w> src/index.scss 3:1                                                                                           root stylesheet
        <w> 445 repetitive deprecation warnings omitted.
        ```
8. Fix test dependencies
    1. Because of node runtime vs. browser runtime issues for certain packages, may get the following error: `Must use import to load ES Module`
    1. jest must be configured to ignore the es5 versions of some things. Add the following to the `jest` section of `package.json`
        ```json
        "transform": {},
        "moduleNameMapper": {
            "^axios$": "axios/dist/node/axios.cjs",
            "@uswds/uswds/src/js/components": "@uswds/uswds/packages/uswds-core/src/js/index.js",
            "\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$": "jest-transform-stub"
        }
        ```
9. Replace `file-type` library (node runtime) with `file-type-checker` (browser runtime)
    * Error presented: `Cannot find module 'strtok3/core' from 'node_modules/file-type/core.js'` or `Must use import to load ES Module`
    * and remove the `file-type` line from `package.json`'s `dependencies` section.
    * Run
        ```bash
        npm i file-type-checker --save
        ```
    * May be required to delete the `node_modules` folder, then run `npm i` again (if you have cache issues)
10. Fix tests
    1. Only major issue was with `IdleTimer`, need to handle timers and focus the document differently.
        ```javascript
        jest.useFakeTimers()
        let start = Date.now()

        // pre-timeout test code

        React.act(() => {
            jest.setSystemTime(start + 1200000) // replaces jest.runAllTimers() which wasn't working in this case
            fireEvent.focus(document) // required to apply the new time
        })

        // post-timeout test code

        jest.useRealTimers()
        ```
    1. todo: Default props deprecated (warning) - `Warning: STTComboBox: Support for defaultProps will be removed from function components in a future major release. Use JavaScript default parameters instead.`
    1. todo: fix span not allowed as table child warning - `Warning: validateDOMNesting(...): <span> cannot appear as a child of <table>.`
    2. todo: Test deprecations
        * (done) test utils act - `act()` in tests becomes `React.act()`
        * wrapper.find - `Warning: findDOMNode is deprecated and will be removed in the next major release. Instead, add a ref directly to the element you want to reference. Learn more about using refs safely here: https://reactjs.org/link/strict-mode-find-node`
        * redux configureStore - `The signature '(middlewares?: Middleware<{}, any, Dispatch<AnyAction>>[] | undefined): MockStoreCreator<any, {}>' of 'configureStore' is deprecated.`
    3. todo: can utilize `fetch` now that we're upgraded, remove `axios`
11. need to test that all components still work from a11y perspective
12. security vulns
    * Running `npm audit` results in the following
        ```bash
        37 vulnerabilities (19 moderate, 17 high, 1 critical)
        ```
    * These should be addressed as soon as possible

### Sub header (piece of the design, can be many of these)
sub header content describing component.

## Affected Systems
provide a list of systems this feature will depend on/change.

## Use and Test cases to consider
provide a list of use cases and test cases to be considered when the feature is being implemented.

1. A11y compliance