import React from "react";
import { connect } from "react-redux";
import { Link } from "react-router-dom";
import { Tab, Tabs, TabList, TabPanel } from "react-tabs";

import SetActiveOrganization from "../components/gateways/set-active-organization";
import OrgRoleBasedGateway from "../components/gateways/org-role-based-gateway";
import FreshTokenGateway from "../components/gateways/fresh-token-gateway";
import NetworkScan from "../components/forms/network-scan";
import PrintersTable from "../components/listings/printers-table";
import UsersTable from "../components/listings/users-table";
import { addUser, getUsers, patchUser, deleteUser } from "../actions/users";
import { enqueueTask } from "../actions/misc";
import { setNetworkInterface } from "../actions/preferences";
import { loadPrinters, deletePrinter } from "../actions/printers";

const Settings = ({
  match,
  currentUuid,
  loadUsers,
  usersLoaded,
  usersList,
  onUserDelete,
  onUserChange,
  onResendInvitation,
  loadPrinters,
  printersList,
  printersLoaded,
  onPrinterDelete,
  networkInterface,
  onNetworkInterfaceChange,
  scanNetwork
}) => {
  return (
    <>
      <SetActiveOrganization />
      <OrgRoleBasedGateway requiredRole="admin">
        <FreshTokenGateway>
          <div className="content">
            <div className="container">
              <h1 className="main-title">Settings</h1>
            </div>

            <Tabs>
              <TabList>
                <Tab>Printers</Tab>
                <Tab>Users</Tab>
              </TabList>

              <TabPanel>
                <div className="container">
                  <div className="react-tabs__tab-panel__header">
                    <h1 className="react-tabs__tab-panel__header__title">
                      Printers
                    </h1>
                    <Link
                      to={`/${match.params.orgslug}/add-printer`}
                      className="btn btn-sm"
                    >
                      <span>+ Add a printer</span>
                    </Link>
                  </div>
                </div>
                <PrintersTable
                  orgslug={match.params.orgslug}
                  loadPrinters={loadPrinters}
                  printersList={printersList}
                  printersLoaded={printersLoaded}
                  onPrinterDelete={onPrinterDelete}
                />

                <div className="container">
                  <br />
                  <br />
                  <strong>Network scan</strong>
                  <NetworkScan
                    networkInterface={networkInterface}
                    onNetworkInterfaceChange={onNetworkInterfaceChange}
                    scanNetwork={scanNetwork}
                  />
                </div>
              </TabPanel>

              <TabPanel>
                <div className="container">
                  <div className="react-tabs__tab-panel__header">
                    <h1 className="react-tabs__tab-panel__header__title">
                      Users
                    </h1>
                    <Link
                      to={`/${match.params.orgslug}/add-user`}
                      className="btn btn-sm"
                    >
                      <span>+ Add a user</span>
                    </Link>
                  </div>
                </div>

                <UsersTable
                  currentUuid={currentUuid}
                  loadUsers={loadUsers}
                  usersList={usersList}
                  usersLoaded={usersLoaded}
                  onUserDelete={onUserDelete}
                  onUserChange={onUserChange}
                  onResendInvitation={onResendInvitation}
                />
              </TabPanel>
            </Tabs>
          </div>
        </FreshTokenGateway>
      </OrgRoleBasedGateway>
    </>
  );
};

export default connect(
  state => ({
    usersList: state.users.list,
    usersLoaded: state.users.listLoaded,
    printersList: state.printers.printers,
    printersLoaded: state.printers.printersLoaded,
    currentUuid: state.users.me.identity,
    networkInterface: state.preferences.networkInterface
  }),
  (dispatch, ownProps) => ({
    loadPrinters: fields =>
      dispatch(loadPrinters(ownProps.match.params.orgslug, fields)),
    onPrinterDelete: uuid =>
      dispatch(deletePrinter(ownProps.match.params.orgslug, uuid)),
    loadUsers: fields =>
      dispatch(getUsers(ownProps.match.params.orgslug, fields)),
    onUserChange: (uuid, role) =>
      dispatch(patchUser(ownProps.match.params.orgslug, uuid, role)),
    onUserDelete: uuid =>
      dispatch(deleteUser(ownProps.match.params.orgslug, uuid)),
    onResendInvitation: (email, role) =>
      dispatch(addUser(ownProps.match.params.orgslug, email, role)),
    onNetworkInterfaceChange: networkInterface =>
      dispatch(setNetworkInterface(networkInterface)),
    scanNetwork: networkInterface =>
      dispatch(
        enqueueTask(ownProps.match.params.orgslug, "scan_network", {
          network_interface: networkInterface
        })
      )
  })
)(Settings);
