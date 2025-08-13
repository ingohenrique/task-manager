import React from "react";

const TaskItem = ({ task, onEdit, onDelete, onToggleStatus }) => {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("pt-BR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const isCompleted = task.status === "concluida";

  return (
    <div className={`task-item ${isCompleted ? "completed" : ""}`}>
      <div className="task-header">
        <input
          type="checkbox"
          className="task-checkbox"
          checked={isCompleted}
          onChange={() => onToggleStatus(task.id)}
        />
        <h3 className={`task-title ${isCompleted ? "completed" : ""}`}>
          {task.titulo}
        </h3>
      </div>

      {task.descricao && <p className="task-description">{task.descricao}</p>}

      <div className="task-meta">
        <span>Criada em: {formatDate(task.data_criacao)}</span>
        <span className={`task-status ${task.status}`}>
          {task.status === "pendente" ? "⏳ Pendente" : "✅ Concluída"}
        </span>
      </div>

      {task.data_atualizacao && task.status === "concluida" && (
        <div
          className="task-meta"
          style={{ marginTop: "5px" }}
        >
          <span>Concluída em: {formatDate(task.data_atualizacao)}</span>
        </div>
      )}

      <div className="task-actions">
        <button
          className="btn btn-primary"
          onClick={() => onEdit(task)}
          style={{ fontSize: "12px", padding: "6px 12px" }}
        >
          ✏️ Editar
        </button>
        <button
          className="btn btn-danger"
          onClick={() => onDelete(task.id)}
          style={{ fontSize: "12px", padding: "6px 12px" }}
        >
          🗑️ Deletar
        </button>
      </div>
    </div>
  );
};

export default TaskItem;
