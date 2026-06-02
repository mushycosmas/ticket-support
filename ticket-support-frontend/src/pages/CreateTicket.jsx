import React, { useState } from "react";
import { Card, Form, Button, Row, Col, Alert, Spinner } from "react-bootstrap";
import { createTicket } from "../api/ticketApi";

const CreateTicket = () => {

    const [formData, setFormData] = useState({
        customer_name: "",
        customer_contact: "",
        channel: "WEB",
        title: "",
        description: "",
        priority: "MEDIUM"
    });

    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null);
    const [error, setError] = useState(null);

    // -------------------------
    // HANDLE INPUT CHANGE
    // -------------------------
    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    // -------------------------
    // SUBMIT TICKET
    // -------------------------
    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            setLoading(true);
            setError(null);
            setMessage(null);

            await createTicket(formData);

            setMessage("Ticket created successfully!");

            // reset form
            setFormData({
                customer_name: "",
                customer_contact: "",
                channel: "WEB",
                title: "",
                description: "",
                priority: "MEDIUM"
            });

        } catch (err) {
            console.error(err);
            setError(
                err.response?.data ||
                "Failed to create ticket"
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container mt-4">

            <Card>
                <Card.Body>

                    <h4>Create Support Ticket</h4>

                    {message && (
                        <Alert variant="success">{message}</Alert>
                    )}

                    {error && (
                        <Alert variant="danger">
                            {JSON.stringify(error)}
                        </Alert>
                    )}

                    <Form onSubmit={handleSubmit}>

                        {/* CUSTOMER INFO */}
                        <Row>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Customer Name</Form.Label>
                                    <Form.Control
                                        name="customer_name"
                                        value={formData.customer_name}
                                        onChange={handleChange}
                                        required
                                    />
                                </Form.Group>
                            </Col>

                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Contact (Phone/Email)</Form.Label>
                                    <Form.Control
                                        name="customer_contact"
                                        value={formData.customer_contact}
                                        onChange={handleChange}
                                        required
                                    />
                                </Form.Group>
                            </Col>
                        </Row>

                        {/* CHANNEL + PRIORITY */}
                        <Row>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Channel</Form.Label>
                                    <Form.Select
                                        name="channel"
                                        value={formData.channel}
                                        onChange={handleChange}
                                    >
                                        <option value="WEB">Web</option>
                                        <option value="EMAIL">Email</option>
                                        <option value="PHONE">Phone</option>
                                        <option value="CHAT">Chat</option>
                                        <option value="WALKIN">Walk-in</option>
                                    </Form.Select>
                                </Form.Group>
                            </Col>

                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Priority</Form.Label>
                                    <Form.Select
                                        name="priority"
                                        value={formData.priority}
                                        onChange={handleChange}
                                    >
                                        <option value="LOW">Low</option>
                                        <option value="MEDIUM">Medium</option>
                                        <option value="HIGH">High</option>
                                        <option value="CRITICAL">Critical</option>
                                    </Form.Select>
                                </Form.Group>
                            </Col>
                        </Row>

                        {/* TITLE */}
                        <Form.Group className="mb-3">
                            <Form.Label>Title</Form.Label>
                            <Form.Control
                                name="title"
                                value={formData.title}
                                onChange={handleChange}
                                required
                            />
                        </Form.Group>

                        {/* DESCRIPTION */}
                        <Form.Group className="mb-3">
                            <Form.Label>Description</Form.Label>
                            <Form.Control
                                as="textarea"
                                rows={4}
                                name="description"
                                value={formData.description}
                                onChange={handleChange}
                                required
                            />
                        </Form.Group>

                        {/* SUBMIT */}
                        <Button
                            type="submit"
                            variant="primary"
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <Spinner
                                        size="sm"
                                        animation="border"
                                    /> Creating...
                                </>
                            ) : (
                                "Create Ticket"
                            )}
                        </Button>

                    </Form>

                </Card.Body>
            </Card>

        </div>
    );
};

export default CreateTicket;