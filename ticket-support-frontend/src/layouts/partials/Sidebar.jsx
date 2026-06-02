import React from "react";
import { Nav } from "react-bootstrap";
import { Link } from "react-router-dom";

const Sidebar = () => {
    return (
        <div
            className="bg-white border-end p-3"
            style={{ width: "250px" }}
        >
            <h5 className="mb-3">Menu</h5>

            <Nav className="flex-column">

                <Nav.Link as={Link} to="/">
                    Dashboard
                </Nav.Link>

                <Nav.Link as={Link} to="/tickets">
                    Tickets
                </Nav.Link>

                <Nav.Link as={Link} to="/admin/users">
                    Users
                </Nav.Link>

                <Nav.Link as={Link} to="/admin/teams">
                    Teams
                </Nav.Link>

            </Nav>
        </div>
    );
};

export default Sidebar;