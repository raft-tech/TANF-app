import axios from 'axios'
import thunk from 'redux-thunk'
import configureStore from 'redux-mock-store'

import { upload, SET_FILE, SET_FILE_ERROR, setYear, SET_YEAR } from './reports'

describe('actions/reports.js', () => {
  const mockStore = configureStore([thunk])

  it('should dispatch SET_FILE', async () => {
    axios.post.mockImplementationOnce(() =>
      Promise.resolve({ data: { signed_url: 'www.test.com' } })
    )

    const store = mockStore()

    await store.dispatch(
      upload({ file: { name: 'HELLO' }, section: 'Active Case Data' })
    )

    const actions = store.getActions()

    expect(actions[0].type).toBe(SET_FILE)
    expect(actions[0].payload).toStrictEqual({
      fileName: 'HELLO',
      section: 'Active Case Data',
    })
  })

  it('should dispatch SET_FILE_ERROR when there is an error with the post', async () => {
    axios.post.mockImplementationOnce(() =>
      Promise.reject(Error({ message: 'something went wrong' }))
    )

    const store = mockStore()

    await store.dispatch(
      upload({
        file: { name: 'HELLO', type: 'text/plain' },
        section: 'Active Case Data',
      })
    )

    const actions = store.getActions()

    expect(actions[0].type).toBe(SET_FILE_ERROR)
    expect(actions[0].payload).toStrictEqual({
      error: Error({ message: 'something went wrong' }),
      section: 'Active Case Data',
    })
  })
})

describe('actions/setYear', () => {
  const mockStore = configureStore([thunk])

  it('should dispatch SET_YEAR', async () => {
    const store = mockStore()

    await store.dispatch(setYear(2020))

    const actions = store.getActions()

    expect(actions[0].type).toBe(SET_YEAR)
    expect(actions[0].payload).toStrictEqual({ year: 2020 })
  })
})
