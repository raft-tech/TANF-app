import React from 'react'
import thunk from 'redux-thunk'
import { mount, shallow } from 'enzyme'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'

import IdleTimer from './components/IdleTimer'
import GovBanner from './components/GovBanner'
import Header from './components/Header'
import { Alert, ALERT_INFO } from './components/Alert'

import App from './App'

describe('App.js', () => {
  afterEach(() => {
    window.location.href = ''
  })

  it('renders the Idle Timer', () => {
    const wrapper = shallow(<App />)
    expect(wrapper.find(IdleTimer)).toExist()
  })

  it('renders the Gov Banner', () => {
    const wrapper = shallow(<App />)
    expect(wrapper.find(GovBanner)).toExist()
  })

  it('renders the Header', () => {
    const wrapper = shallow(<App />)
    expect(wrapper.find(Header)).toExist()
  })

  it('renders the Alert', () => {
    const wrapper = shallow(<App />)
    expect(wrapper.find(Alert)).toExist()
  })

  it('should redirect to #main-content when space bar is pressed on "skip links" element', () => {
    const url = '#main-content'

    global.window = Object.create(window)
    Object.defineProperty(window, 'location', {
      value: {
        href: url,
      },
    })

    const wrapper = shallow(<App />)

    const skipLink = wrapper.find('.usa-skipnav')
    skipLink.simulate('keyPress', {
      charCode: 32,
    })

    expect(window.location.href).toEqual(url)
  })

  it('should do nothing if any key besides space bar is pressed', () => {
    const url = ''

    global.window = Object.create(window)
    Object.defineProperty(window, 'location', {
      value: {
        href: url,
      },
    })

    const wrapper = shallow(<App />)

    const skipLink = wrapper.find('.usa-skipnav')
    skipLink.simulate('keyPress', {
      charCode: 25,
    })

    expect(window.location.href).toEqual(url)
  })
})
