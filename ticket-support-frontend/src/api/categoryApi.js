import api from "./axios";

// GET ALL
export const getCategories = () =>
  api.get("/categories/categories/");

// CREATE
export const createCategory = (data) =>
  api.post("/categories/categories/", data);

// UPDATE
export const updateCategory = (id, data) =>
  api.put(`/categories/categories/${id}/`, data);

// DELETE
export const deleteCategory = (id) =>
  api.delete(`/categories/categories/${id}/`);