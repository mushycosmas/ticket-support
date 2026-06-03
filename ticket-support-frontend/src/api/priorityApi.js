import api from "./axios";

// GET ALL
export const getPriorities = () =>
    api.get("/priorities/");

// CREATE
export const createPriority = (data) =>
    api.post("/priorities/", data);

// UPDATE
export const updatePriority = (id, data) =>
    api.put(`/priorities/${id}/`, data);

// DELETE
export const deletePriority = (id) =>
    api.delete(`/priorities/${id}/`);