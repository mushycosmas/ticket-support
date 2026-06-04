import React, { useEffect, useState } from "react";
import { Table, Button, Modal, Form, Badge, Spinner, Alert } from "react-bootstrap";

import {
  getRoles,
  createRole,
  updateRole,
  deleteRole,
} from "../../api/roleApi";

// =====================
// TYPES
// =====================
type Role = {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
};

type RoleForm = {
  name: string;
  description: string;
  is_active: boolean;
};

const Roles: React.FC = () => {
  // =====================
  // STATE
  // =====================
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const [show, setShow] = useState<boolean>(false);
  const [editMode, setEditMode] = useState<boolean>(false);
  const [currentId, setCurrentId] = useState<number | null>(null);

  const [formData, setFormData] = useState<RoleForm>({
    name: "",
    description: "",
    is_active: true,
  });

  // =====================
  // LOAD ROLES
  // =====================
  const loadRoles = async (): Promise<void> => {
    try {
      setLoading(true);
      setError(null);

      const res = await getRoles();
      setRoles(res.data);
    } catch (err) {
      console.error(err);
      setError("Failed to load roles");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRoles();
  }, []);

  // =====================
  // OPEN CREATE
  // =====================
  const handleCreate = (): void => {
    setEditMode(false);
    setCurrentId(null);
    setFormData({
      name: "",
      description: "",
      is_active: true,
    });
    setShow(true);
  };

  // =====================
  // OPEN EDIT
  // =====================
  const handleEdit = (role: Role): void => {
    setEditMode(true);
    setCurrentId(role.id);

    setFormData({
      name: role.name,
      description: role.description || "",
      is_active: role.is_active,
    });

    setShow(true);
  };

  // =====================
  // DELETE ROLE
  // =====================
  const handleDelete = async (id: number): Promise<void> => {
    if (!window.confirm("Delete this role?")) return;

    try {
      await deleteRole(id);
      loadRoles();
    } catch (err) {
      console.error(err);
      alert("Failed to delete role");
    }
  };

  // =====================
  // SUBMIT
  // =====================
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();

    try {
      if (editMode && currentId !== null) {
        await updateRole(currentId, formData);
      } else {
        await createRole(formData);
      }

      setShow(false);
      loadRoles();
    } catch (err) {
      console.error(err);
      alert("Failed to save role");
    }
  };

  // =====================
  // UI
  // =====================
  return (
    <div className="container-fluid p-4">

      {/* HEADER */}
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h3>Roles Management</h3>

        <Button onClick={handleCreate}>
          + Add Role
        </Button>
      </div>

      {/* ERROR */}
      {error && <Alert variant="danger">{error}</Alert>}

      {/* TABLE */}
      <div className="card shadow-sm">
        <div className="card-body">

          {loading ? (
            <div className="text-center py-4">
              <Spinner animation="border" />
            </div>
          ) : (
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
                {roles.map((r, index) => (
                  <tr key={r.id}>
                    <td>{index + 1}</td>
                    <td>{r.name}</td>
                    <td>{r.description || "-"}</td>

                    <td>
                      <Badge bg={r.is_active ? "success" : "secondary"}>
                        {r.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </td>

                    <td>
                      <Button
                        size="sm"
                        variant="warning"
                        className="me-2"
                        onClick={() => handleEdit(r)}
                      >
                        Edit
                      </Button>

                      <Button
                        size="sm"
                        variant="danger"
                        onClick={() => handleDelete(r.id)}
                      >
                        Delete
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}

        </div>
      </div>

      {/* MODAL */}
      <Modal show={show} onHide={() => setShow(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>
            {editMode ? "Edit Role" : "Create Role"}
          </Modal.Title>
        </Modal.Header>

        <Form onSubmit={handleSubmit}>
          <Modal.Body>

            <Form.Group className="mb-2">
              <Form.Label>Role Name</Form.Label>
              <Form.Control
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                required
              />
            </Form.Group>

            <Form.Group className="mb-2">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={formData.description}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    description: e.target.value,
                  })
                }
              />
            </Form.Group>

            <Form.Group>
              <Form.Check
                type="switch"
                label="Active"
                checked={formData.is_active}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    is_active: e.target.checked,
                  })
                }
              />
            </Form.Group>

          </Modal.Body>

          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShow(false)}>
              Cancel
            </Button>

            <Button type="submit">
              {editMode ? "Update" : "Save"}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

    </div>
  );
};

export default Roles;