import React, { useEffect, useState } from "react";
import { Card, Row, Col, Table, Badge, Spinner } from "react-bootstrap";
import { getTickets } from "../api/ticketApi";

const Dashboard = () => {

    const [tickets, setTickets] = useState([]);
    const [loading, setLoading] = useState(true);

    // =========================
    // LOAD DATA
    // =========================
    const loadTickets = async () => {
        try {
            setLoading(true);
            const response = await getTickets();
            setTickets(response.data || []);
        } catch (error) {
            console.error("Error loading dashboard data", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadTickets();
    }, []);

    // =========================
    // SAFE FILTERS
    // =========================
    const total = tickets.length;

    const open = tickets.filter(t => t.status === "OPEN").length;

    const inProgress = tickets.filter(t => t.status === "IN_PROGRESS").length;

    const resolved = tickets.filter(t => t.status === "RESOLVED").length;

    const closed = tickets.filter(t => t.status === "CLOSED").length;

    const unassigned = tickets.filter(t => !t.assigned_to_id).length;

    // =========================
    // BADGES
    // =========================
    const getStatusBadge = (status) => {
        switch (status) {
            case "OPEN":
                return <Badge bg="secondary">OPEN</Badge>;
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

    const getPriorityBadge = (priority) => {
        switch (priority) {
            case "HIGH":
                return <Badge bg="danger">HIGH</Badge>;
            case "MEDIUM":
                return <Badge bg="warning">MEDIUM</Badge>;
            case "LOW":
                return <Badge bg="success">LOW</Badge>;
            default:
                return <Badge bg="secondary">{priority}</Badge>;
        }
    };

    return (
        <div className="container-fluid mt-4">

            {/* HEADER */}
            <h3 className="mb-4">Ticket Support Dashboard</h3>

            {/* =========================
                STATS
            ========================= */}
            <Row className="mb-4">

                <Col md={2}>
                    <Card className="text-center shadow-sm">
                        <Card.Body>
                            <h6>Total</h6>
                            <h3>{total}</h3>
                        </Card.Body>
                    </Card>
                </Col>

                <Col md={2}>
                    <Card className="text-center shadow-sm">
                        <Card.Body>
                            <h6>Open</h6>
                            <h3>{open}</h3>
                        </Card.Body>
                    </Card>
                </Col>

                <Col md={2}>
                    <Card className="text-center shadow-sm">
                        <Card.Body>
                            <h6>In Progress</h6>
                            <h3>{inProgress}</h3>
                        </Card.Body>
                    </Card>
                </Col>

                <Col md={2}>
                    <Card className="text-center shadow-sm">
                        <Card.Body>
                            <h6>Resolved</h6>
                            <h3>{resolved}</h3>
                        </Card.Body>
                    </Card>
                </Col>

                <Col md={2}>
                    <Card className="text-center shadow-sm">
                        <Card.Body>
                            <h6>Closed</h6>
                            <h3>{closed}</h3>
                        </Card.Body>
                    </Card>
                </Col>

                <Col md={2}>
                    <Card className="text-center shadow-sm">
                        <Card.Body>
                            <h6>Unassigned</h6>
                            <h3>{unassigned}</h3>
                        </Card.Body>
                    </Card>
                </Col>

            </Row>

            {/* =========================
                RECENT TICKETS
            ========================= */}
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
                                    <th>Channel</th>
                                    <th>Assigned</th>
                                    <th>Created</th>
                                </tr>
                            </thead>

                            <tbody>
                                {tickets.slice(0, 8).map(ticket => (
                                    <tr key={ticket.id}>

                                        <td>{ticket.id}</td>

                                        <td>
                                            <div>
                                                <strong>{ticket.customer_name}</strong>
                                                <div style={{ fontSize: "12px", color: "#666" }}>
                                                    {ticket.customer_contact}
                                                </div>
                                            </div>
                                        </td>

                                        <td>{ticket.title}</td>

                                        <td>{getStatusBadge(ticket.status)}</td>

                                        <td>{getPriorityBadge(ticket.priority)}</td>

                                        <td>
                                            <Badge bg="info">{ticket.channel}</Badge>
                                        </td>

                                        <td>
                                            {ticket.assigned_to_id
                                                ? <Badge bg="success">Assigned</Badge>
                                                : <Badge bg="danger">Unassigned</Badge>
                                            }
                                        </td>

                                        <td>
                                            {ticket.created_at
                                                ? new Date(ticket.created_at).toLocaleString()
                                                : "-"
                                            }
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