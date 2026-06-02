import React, { useEffect, useState } from "react";
import { Card, Table, Button, Badge, Spinner } from "react-bootstrap";

import { getTickets, deleteTicket } from "../api/ticketApi";

import CreateTicketModal from "../components/tickets/CreateTicketModal";
import TicketViewModal from "../components/tickets/TicketViewModal";
import ConfirmModal from "../components/common/ConfirmModal";

const Tickets = () => {

    const [tickets, setTickets] = useState([]);
    const [loading, setLoading] = useState(true);

    const [showCreate, setShowCreate] = useState(false);
    const [showView, setShowView] = useState(false);

    const [selectedTicket, setSelectedTicket] = useState(null);

    // NEW: delete modal state
    const [showDelete, setShowDelete] = useState(false);
    const [deleteId, setDeleteId] = useState(null);

    const loadTickets = async () => {
        setLoading(true);
        const res = await getTickets();
        setTickets(res.data);
        setLoading(false);
    };

    useEffect(() => {
        loadTickets();
    }, []);

    // open confirm modal
    const confirmDelete = (id) => {
        setDeleteId(id);
        setShowDelete(true);
    };

    // actual delete
    const handleDelete = async () => {
        await deleteTicket(deleteId);
        setDeleteId(null);
        loadTickets();
    };

    return (
        <div className="container-fluid mt-4">

            {/* HEADER */}
            <Card className="mb-3">
                <Card.Body className="d-flex justify-content-between">

                    <h4>Tickets</h4>

                    <Button onClick={() => setShowCreate(true)}>
                        + Create Ticket
                    </Button>

                </Card.Body>
            </Card>

            {/* TABLE */}
            <Card>
                <Card.Body>

                    {loading ? (
                        <Spinner />
                    ) : (
                        <Table striped bordered hover>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Customer</th>
                                    <th>Title</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>

                            <tbody>
                                {tickets.map(t => (
                                    <tr key={t.id}>

                                        <td>{t.id}</td>
                                        <td>{t.customer_name}</td>
                                        <td>{t.title}</td>

                                        <td>
                                            <Badge bg="info">
                                                {t.status}
                                            </Badge>
                                        </td>

                                        <td>

                                            <Button
                                                size="sm"
                                                className="me-2"
                                                onClick={() => {
                                                    setSelectedTicket(t);
                                                    setShowView(true);
                                                }}
                                            >
                                                View
                                            </Button>

                                            <Button
                                                size="sm"
                                                variant="danger"
                                                onClick={() => confirmDelete(t.id)}
                                            >
                                                Delete
                                            </Button>

                                        </td>

                                    </tr>
                                ))}
                            </tbody>

                        </Table>
                    )}

                </Card.Body>
            </Card>

            {/* MODALS */}
            <CreateTicketModal
                show={showCreate}
                onHide={() => setShowCreate(false)}
                onSuccess={loadTickets}
            />

            <TicketViewModal
                show={showView}
                onHide={() => setShowView(false)}
                ticket={selectedTicket}
                onRefresh={loadTickets}
            />

            {/* DELETE CONFIRM MODAL */}
            <ConfirmModal
                show={showDelete}
                onHide={() => setShowDelete(false)}
                title="Delete Ticket"
                message="Are you sure you want to delete this ticket? This action cannot be undone."
                onConfirm={handleDelete}
            />

        </div>
    );
};

export default Tickets;