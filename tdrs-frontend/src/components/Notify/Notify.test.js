import React from 'react'
import thunk from 'redux-thunk'
import { mount } from 'enzyme'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { Alert } from '@trussworks/react-uswds'
import { ALERT_INFO, Notify } from '.'

describe('Notify.js', () => {
  const mockStore = configureStore([thunk])

  it('returns an Alert component', () => {
    const store = mockStore({
      alert: {
        show: true,
        type: ALERT_INFO,
        heading: 'Hey, Look at Me!',
        body: 'more details',
      },
    })
    const wrapper = mount(
      <Provider store={store}>
        <Notify />
      </Provider>
    )
    expect(wrapper.find(Alert)).toExist()
    expect(wrapper.find('h3')).toIncludeText('Hey, Look at Me!')
    expect(wrapper.find('p')).toIncludeText('more details')
  })

  it('returns nothing if the "show" property is false', () => {
    const store = mockStore({ alert: { show: false } })
    const wrapper = mount(
      <Provider store={store}>
        <Notify />
      </Provider>
    )
    expect(wrapper.find(Alert)).not.toExist()
  })
})
