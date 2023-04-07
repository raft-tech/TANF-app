import { getParseErrors } from './createXLSReport'

it('should create an action to create an XLS report', () => {
  const data_json = {
    data: {},
    xls_report: 'aGVsbG8=',
  }
  // atob is not available in jest
  const expectedReturn = Error(
    'TypeError: URL.createObjectURL is not a function'
  )
  expect(getParseErrors(data_json)).toEqual(expectedReturn)
})

it('should create an action to create an XLS report and throwError', () => {
  const data_json = { data: {} }
  const expectedReturn = Error(
    'InvalidCharacterError: The string to be decoded contains invalid characters.'
  )
  expect(getParseErrors(data_json)).toEqual(expectedReturn)
})
