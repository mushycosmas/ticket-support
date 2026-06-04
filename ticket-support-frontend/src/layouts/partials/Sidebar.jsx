import React from "react";
import { Nav, Button } from "react-bootstrap";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
    House,
    TicketDetailed,
    Person,
    People,
    PersonWorkspace,
    Folder,
    Flag,
    Book,
    BarChart,
    Gear,
    Database,
    BoxArrowRight,
} from "react-bootstrap-icons";

const Sidebar = () => {
    const navigate = useNavigate();
    const location = useLocation();

    const user = JSON.parse(localStorage.getItem("user"));
    const role = user?.role;

    const handleLogout = () => {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        navigate("/login");
    };

    const isActive = (path) => location.pathname === path;

    return (
        <div
            className="bg-white border-end d-flex flex-column justify-content-between p-3"
            style={{
                width: "280px",
                height: "100vh",
                overflowY: "auto",
            }}
        >
            <div>
                {/* LOGO */}
                <div className="mb-4 pb-3 border-bottom">
                    <h4 className="fw-bold text-primary">
                        SupportFlow
                    </h4>
                    <small className="text-muted">
                        Ticket Support System
                    </small>
                </div>

                {/* ==================== */}
                {/* DASHBOARD */}
                {/* ==================== */}
                <div className="text-uppercase text-muted small fw-bold mb-2">
                    Dashboard
                </div>

                <Nav className="flex-column mb-3">
                    <Nav.Link
                        as={Link}
                        to="/dashboard"
                        active={isActive("/dashboard")}
                    >
                        <House className="me-2" />
                        Dashboard
                    </Nav.Link>
                </Nav>

                {/* ==================== */}
                {/* TICKETS */}
                {/* ==================== */}
                <div className="text-uppercase text-muted small fw-bold mb-2">
                    Tickets
                </div>

                <Nav className="flex-column mb-3">
                <Nav.Link as={Link} to="/tickets">
                    <TicketDetailed className="me-2" />
                    All Tickets
                </Nav.Link>

                <Nav.Link as={Link} to="/tickets/my">
                    <Person className="me-2" />
                    My Tickets
                </Nav.Link>

                <Nav.Link as={Link} to="/tickets/assigned">
                    <PersonWorkspace className="me-2" />
                    Assigned Tickets
                </Nav.Link>

                <Nav.Link as={Link} to="/tickets/unassigned">
                    <People className="me-2" />
                    Unassigned Tickets
                </Nav.Link>

                <Nav.Link as={Link} to="/tickets/open">
                    <Folder className="me-2" />
                    Open Tickets
                </Nav.Link>

                <Nav.Link as={Link} to="/tickets/in-progress">
                    <Folder className="me-2" />
                    In Progress Tickets
                </Nav.Link>

                <Nav.Link as={Link} to="/tickets/resolved">
                    <Folder className="me-2" />
                    Resolved Tickets
                </Nav.Link>

                <Nav.Link as={Link} to="/tickets/closed">
                    <Folder className="me-2" />
                    Closed Tickets
                </Nav.Link>
            </Nav>
                {/* ==================== */}
                {/* ADMIN */}
                {/* ==================== */}
                {role === "ADMIN" && (
                    <>
                        <div className="text-uppercase text-muted small fw-bold mb-2">
                            Management
                        </div>

                        <Nav className="flex-column mb-3">
                             <Nav.Link as={Link} to="/admin/roles">
                                <Person className="me-2" />
                                Roles
                            </Nav.Link>
                            
                            <Nav.Link as={Link} to="/admin/users">
                                <Person className="me-2" />
                                Users
                            </Nav.Link>

                            <Nav.Link as={Link} to="/admin/teams">
                                <People className="me-2" />
                                Teams
                            </Nav.Link>

                            <Nav.Link as={Link} to="/admin/categories">
                                <Folder className="me-2" />
                                Categories
                            </Nav.Link>

                            <Nav.Link as={Link} to="/admin/priorities">
                                <Flag className="me-2" />
                                Priorities
                            </Nav.Link>

                            {/* <Nav.Link as={Link} to="/admin/knowledge-base">
                                <Book className="me-2" />
                                Knowledge Base
                            </Nav.Link> */}
                        </Nav>

                         <div className="text-uppercase text-muted small fw-bold mb-2">
                            Locations
                        </div>

                        <Nav className="flex-column mb-3">
                            <Nav.Link as={Link} to="/admin/locations/regions">
                                <Database className="me-2" />
                                Regions
                            </Nav.Link>

                            <Nav.Link as={Link} to="/admin/locations/districts">
                                <Database className="me-2" />
                                Districts
                            </Nav.Link>

                            <Nav.Link as={Link} to="/admin/locations/wards">
                                <Database className="me-2" />
                                Wards
                            </Nav.Link>
                        </Nav>
                    </>
                )}

                {/* ==================== */}
                {/* TEAM LEAD */}
                {/* ==================== */}
                {role === "TEAM_LEAD" && (
                    <>
                        <div className="text-uppercase text-muted small fw-bold mb-2">
                            Team Management
                        </div>

                        <Nav className="flex-column mb-3">
                            <Nav.Link as={Link} to="/team/tickets">
                                <TicketDetailed className="me-2" />
                                Team Tickets
                            </Nav.Link>

                            <Nav.Link as={Link} to="/team/agents">
                                <People className="me-2" />
                                Agents
                            </Nav.Link>
                        </Nav>
                    </>
                )}

                {/* ==================== */}
                {/* REPORTS */}
                {/* ==================== */}
                {(role === "ADMIN" || role === "TEAM_LEAD") && (
                    <>
                        <div className="text-uppercase text-muted small fw-bold mb-2">
                            Reports
                        </div>

                        <Nav className="flex-column mb-3">
                            <Nav.Link as={Link} to="/reports">
                                <BarChart className="me-2" />
                                Reports
                            </Nav.Link>

                            <Nav.Link as={Link} to="/analytics">
                                <BarChart className="me-2" />
                                Analytics
                            </Nav.Link>
                        </Nav>
                    </>
                )}

                {/* ==================== */}
                {/* SETTINGS */}
                {/* ==================== */}
                {role === "ADMIN" && (
                    <>
                        <div className="text-uppercase text-muted small fw-bold mb-2">
                            System
                        </div>

                        <Nav className="flex-column">
                            <Nav.Link as={Link} to="/settings">
                                <Gear className="me-2" />
                                Settings
                            </Nav.Link>

                            <Nav.Link as={Link} to="/logs">
                                <Database className="me-2" />
                                System Logs
                            </Nav.Link>
                        </Nav>
                    </>
                )}
            </div>

            {/* USER & LOGOUT */}
            <div className="border-top pt-3">
                <div className="mb-3">
                    <strong>{user?.username}</strong>
                    <br />
                    <small className="text-muted">
                        {role}
                    </small>
                </div>

                <Button
                    variant="danger"
                    className="w-100"
                    onClick={handleLogout}
                >
                    <BoxArrowRight className="me-2" />
                    Logout
                </Button>
            </div>
        </div>
    );
};

export default Sidebar;