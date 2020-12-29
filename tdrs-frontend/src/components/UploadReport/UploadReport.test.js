import React from 'react'
import thunk from 'redux-thunk'
import { mount } from 'enzyme'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { render } from '@testing-library/react'

import UploadReport from './UploadReport'

describe('UploadReport', () => {
  const initialState = {
    upload: {
      files: [
        {
          name: 'activeData',
          file: null,
          error: null,
        },
        {
          name: 'closedData',
          file: null,
          error: null,
        },
        {
          name: 'aggregataData',
          file: null,
          error: null,
        },
        {
          name: 'stratumData',
          file: null,
          error: null,
        },
      ],
    },
  }
  const mockStore = configureStore([thunk])

  it('should render four inputs for uploading files', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <UploadReport />
      </Provider>
    )

    const inputs = wrapper.find('.usa-file-input')

    expect(inputs.length).toEqual(4)
  })

  it('should dispatch the `clearError` and `upload` actions when submit button is clicked', () => {
    const store = mockStore(initialState)
    const origDispatch = store.dispatch
    store.dispatch = jest.fn(origDispatch)
    const wrapper = mount(
      <Provider store={store}>
        <UploadReport />
      </Provider>
    )

    const fileInput = wrapper.find('.usa-file-input').first()

    expect(fileInput).toHaveLength(1)

    fileInput.simulate('change', {
      target: {
        files: ['HELLO'],
      },
    })

    expect(store.dispatch).toHaveBeenCalledTimes(2)
  })

  it('should render a div with class "usa-form-group--error" if there is an error', () => {
    const store = mockStore({
      ...initialState,
      upload: {
        files: [
          {
            name: 'activeData',
            file: null,
            error: {
              message: 'something went wrong',
            },
          },
          {
            name: 'closedData',
            file: null,
            error: null,
          },
          {
            name: 'aggregataData',
            file: null,
            error: null,
          },
          {
            name: 'stratumData',
            file: null,
            error: null,
          },
        ],
      },
    })
    render(
      <Provider store={store}>
        <UploadReport />
      </Provider>
    )

    const formGroup = document.querySelector('.usa-form-group')

    expect(formGroup.classList.contains('usa-form-group--error')).toBeTruthy()
  })

  it('should render a div without class "usa-form-group--error" if there is NOT an error', () => {
    const store = mockStore(initialState)
    render(
      <Provider store={store}>
        <UploadReport />
      </Provider>
    )

    const formGroup = document.querySelector('.usa-form-group')

    expect(formGroup.classList.contains('usa-form-group--error')).toBeFalsy()
  })
})
