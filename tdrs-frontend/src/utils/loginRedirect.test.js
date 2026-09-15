import {
  clearLoginDestination,
  getLoginDestination,
  saveLoginDestination,
} from './loginRedirect'

describe('login destinations', () => {
  beforeEach(() => {
    window.sessionStorage.clear()
  })

  afterEach(() => {
    jest.restoreAllMocks()
    window.sessionStorage.clear()
  })

  it.each([
    '/data-files?type=tanf',
    '/fra-data-files/2026/1?type=fra#history',
    '/profile',
    '/feedback-reports?name=a%26b%2Bc#reports',
  ])('preserves the full local destination %s', (destination) => {
    saveLoginDestination(destination)
    expect(getLoginDestination()).toBe(destination)
  })

  it('defaults to home when no destination has been saved', () => {
    expect(getLoginDestination()).toBe('/home')
  })

  it('clears the saved destination after use', () => {
    saveLoginDestination('/profile')
    clearLoginDestination()
    expect(getLoginDestination()).toBe('/home')
  })

  it('uses the most recently requested page', () => {
    saveLoginDestination('/profile')
    saveLoginDestination('/data-files?type=tanf')
    expect(getLoginDestination()).toBe('/data-files?type=tanf')
  })

  it.each([
    '',
    'https://example.com/data-files',
    '//example.com/data-files',
    '///example.com',
    '/\\example.com',
    '/\n/example.com',
    // eslint-disable-next-line no-script-url -- Verify script URLs are rejected.
    'javascript:alert(1)',
    'data-files',
    '/',
    '/?type=tanf',
    '/login',
    '/login/?next=/profile',
    '/LOGIN',
    '/%6cogin',
    '/data-files/../login',
    '/profile/..',
    '/%invalid',
  ])('rejects unsafe or looping destinations: %s', (destination) => {
    saveLoginDestination(destination)
    expect(getLoginDestination()).toBe('/home')
  })

  it('allows sign-in to continue when saving a destination fails', () => {
    jest.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('Storage unavailable')
    })
    expect(() => saveLoginDestination('/profile')).not.toThrow()
  })

  it('defaults to home when reading storage fails', () => {
    jest.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('Storage unavailable')
    })
    expect(getLoginDestination()).toBe('/home')
  })

  it('allows sign-in to continue when clearing a destination fails', () => {
    jest.spyOn(Storage.prototype, 'removeItem').mockImplementation(() => {
      throw new Error('Storage unavailable')
    })
    expect(clearLoginDestination).not.toThrow()
  })
})
