import React from 'react'
import thunk from 'redux-thunk'
import { mount } from 'enzyme'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'

import NewReport from './NewReport'

describe('NewReport', () => {
  const initialState = {}
  const mockStore = configureStore([thunk])
  it('should render an h1 of `New Sample Report 2020`', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <NewReport />
      </Provider>
    )

    const h1 = wrapper.find('h1')

    expect(h1.text()).toEqual('New Sample Report 2020')
  })

  it('should render four inputs for uploading files', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <NewReport />
      </Provider>
    )

    const inputs = wrapper.find('.usa-file-input')

    expect(inputs.length).toEqual(4)
  })

  it('should dispatch the `upload` action when submit button is clicked', () => {
    const store = mockStore(initialState)
    const origDispatch = store.dispatch
    store.dispatch = jest.fn(origDispatch)
    const wrapper = mount(
      <Provider store={store}>
        <NewReport />
      </Provider>
    )

    const fileInput = wrapper.find('.usa-file-input').first()

    expect(fileInput).toHaveLength(1)

    fileInput.simulate('change', {
      target: {
        files: ['HELLO'],
      },
    })

    expect(store.dispatch).toHaveBeenCalledTimes(1)
  })
})
