import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
    Card,
    Badge,
    Button,
    Spinner,
    Form,
    Row,
    Col
} from "react-bootstrap";

import {
    getTicket,
    assignTicket,
    resolveTicket,
    closeTicket
} from "../api/ticketApi";

const TicketDetails = () => {

    const { id } = useParams();

    const [ticket, setTicket] = useState(null);
    const [loading, setLoading] = useState(true);
    const [agent, setAgent] = useState("");

    // -------------------------
    // LOAD SINGLE TICKET
    // -------------------------
    const loadTicket = async () => {
        try {
            setLoading(true);

            const res = await getTicket(id);
            setTicket(res.data);

        } catch (error) {
            console.error("Error loading ticket", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadTicket();
    }, [id]);

    // -------------------------
    // ACTIONS
    // -------------------------
    const handleAssign = async () => {
        if (!agent) return alert("Enter agent name");

        await assignTicket(id, agent);
        loadTicket();
        setAgent("");
    };

    const handleResolve = async () => {
        await resolveTicket(id);
        loadTicket();
    };

    const handleClose = async () => {
        await closeTicket(id);
        loadTicket();
    };

    // -------------------------
    // STATUS BADGE
    // -------------------------
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

    // -------------------------
    // LOADING
    // -------------------------
    if (loading) {
        return (
            <div className="text-center mt-5">
                <Spinner animation="border" />
            </div>
        );
    }

    if (!ticket) {
        return <p className="text-center">Ticket not found</p>;
    }

    return (
        <div className="container mt-4">

            {/* HEADER */}
            <Card className="mb-3">
                <Card.Body>

                    <h4>
                        Ticket #{ticket.id} {" "}
                        {getBadge(ticket.status)}
                    </h4>

                    <p><b>Title:</b> {ticket.title}</p>
                    <p><b>Description:</b> {ticket.description}</p>

                    <p>
                        <b>Customer:</b> {ticket.customer_name} <br />
                        <b>Contact:</b> {ticket.customer_contact}
                    </p>

                    <p>
                        <b>Priority:</b> {ticket.priority}
                    </p>

                    <p>
                        <b>Channel:</b> {ticket.channel}
                    </p>

                    <p>
                        <b>Assigned To:</b>{" "}
                        {ticket.assigned_to || "Not assigned"}
                    </p>

                </Card.Body>
            </Card>

            {/* ACTIONS */}
            <Card className="mb-3">
                <Card.Body>

                    <h5>Actions</h5>

                    <Row>
                        <Col md={6}>
                            <Form.Control
                                placeholder="Assign agent name"
                                value={agent}
                                onChange={(e) =>
                                    setAgent(e.target.value)
                                }
                            />
                        </Col>

                        <Col md={6}>
                            <Button
                                variant="primary"
                                className="me-2"
                                onClick={handleAssign}
                            >
                                Assign
                            </Button>

                            <Button
                                variant="success"
                                className="me-2"
                                onClick={handleResolve}
                            >
                                Resolve
                            </Button>

                            <Button
                                variant="dark"
                                onClick={handleClose}
                            >
                                Close
                            </Button>
                        </Col>
                    </Row>

                </Card.Body>
            </Card>

        </div>
    );
};

export default TicketDetails;