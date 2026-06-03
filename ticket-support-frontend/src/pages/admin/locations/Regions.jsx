import React, { useEffect, useState } from "react";
import {
    getRegions,
    createRegion,
    updateRegion,
    deleteRegion,
} from "../../../api/locationApi";

import { Modal, Button, Form, Table } from "react-bootstrap";

const Regions = () => {
    const [regions, setRegions] = useState([]);
    const [show, setShow] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [name, setName] = useState("");

    // =====================
    // LOAD REGIONS
    // =====================
    const loadRegions = () => {
        getRegions()
            .then((res) => setRegions(res.data))
            .catch((err) => console.error(err));
    };

    useEffect(() => {
        loadRegions();
    }, []);

    // =====================
    // OPEN MODAL
    // =====================
    const handleShow = (region = null) => {
        if (region) {
            setEditingId(region.id);
            setName(region.name);
        } else {
            setEditingId(null);
            setName("");
        }
        setShow(true);
    };

    const handleClose = () => {
        setShow(false);
        setName("");
        setEditingId(null);
    };

    // =====================
    // SAVE REGION
    // =====================
    const handleSave = () => {
        const data = { name };

        if (editingId) {
            updateRegion(editingId, data)
                .then(() => {
                    loadRegions();
                    handleClose();
                })
                .catch((err) => console.error(err));
        } else {
            createRegion(data)
                .then(() => {
                    loadRegions();
                    handleClose();
                })
                .catch((err) => console.error(err));
        }
    };

    // =====================
    // DELETE REGION
    // =====================
    const handleDelete = (id) => {
        if (window.confirm("Are you sure you want to delete this region?")) {
            deleteRegion(id)
                .then(() => loadRegions())
                .catch((err) => console.error(err));
        }
    };

    return (
        <div className="container mt-3">
            <div className="d-flex justify-content-between align-items-center mb-3">
                <h3>Regions</h3>
                <Button onClick={() => handleShow()}>
                    + Add Region
                </Button>
            </div>

            {/* TABLE */}
            <Table bordered hover>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Region Name</th>
                        <th width="200">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {regions.map((region, index) => (
                        <tr key={region.id}>
                            <td>{index + 1}</td>
                            <td>{region.name}</td>
                            <td>
                                <Button
                                    size="sm"
                                    variant="warning"
                                    className="me-2"
                                    onClick={() => handleShow(region)}
                                >
                                    Edit
                                </Button>

                                <Button
                                    size="sm"
                                    variant="danger"
                                    onClick={() =>
                                        handleDelete(region.id)
                                    }
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
                        {editingId ? "Edit Region" : "Add Region"}
                    </Modal.Title>
                </Modal.Header>

                <Modal.Body>
                    <Form>
                        <Form.Group>
                            <Form.Label>Region Name</Form.Label>
                            <Form.Control
                                type="text"
                                value={name}
                                onChange={(e) =>
                                    setName(e.target.value)
                                }
                                placeholder="Enter region name"
                            />
                        </Form.Group>
                    </Form>
                </Modal.Body>

                <Modal.Footer>
                    <Button variant="secondary" onClick={handleClose}>
                        Cancel
                    </Button>
                    <Button variant="primary" onClick={handleSave}>
                        {editingId ? "Update" : "Save"}
                    </Button>
                </Modal.Footer>
            </Modal>
        </div>
    );
};

export default Regions;