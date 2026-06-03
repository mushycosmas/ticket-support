import React, { useEffect, useState } from "react";
import { Table, Button, Modal, Form, Badge } from "react-bootstrap";

import {
  getPriorities,
  createPriority,
  updatePriority,
  deletePriority,
} from "../../api/priorityApi";

const Priorities = () => {
  const [priorities, setPriorities] = useState([]);

  const [show, setShow] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [currentId, setCurrentId] = useState(null);

  const [formData, setFormData] = useState({
    name: "",
    level: "",
    description: "",
    color: "secondary",
  });

  // =====================
  // LOAD DATA
  // =====================
  const fetchPriorities = () => {
    getPriorities()
      .then((res) => setPriorities(res.data))
      .catch((err) => console.log(err));
  };

  useEffect(() => {
    fetchPriorities();
  }, []);

  // =====================
  // CREATE
  // =====================
  const handleCreate = () => {
    setEditMode(false);
    setFormData({
      name: "",
      level: "",
      description: "",
      color: "secondary",
    });
    setShow(true);
  };

  // =====================
  // EDIT
  // =====================
  const handleEdit = (priority) => {
    setEditMode(true);
    setCurrentId(priority.id);
    setFormData({
      name: priority.name,
      level: priority.level,
      description: priority.description,
      color: priority.color,
    });
    setShow(true);
  };

  // =====================
  // DELETE
  // =====================
  const handleDelete = (id) => {
    deletePriority(id)
      .then(() => fetchPriorities())
      .catch((err) => console.log(err));
  };

  // =====================
  // SUBMIT
  // =====================
  const handleSubmit = (e) => {
    e.preventDefault();

    if (editMode) {
      updatePriority(currentId, formData)
        .then(() => {
          fetchPriorities();
          setShow(false);
        })
        .catch((err) => console.log(err));
    } else {
      createPriority(formData)
        .then(() => {
          fetchPriorities();
          setShow(false);
        })
        .catch((err) => console.log(err));
    }
  };

  return (
    <div className="container-fluid p-4">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h3>Priorities</h3>
        <Button variant="primary" onClick={handleCreate}>
          + Add Priority
        </Button>
      </div>

      {/* Table */}
      <div className="card shadow-sm">
        <div className="card-body">
          <Table striped hover responsive>
            <thead>
              <tr>
                <th>#</th>
                <th>Name</th>
                <th>Level</th>
                <th>Description</th>
                <th>Indicator</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {priorities
                .sort((a, b) => a.level - b.level)
                .map((p, index) => (
                  <tr key={p.id}>
                    <td>{index + 1}</td>
                    <td>{p.name}</td>
                    <td>{p.level}</td>
                    <td>{p.description}</td>
                    <td>
                      <Badge bg={p.color}>
                        {p.name}
                      </Badge>
                    </td>
                    <td>
                      <Button
                        size="sm"
                        variant="warning"
                        className="me-2"
                        onClick={() => handleEdit(p)}
                      >
                        Edit
                      </Button>

                      <Button
                        size="sm"
                        variant="danger"
                        onClick={() => handleDelete(p.id)}
                      >
                        Delete
                      </Button>
                    </td>
                  </tr>
                ))}
            </tbody>
          </Table>
        </div>
      </div>

      {/* Modal */}
      <Modal show={show} onHide={() => setShow(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>
            {editMode ? "Edit Priority" : "Create Priority"}
          </Modal.Title>
        </Modal.Header>

        <Form onSubmit={handleSubmit}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Name</Form.Label>
              <Form.Control
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                required
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Level</Form.Label>
              <Form.Control
                type="number"
                value={formData.level}
                onChange={(e) =>
                  setFormData({ ...formData, level: e.target.value })
                }
                required
              />
              <Form.Text>
                Lower number = higher priority
              </Form.Text>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
              />
            </Form.Group>

            <Form.Group>
              <Form.Label>Color</Form.Label>
              <Form.Select
                value={formData.color}
                onChange={(e) =>
                  setFormData({ ...formData, color: e.target.value })
                }
              >
                <option value="secondary">Secondary</option>
                <option value="info">Info</option>
                <option value="warning">Warning</option>
                <option value="danger">Danger</option>
                <option value="success">Success</option>
              </Form.Select>
            </Form.Group>
          </Modal.Body>

          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShow(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary">
              {editMode ? "Update" : "Save"}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </div>
  );
};

export default Priorities;