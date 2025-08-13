import React, { useState, useEffect } from "react";

const TaskForm = ({ onSubmit, initialData, onCancel, isEditing }) => {
  const [formData, setFormData] = useState({
    titulo: "",
    descricao: "",
  });

  useEffect(() => {
    if (initialData) {
      setFormData({
        titulo: initialData.titulo || "",
        descricao: initialData.descricao || "",
      });
    } else {
      setFormData({
        titulo: "",
        descricao: "",
      });
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!formData.titulo.trim()) {
      alert("Por favor, insira um título para a tarefa");
      return;
    }

    onSubmit(formData);

    if (!isEditing) {
      setFormData({
        titulo: "",
        descricao: "",
      });
    }
  };

  return (
    <form
      className="task-form"
      onSubmit={handleSubmit}
    >
      <h2>{isEditing ? "Editar Tarefa" : "Nova Tarefa"}</h2>

      <div className="form-group">
        <label htmlFor="titulo">Título *</label>
        <input
          type="text"
          id="titulo"
          name="titulo"
          value={formData.titulo}
          onChange={handleChange}
          placeholder="Digite o título da tarefa"
          maxLength={200}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="descricao">Descrição</label>
        <textarea
          id="descricao"
          name="descricao"
          value={formData.descricao}
          onChange={handleChange}
          placeholder="Digite uma descrição opcional para a tarefa"
          maxLength={1000}
        />
      </div>

      <div>
        <button
          type="submit"
          className="btn btn-primary"
        >
          {isEditing ? "💾 Salvar Alterações" : "➕ Adicionar Tarefa"}
        </button>

        {isEditing && (
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onCancel}
          >
            ❌ Cancelar
          </button>
        )}
      </div>
    </form>
  );
};

export default TaskForm;
