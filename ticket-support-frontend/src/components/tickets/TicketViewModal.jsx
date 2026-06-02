import React from "react";
import { Modal, Form, Badge, Row, Col } from "react-bootstrap";
import AssignTicketForm from "./AssignTicketForm";

const TicketViewModal = ({ show, onHide, ticket, onRefresh }) => {

    if (!ticket) return null;

    const user = JSON.parse(localStorage.getItem("user"));

    const canAssign = user?.role === "ADMIN" || user?.role === "TEAM_LEAD";

    return (
        <Modal show={show} onHide={onHide} size="lg" centered>

            {/* HEADER */}
            <Modal.Header closeButton>
                <Modal.Title>
                    Ticket #{ticket.id}
                </Modal.Title>
            </Modal.Header>

            <Modal.Body>

                {/* CUSTOMER INFO */}
                <Form>

                    <Form.Group className="mb-2">
                        <Form.Label>Customer Name</Form.Label>
                        <Form.Control value={ticket.customer_name || "-"} disabled />
                    </Form.Group>

                    <Form.Group className="mb-2">
                        <Form.Label>Contact</Form.Label>
                        <Form.Control value={ticket.customer_contact || "-"} disabled />
                    </Form.Group>

                    <Form.Group className="mb-2">
                        <Form.Label>Title</Form.Label>
                        <Form.Control value={ticket.title || "-"} disabled />
                    </Form.Group>

                    <Form.Group className="mb-2">
                        <Form.Label>Description</Form.Label>
                        <Form.Control
                            as="textarea"
                            rows={3}
                            value={ticket.description || "-"}
                            disabled
                        />
                    </Form.Group>

                </Form>

                {/* WORKFLOW INFO */}
                <Row className="mt-3">

                    <Col>
                        <strong>Status:</strong><br />
                        <Badge bg="info">{ticket.status || "OPEN"}</Badge>
                    </Col>

                    <Col>
                        <strong>Priority:</strong><br />
                        <Badge bg="warning">{ticket.priority || "MEDIUM"}</Badge>
                    </Col>

                    <Col>
                        <strong>Team:</strong><br />
                        <Badge bg="secondary">
                            {ticket.team_name || `Team #${ticket.team_id}` || "Unassigned"}
                        </Badge>
                    </Col>

                    <Col>
                        <strong>Assigned Agent:</strong><br />
                        <Badge bg="dark">
                            {ticket.assigned_to_name || `Agent #${ticket.assigned_to_id}` || "Unassigned"}
                        </Badge>
                    </Col>

                </Row>

                {/* ===================== */}
                {/* ASSIGN SECTION (FIXED) */}
                {/* ===================== */}
                <hr />

                {canAssign && (
                    <AssignTicketForm
                        ticket={ticket}
                        ticketId={ticket.id}
                        onSuccess={onRefresh}
                        onClose={onHide}
                    />
                )}

            </Modal.Body>

        </Modal>
    );
};

export default TicketViewModal;