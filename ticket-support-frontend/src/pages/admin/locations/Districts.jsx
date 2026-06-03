import React, { useEffect, useState } from "react";
import {
    getDistricts,
    createDistrict,
    updateDistrict,
    deleteDistrict,
    getRegions,
} from "../../../api/locationApi";

import { Modal, Button, Form, Table } from "react-bootstrap";

const Districts = () => {
    const [districts, setDistricts] = useState([]);
    const [regions, setRegions] = useState([]);

    const [show, setShow] = useState(false);
    const [editingId, setEditingId] = useState(null);

    const [name, setName] = useState("");
    const [region, setRegion] = useState("");

    // LOAD DATA
    const loadDistricts = () => {
        getDistricts().then((res) => setDistricts(res.data));
    };

    useEffect(() => {
        loadDistricts();
        getRegions().then((res) => setRegions(res.data));
    }, []);

    // MODAL
    const handleShow = (item = null) => {
        if (item) {
            setEditingId(item.id);
            setName(item.name);
            setRegion(item.region);
        } else {
            setEditingId(null);
            setName("");
            setRegion("");
        }
        setShow(true);
    };

    const handleClose = () => {
        setShow(false);
        setName("");
        setRegion("");
        setEditingId(null);
    };

    // SAVE
    const handleSave = () => {
        const data = { name, region };

        if (editingId) {
            updateDistrict(editingId, data).then(() => {
                loadDistricts();
                handleClose();
            });
        } else {
            createDistrict(data).then(() => {
                loadDistricts();
                handleClose();
            });
        }
    };

    // DELETE
    const handleDelete = (id) => {
        if (window.confirm("Delete this district?")) {
            deleteDistrict(id).then(() => loadDistricts());
        }
    };

    return (
        <div className="container mt-3">
            <div className="d-flex justify-content-between mb-3">
                <h3>Districts</h3>
                <Button onClick={() => handleShow()}>
                    + Add District
                </Button>
            </div>

            <Table bordered hover>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>District</th>
                        <th>Region</th>
                        <th>Actions</th>
                    </tr>
                </thead>

                <tbody>
                    {districts.map((d, i) => (
                        <tr key={d.id}>
                            <td>{i + 1}</td>
                            <td>{d.name}</td>
                            <td>{d.region}</td>
                            <td>
                                <Button
                                    size="sm"
                                    variant="warning"
                                    className="me-2"
                                    onClick={() => handleShow(d)}
                                >
                                    Edit
                                </Button>

                                <Button
                                    size="sm"
                                    variant="danger"
                                    onClick={() => handleDelete(d.id)}
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
                        {editingId ? "Edit District" : "Add District"}
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
                            <Form.Label>Region</Form.Label>
                            <Form.Select
                                value={region}
                                onChange={(e) => setRegion(e.target.value)}
                            >
                                <option value="">Select Region</option>
                                {regions.map((r) => (
                                    <option key={r.id} value={r.id}>
                                        {r.name}
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

export default Districts;