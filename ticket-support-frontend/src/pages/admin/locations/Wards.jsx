import React, { useEffect, useState } from "react";
import {
    getWards,
    createWard,
    updateWard,
    deleteWard,
    getDistricts,
} from "../../../api/locationApi";

import { Modal, Button, Form, Table } from "react-bootstrap";

const Wards = () => {
    const [wards, setWards] = useState([]);
    const [districts, setDistricts] = useState([]);

    const [show, setShow] = useState(false);
    const [editingId, setEditingId] = useState(null);

    const [name, setName] = useState("");
    const [district, setDistrict] = useState("");

    // LOAD
    const loadWards = () => {
        getWards().then((res) => setWards(res.data));
    };

    useEffect(() => {
        loadWards();
        getDistricts().then((res) => setDistricts(res.data));
    }, []);

    // MODAL
    const handleShow = (item = null) => {
        if (item) {
            setEditingId(item.id);
            setName(item.name);
            setDistrict(item.district);
        } else {
            setEditingId(null);
            setName("");
            setDistrict("");
        }
        setShow(true);
    };

    const handleClose = () => {
        setShow(false);
        setName("");
        setDistrict("");
        setEditingId(null);
    };

    // SAVE
    const handleSave = () => {
        const data = { name, district };

        if (editingId) {
            updateWard(editingId, data).then(() => {
                loadWards();
                handleClose();
            });
        } else {
            createWard(data).then(() => {
                loadWards();
                handleClose();
            });
        }
    };

    // DELETE
    const handleDelete = (id) => {
        if (window.confirm("Delete this ward?")) {
            deleteWard(id).then(() => loadWards());
        }
    };

    return (
        <div className="container mt-3">
            <div className="d-flex justify-content-between mb-3">
                <h3>Wards</h3>
                <Button onClick={() => handleShow()}>
                    + Add Ward
                </Button>
            </div>

            <Table bordered hover>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Ward</th>
                        <th>District</th>
                        <th>Actions</th>
                    </tr>
                </thead>

                <tbody>
                    {wards.map((w, i) => (
                        <tr key={w.id}>
                            <td>{i + 1}</td>
                            <td>{w.name}</td>
                            <td>{w.district}</td>
                            <td>
                                <Button
                                    size="sm"
                                    variant="warning"
                                    className="me-2"
                                    onClick={() => handleShow(w)}
                                >
                                    Edit
                                </Button>

                                <Button
                                    size="sm"
                                    variant="danger"
                                    onClick={() => handleDelete(w.id)}
                                >
                                    Delete
                                </Button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </Table>

            {/* MODAL */}
            <Modal show={show} onHide={handleClose}>
                <Modal.Header closeButton>
                    <Modal.Title>
                        {editingId ? "Edit Ward" : "Add Ward"}
                    </Modal.Title>
                </Modal.Header>

                <Modal.Body>
                    <Form>
                        <Form.Group className="mb-2">
                            <Form.Label>Name</Form.Label>
                            <Form.Control
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                            />
                        </Form.Group>

                        <Form.Group>
                            <Form.Label>District</Form.Label>
                            <Form.Select
                                value={district}
                                onChange={(e) => setDistrict(e.target.value)}
                            >
                                <option value="">Select District</option>
                                {districts.map((d) => (
                                    <option key={d.id} value={d.id}>
                                        {d.name}
                                    </option>
                                ))}
                            </Form.Select>
                        </Form.Group>
                    </Form>
                </Modal.Body>

                <Modal.Footer>
                    <Button variant="secondary" onClick={handleClose}>
                        Close
                    </Button>
                    <Button onClick={handleSave}>Save</Button>
                </Modal.Footer>
            </Modal>
        </div>
    );
};

export default Wards;