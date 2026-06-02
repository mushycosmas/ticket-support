import React, { useEffect, useState } from "react";
import { Card, Row, Col, Table, Badge, Spinner } from "react-bootstrap";
import { getTickets } from "../api/ticketApi";

const Dashboard = () => {
    const [tickets, setTickets] = useState([]);
    const [loading, setLoading] = useState(true);

    const loadTickets = async () => {
        try {
            setLoading(true);

            const response = await getTickets();
            setTickets(response.data);

        } catch (error) {
            console.error("Error loading dashboard data", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadTickets();
    }, []);

    // -------------------------
    // STATS CALCULATION
    // -------------------------
    const total = tickets.length;
    const open = tickets.filter(t => t.status === "OPEN").length;
    const assigned = tickets.filter(t => t.status === "ASSIGNED").length;
    const resolved = tickets.filter(t => t.status === "RESOLVED").length;

    const getBadge = (status) => {
        switch (status) {
            case "OPEN":
                return <Badge bg="secondary">OPEN</Badge>;
            case "ASSIGNED":
                return <Badge bg="info">ASSIGNED</Badge>;
            case "IN_PROGRESS":
                return <Badge bg="warning">IN PROGRESS</Badge>;
            case "RESOLVED":
                return <Badge bg="success">RESOLVED</Badge>;
            case "CLOSED":
                return <Badge bg="dark">CLOSED</Badge>;
            default:
                return <Badge bg="light">{status}</Badge>;
        }
    };

    return (
        <div className="container-fluid mt-4">

            {/* HEADER */}
            <h3 className="mb-4">Ticket Support Dashboard</h3>

            {/* STATS CARDS */}
            <Row className="mb-4">

                <Col md={3}>
                    <Card className="text-center shadow-sm">
                        <Card.Body>
                            <h5>Total Tickets</h5>
                            <h2>{total}</h2>
                        </Card.Body>
                    </Card>
                </Col>

                <Col md={3}>
                    <Card className="text-center shadow-sm">
                        <Card.Body>
                            <h5>Open</h5>
                            <h2>{open}</h2>
                        </Card.Body>
                    </Card>
                </Col>

                <Col md={3}>
                    <Card className="text-center shadow-sm">
                        <Card.Body>
                            <h5>Assigned</h5>
                            <h2>{assigned}</h2>
                        </Card.Body>
                    </Card>
                </Col>

                <Col md={3}>
                    <Card className="text-center shadow-sm">
                        <Card.Body>
                            <h5>Resolved</h5>
                            <h2>{resolved}</h2>
                        </Card.Body>
                    </Card>
                </Col>

            </Row>

            {/* RECENT TICKETS */}
            <Card className="shadow-sm">
                <Card.Header>
                    <h5 className="mb-0">Recent Tickets</h5>
                </Card.Header>

                <Card.Body>

                    {loading ? (
                        <div className="text-center py-4">
                            <Spinner animation="border" />
                        </div>
                    ) : (

                        <Table striped bordered hover responsive>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Customer</th>
                                    <th>Title</th>
                                    <th>Status</th>
                                    <th>Priority</th>
                                    <th>Created</th>
                                </tr>
                            </thead>

                            <tbody>
                                {tickets.slice(0, 5).map(ticket => (
                                    <tr key={ticket.id}>
                                        <td>{ticket.id}</td>
                                        <td>{ticket.customer_name}</td>
                                        <td>{ticket.title}</td>
                                        <td>{getBadge(ticket.status)}</td>
                                        <td>{ticket.priority}</td>
                                        <td>
                                            {new Date(ticket.created_at).toLocaleString()}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>

                        </Table>

                    )}

                </Card.Body>
            </Card>

        </div>
    );
};

export default Dashboard;