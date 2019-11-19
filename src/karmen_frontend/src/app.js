import React from 'react';
import { connect } from 'react-redux';
import { BrowserRouter, Switch, Route } from 'react-router-dom';

import Menu from './components/menu';
import Heartbeat from './components/heartbeat';
import LoginGateway from './components/login-gateway';
import Loader from './components/loader';

import PrinterList from './routes/printer-list';
import GcodeList from './routes/gcode-list'
import GcodeDetail from './routes/gcode-detail';
import PrinterDetail from './routes/printer-detail';
import AddPrinter from './routes/add-printer';
import AddGcode from './routes/add-gcode';
import Settings from './routes/settings';
import UserPreferences from './routes/user-preferences';

import { loadUserState } from './actions/users';

import { registerAccessTokenExpirationHandler, deregisterAccessTokenExpirationHandler } from './services/backend';

class App extends React.Component {
  
  constructor(props) {
    super(props);
    this.state = {
      initialized: false,
    }
  }

  componentDidMount() {
    const { loadUser } = this.props;
    const { initialized } = this.state;
    if (!initialized) {
      loadUser()
        .then(() => {
          this.setState({
            initialized: true,
          });
        });
      registerAccessTokenExpirationHandler();
    }
  }

  componentWillUnmount() {
    deregisterAccessTokenExpirationHandler();
  }

  render () {
    const { loadUser } = this.props;
    const { initialized } = this.state;
    if (!initialized) {
      return (<div><Loader /></div>);
    }
    return (
      <>
        <BrowserRouter>
          <Menu />
          <main>
            <LoginGateway onUserStateChanged={loadUser}>
              <Switch>
                <Route path="/add-printer" exact component={AddPrinter} />
                <Route path="/add-gcode" exact component={AddGcode} />
                <Route path="/settings" exact component={Settings} />
                <Route path="/users/me" exact component={UserPreferences} />
                <Route path="/gcodes" exact component={GcodeList} />
                <Route path="/gcodes/:id" exact component={GcodeDetail} />
                <Route path="/printers/:host" exact component={PrinterDetail} />
                <Route path="/" exact component={PrinterList} />
              </Switch>
            </LoginGateway>
            <Heartbeat />
          </main>
        </BrowserRouter>
        <footer>
          <section>
            &copy; {(new Date()).getFullYear()}
            <a href="https://fragaria.cz" target="_blank" rel="noopener noreferrer">Fragaria s.r.o.</a>
          </section>
          <section>
            <a href="https://github.com/fragaria/karmen/blob/master/LICENSE.txt" target="_blank" rel="noopener noreferrer">License</a>
            <a href="https://github.com/fragaria/karmen" target="_blank" rel="noopener noreferrer">Source</a>
            <a href={`https://github.com/fragaria/karmen/releases/tag/${process.env.REACT_APP_GIT_REV}`} target="_blank" rel="noopener noreferrer">{process.env.REACT_APP_GIT_REV}</a>
          </section>
        </footer>
      </>
    );
  }
}

export default connect(
  null,
  dispatch => ({
    loadUser: () => (dispatch(loadUserState()))
  })
)(App);
