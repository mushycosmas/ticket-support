import React, { useEffect, useState } from "react";
import { Table, Button, Modal, Form, Badge } from "react-bootstrap";

import {
  getCategories,
  createCategory,
  updateCategory,
  deleteCategory,
} from "../../api/categoryApi";

const Categories = () => {
  const [categories, setCategories] = useState([]);

  const [show, setShow] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [currentId, setCurrentId] = useState(null);

  const [formData, setFormData] = useState({
    name: "",
    description: "",
    status: "Active",
  });

  // =====================
  // LOAD DATA FROM API
  // =====================
  const fetchCategories = () => {
    getCategories()
      .then((res) => setCategories(res.data))
      .catch((err) => console.log(err));
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  // =====================
  // OPEN CREATE
  // =====================
  const handleCreate = () => {
    setEditMode(false);
    setFormData({ name: "", description: "", status: "Active" });
    setShow(true);
  };

  // =====================
  // OPEN EDIT
  // =====================
  const handleEdit = (category) => {
    setEditMode(true);
    setCurrentId(category.id);
    setFormData({
      name: category.name,
      description: category.description,
      status: category.status,
    });
    setShow(true);
  };

  // =====================
  // DELETE
  // =====================
  const handleDelete = (id) => {
    deleteCategory(id)
      .then(() => fetchCategories())
      .catch((err) => console.log(err));
  };

  // =====================
  // SUBMIT (CREATE / UPDATE)
  // =====================
  const handleSubmit = (e) => {
    e.preventDefault();

    if (editMode) {
      updateCategory(currentId, formData)
        .then(() => {
          fetchCategories();
          setShow(false);
        })
        .catch((err) => console.log(err));
    } else {
      createCategory(formData)
        .then(() => {
          fetchCategories();
          setShow(false);
        })
        .catch((err) => console.log(err));
    }
  };

  return (
    <div className="container-fluid p-4">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h3>Categories</h3>
        <Button variant="primary" onClick={handleCreate}>
          + Add Category
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
                <th>Description</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {categories.map((cat, index) => (
                <tr key={cat.id}>
                  <td>{index + 1}</td>
                  <td>{cat.name}</td>
                  <td>{cat.description}</td>
                  <td>
                    <Badge
                      bg={cat.status === "Active" ? "success" : "secondary"}
                    >
                      {cat.status}
                    </Badge>
                  </td>
                  <td>
                    <Button
                      size="sm"
                      variant="warning"
                      className="me-2"
                      onClick={() => handleEdit(cat)}
                    >
                      Edit
                    </Button>

                    <Button
                      size="sm"
                      variant="danger"
                      onClick={() => handleDelete(cat.id)}
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
            {editMode ? "Edit Category" : "Create Category"}
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
              <Form.Label>Status</Form.Label>
              <Form.Select
                value={formData.status}
                onChange={(e) =>
                  setFormData({ ...formData, status: e.target.value })
                }
              >
                <option value="Active">Active</option>
                <option value="Inactive">Inactive</option>
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

export default Categories;