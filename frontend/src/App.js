import React, { useState, useEffect } from "react";
import TaskForm from "./components/TaskForm";
import TaskList from "./components/TaskList";
import { taskApi } from "./services/api";

function App() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingTask, setEditingTask] = useState(null);

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const data = await taskApi.getTasks();
      setTasks(data);
      setError(null);
    } catch (err) {
      setError("Erro ao carregar tarefas");
      console.error("Error loading tasks:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async (taskData) => {
    try {
      const newTask = await taskApi.createTask(taskData);
      setTasks((prev) => [newTask, ...prev]);
      setError(null);
    } catch (err) {
      setError("Erro ao criar tarefa");
      console.error("Error creating task:", err);
    }
  };

  const handleUpdateTask = async (taskId, taskData) => {
    try {
      const updatedTask = await taskApi.updateTask(taskId, taskData);
      setTasks((prev) =>
        prev.map((task) => (task.id === taskId ? updatedTask : task))
      );
      setEditingTask(null);
      setError(null);
    } catch (err) {
      setError("Erro ao atualizar tarefa");
      console.error("Error updating task:", err);
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm("Tem certeza que deseja deletar esta tarefa?")) {
      return;
    }

    try {
      await taskApi.deleteTask(taskId);
      setTasks((prev) => prev.filter((task) => task.id !== taskId));
      setError(null);
    } catch (err) {
      setError("Erro ao deletar tarefa");
      console.error("Error deleting task:", err);
    }
  };

  const handleToggleStatus = async (taskId) => {
    const task = tasks.find((t) => t.id === taskId);
    if (!task) return;

    const newStatus = task.status === "pendente" ? "concluida" : "pendente";

    try {
      const updatedTask = await taskApi.updateTask(taskId, {
        status: newStatus,
      });
      setTasks((prev) => prev.map((t) => (t.id === taskId ? updatedTask : t)));
      setError(null);
    } catch (err) {
      setError("Erro ao atualizar status da tarefa");
      console.error("Error updating task status:", err);
    }
  };

  return (
    <div className="container">
      <header className="header">
        <h1>📝 Gerenciador de Tarefas</h1>
        <p>Organize suas tarefas de forma simples e eficiente</p>
      </header>

      {error && <div className="error">{error}</div>}

      <TaskForm
        onSubmit={
          editingTask
            ? (data) => handleUpdateTask(editingTask.id, data)
            : handleCreateTask
        }
        initialData={editingTask}
        onCancel={() => setEditingTask(null)}
        isEditing={!!editingTask}
      />

      <TaskList
        tasks={tasks}
        loading={loading}
        onEdit={setEditingTask}
        onDelete={handleDeleteTask}
        onToggleStatus={handleToggleStatus}
      />
    </div>
  );
}

export default App;
