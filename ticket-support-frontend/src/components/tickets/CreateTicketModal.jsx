import React, { useState } from "react";
import { Modal, Form, Button } from "react-bootstrap";
import { createTicket } from "../../api/ticketApi";

const CreateTicketModal = ({ show, onHide, onSuccess }) => {

    const [formData, setFormData] = useState({
        customer_name: "",
        customer_contact: "",
        channel: "WEB",
        title: "",
        description: "",
        priority: "MEDIUM"
    });

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async () => {
        await createTicket(formData);
        onSuccess();
        onHide();
    };

    return (
        <Modal show={show} onHide={onHide} size="lg">

            <Modal.Header closeButton>
                <Modal.Title>Create Ticket</Modal.Title>
            </Modal.Header>

            <Modal.Body>

                <Form>

                    <Form.Control
                        className="mb-2"
                        name="customer_name"
                        placeholder="Customer Name"
                        onChange={handleChange}
                    />

                    <Form.Control
                        className="mb-2"
                        name="customer_contact"
                        placeholder="Contact"
                        onChange={handleChange}
                    />

                    <Form.Select
                        className="mb-2"
                        name="channel"
                        onChange={handleChange}
                    >
                        <option value="WEB">WEB</option>
                        <option value="EMAIL">EMAIL</option>
                        <option value="PHONE">PHONE</option>
                        <option value="CHAT">CHAT</option>
                        <option value="WALKIN">WALK-IN</option>
                    </Form.Select>

                    <Form.Control
                        className="mb-2"
                        name="title"
                        placeholder="Title"
                        onChange={handleChange}
                    />

                    <Form.Control
                        as="textarea"
                        rows={3}
                        name="description"
                        placeholder="Description"
                        onChange={handleChange}
                    />

                    <Form.Select
                        className="mt-2"
                        name="priority"
                        onChange={handleChange}
                    >
                        <option value="LOW">LOW</option>
                        <option value="MEDIUM">MEDIUM</option>
                        <option value="HIGH">HIGH</option>
                        <option value="CRITICAL">CRITICAL</option>
                    </Form.Select>

                </Form>

            </Modal.Body>

            <Modal.Footer>
                <Button variant="secondary" onClick={onHide}>
                    Cancel
                </Button>

                <Button variant="primary" onClick={handleSubmit}>
                    Create
                </Button>
            </Modal.Footer>

        </Modal>
    );
};

export default CreateTicketModal;