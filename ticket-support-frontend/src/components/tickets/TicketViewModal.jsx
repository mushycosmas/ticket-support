import React from "react";
import { Modal, Form, Badge } from "react-bootstrap";
import AssignTicketForm from "./AssignTicketForm";

const TicketViewModal = ({ show, onHide, ticket, onRefresh }) => {

    if (!ticket) return null;

    return (
        <Modal show={show} onHide={onHide} size="lg">

            <Modal.Header closeButton>
                <Modal.Title>
                    Ticket #{ticket.id}
                </Modal.Title>
            </Modal.Header>

            <Modal.Body>

                <Form>

                    <Form.Control
                        className="mb-2"
                        value={ticket.customer_name}
                        disabled
                    />

                    <Form.Control
                        className="mb-2"
                        value={ticket.customer_contact}
                        disabled
                    />

                    <Form.Control
                        className="mb-2"
                        value={ticket.title}
                        disabled
                    />

                    <Form.Control
                        as="textarea"
                        rows={3}
                        value={ticket.description}
                        disabled
                    />

                    <div className="mt-3">
                        <Badge bg="info">{ticket.status}</Badge>{" "}
                        <Badge bg="warning">{ticket.priority}</Badge>
                    </div>

                </Form>

                {/* ASSIGN SECTION */}
                <AssignTicketForm
                    ticketId={ticket.id}
                    onSuccess={onRefresh}
                />

            </Modal.Body>

        </Modal>
    );
};

export default TicketViewModal;