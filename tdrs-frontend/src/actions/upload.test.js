import axios from 'axios'
import thunk from 'redux-thunk'
import configureStore from 'redux-mock-store'

import { upload, SET_FILE, SET_FILE_ERROR, setYear, SET_YEAR } from './upload'

describe('actions/upload.js', () => {
  const mockStore = configureStore([thunk])

  it('should dispatch SET_FILE', async () => {
    axios.post.mockImplementationOnce(() => Promise.resolve('HELLO'))

    const store = mockStore()

    await store.dispatch(upload({ file: 'HELLO', name: 'testing' }))

    const actions = store.getActions()

    expect(actions[0].type).toBe(SET_FILE)
    expect(actions[0].payload).toStrictEqual({ file: 'HELLO', name: 'testing' })
  })

  it('should dispatch SET_FILE_ERROR when there is an error with the post', async () => {
    axios.post.mockImplementationOnce(() =>
      Promise.reject(Error({ message: 'something went wrong' }))
    )

    const store = mockStore()

    await store.dispatch(upload({ file: 'HELLO', name: 'testing' }))

    const actions = store.getActions()

    expect(actions[0].type).toBe(SET_FILE_ERROR)
    expect(actions[0].payload).toStrictEqual({
      error: Error({ message: 'something went wrong' }),
      name: 'testing',
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
