import React from "react";
import TaskItem from "./TaskItem";

const TaskList = ({ tasks, loading, onEdit, onDelete, onToggleStatus }) => {
  if (loading) {
    return <div className="loading">⏳ Carregando tarefas...</div>;
  }

  if (tasks.length === 0) {
    return (
      <div className="empty-state">
        <h3>📋 Nenhuma tarefa encontrada</h3>
        <p>Que tal adicionar sua primeira tarefa?</p>
      </div>
    );
  }

  // Separa tarefas pendentes e concluídas
  const pendingTasks = tasks.filter((task) => task.status === "pendente");
  const completedTasks = tasks.filter((task) => task.status === "concluida");

  return (
    <div>
      {pendingTasks.length > 0 && (
        <div>
          <h2>📝 Tarefas Pendentes ({pendingTasks.length})</h2>
          <div className="task-list">
            {pendingTasks.map((task) => (
              <TaskItem
                key={task.id}
                task={task}
                onEdit={onEdit}
                onDelete={onDelete}
                onToggleStatus={onToggleStatus}
              />
            ))}
          </div>
        </div>
      )}

      {completedTasks.length > 0 && (
        <div style={{ marginTop: "30px" }}>
          <h2>✅ Tarefas Concluídas ({completedTasks.length})</h2>
          <div className="task-list">
            {completedTasks.map((task) => (
              <TaskItem
                key={task.id}
                task={task}
                onEdit={onEdit}
                onDelete={onDelete}
                onToggleStatus={onToggleStatus}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TaskList;
