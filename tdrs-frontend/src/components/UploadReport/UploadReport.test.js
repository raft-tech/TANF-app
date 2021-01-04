import React from 'react'
import thunk from 'redux-thunk'
import { mount } from 'enzyme'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { fireEvent, render } from '@testing-library/react'
import axios from 'axios'

import UploadReport from './UploadReport'

describe('UploadReport', () => {
  const initialState = {
    reports: {
      files: [
        {
          section: 'Active Case Data',
          fileName: null,
          error: null,
        },
        {
          section: 'Closed Case Data',
          fileName: null,
          error: null,
        },
        {
          section: 'Aggregate Data',
          fileName: null,
          error: null,
        },
        {
          section: 'Stratum Data',
          fileName: null,
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
      reports: {
        files: [
          {
            section: 'Active Case Data',
            fileName: null,
            error: {
              message: 'something went wrong',
            },
          },
          {
            section: 'Closed Case Data',
            fileName: null,
            error: null,
          },
          {
            section: 'Aggregate Data',
            fileName: null,
            error: null,
          },
          {
            section: 'Stratum Data',
            fileName: null,
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

  it('should clear input value if there is an error', () => {
    const store = mockStore(initialState)
    axios.post.mockImplementationOnce(() =>
      Promise.reject(Error({ message: 'something went wrong' }))
    )

    const { container } = render(
      <Provider store={store}>
        <UploadReport />
      </Provider>
    )

    const fileInput = container.querySelector('#activeCase')

    const newFile = new File(['test'], 'test.txt', { type: 'text/plain' })
    const fileList = [newFile]

    fireEvent.change(fileInput, {
      target: {
        name: 'Active Case Data',
        files: fileList,
      },
    })

    expect(fileInput.value).toStrictEqual('')
  })
})
