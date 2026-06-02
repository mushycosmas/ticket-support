import React, { useEffect, useState } from "react";
import { Modal, Button, Form } from "react-bootstrap";
import { createTeam, updateTeam } from "../../api/teamApi";

const TeamFormModal = ({ show, onHide, team, onSuccess }) => {

    const [form, setForm] = useState({
        name: "",
        description: ""
    });

    useEffect(() => {
        if (team) {
            setForm({
                name: team.name || "",
                description: team.description || ""
            });
        } else {
            setForm({ name: "", description: "" });
        }
    }, [team]);

    const handleSubmit = async () => {
        if (team) {
            await updateTeam(team.id, form);
        } else {
            await createTeam(form);
        }

        onSuccess();
        onHide();
    };

    return (
        <Modal show={show} onHide={onHide}>
            <Modal.Header closeButton>
                <Modal.Title>
                    {team ? "Edit Team" : "Create Team"}
                </Modal.Title>
            </Modal.Header>

            <Modal.Body>
                <Form>

                    <Form.Group className="mb-3">
                        <Form.Label>Name</Form.Label>
                        <Form.Control
                            value={form.name}
                            onChange={(e) =>
                                setForm({ ...form, name: e.target.value })
                            }
                        />
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label>Description</Form.Label>
                        <Form.Control
                            as="textarea"
                            rows={3}
                            value={form.description}
                            onChange={(e) =>
                                setForm({ ...form, description: e.target.value })
                            }
                        />
                    </Form.Group>

                </Form>
            </Modal.Body>

            <Modal.Footer>
                <Button variant="secondary" onClick={onHide}>
                    Cancel
                </Button>

                <Button variant="primary" onClick={handleSubmit}>
                    Save
                </Button>
            </Modal.Footer>
        </Modal>
    );
};

export default TeamFormModal;