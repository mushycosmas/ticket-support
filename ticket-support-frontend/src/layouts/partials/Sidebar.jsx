import React from "react";
import { Nav, Button } from "react-bootstrap";
import { Link, useNavigate } from "react-router-dom";

const Sidebar = () => {

    const navigate = useNavigate();

    const user = JSON.parse(localStorage.getItem("user"));
    const role = user?.role;

    const handleLogout = () => {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        navigate("/login");
    };

    return (
        <div
            className="bg-white border-end p-3 d-flex flex-column justify-content-between"
            style={{ width: "250px", height: "100vh" }}
        >

            {/* MENU */}
            <div>

                <h5 className="mb-3">Menu</h5>

                <Nav className="flex-column">

                    {/* ALL LOGGED USERS */}
                    <Nav.Link as={Link} to="/dashboard">
                        Dashboard
                    </Nav.Link>

                    <Nav.Link as={Link} to="/tickets">
                        Tickets
                    </Nav.Link>

                    {/* ===================== */}
                    {/* ADMIN ONLY */}
                    {/* ===================== */}
                    {role === "ADMIN" && (
                        <>
                            <Nav.Link as={Link} to="/admin/users">
                                Users
                            </Nav.Link>

                            <Nav.Link as={Link} to="/admin/teams">
                                Teams
                            </Nav.Link>
                        </>
                    )}

                    {/* ===================== */}
                    {/* TEAM LEAD ONLY */}
                    {/* ===================== */}
                    {role === "TEAM_LEAD" && (
                        <>
                            <Nav.Link as={Link} to="/tickets">
                                Team Tickets
                            </Nav.Link>
                        </>
                    )}

                    {/* ===================== */}
                    {/* AGENT ONLY */}
                    {/* ===================== */}
                    {role === "AGENT" && (
                        <>
                            <Nav.Link as={Link} to="/tickets">
                                My Tickets
                            </Nav.Link>
                        </>
                    )}

                </Nav>

            </div>

            {/* LOGOUT */}
            <div className="pt-3 border-top">

                <Button
                    variant="danger"
                    className="w-100"
                    onClick={handleLogout}
                >
                    Logout
                </Button>

            </div>

        </div>
    );
};

export default Sidebar;