import React from "react";
import { Navbar, Container } from "react-bootstrap";

const Header = () => {
    return (
        <Navbar bg="dark" variant="dark" className="px-3">
            <Container fluid>
                <Navbar.Brand>
                    🎫 Ticket Support System
                </Navbar.Brand>
            </Container>
        </Navbar>
    );
};

export default Header;