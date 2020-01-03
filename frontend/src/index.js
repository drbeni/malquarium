import React from 'react';
import ReactDOM from 'react-dom';
import {Provider} from 'react-redux';
import {createBrowserHistory} from 'history';
import {ConnectedRouter, routerMiddleware} from 'connected-react-router'
import {applyMiddleware, createStore} from 'redux';
import {Route, Switch} from 'react-router-dom';
import promise from 'redux-promise';
import thunk from 'redux-thunk';

import reducers from './reducers';
import Login from './containers/login';
import Logout from './containers/logout';
import IndexView from './components/index_view';
import AccountView from './components/account_view';
import SampleListView from './components/sample_list_view';
import DetailView from './components/detail_view';
import UploadView from './components/upload_view';
import Footer from './components/footer'

import './css/malquarium.css';
import './css/autocomplete.css';

const history = createBrowserHistory();


const store = createStore(
  reducers(history),
  applyMiddleware(thunk, promise, routerMiddleware(history))
);


ReactDOM.render(
  <Provider store={store}>
    <div>
      <ConnectedRouter history={history}>
        <div className="content">
          <Switch>
            <Route exact path="/login/" component={Login}/>
            <Route exact path="/logout/" component={Logout}/>
            <Route exact path="/profile/" component={AccountView}/>
            <Route path="/samples/:sha2" component={DetailView}/>
            <Route exact path="/samples/" component={SampleListView}/>
            <Route exact path="/upload/" component={UploadView}/>
            <Route path="/" component={IndexView}/>
          </Switch>
        </div>
      </ConnectedRouter>
      <Footer history={history}/>
    </div>
  </Provider>
  , document.getElementById('root'));
