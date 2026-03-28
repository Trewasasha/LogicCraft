from typing import List, Dict, Optional
from .diagram import UMLDiagram, UMLConnection, ConnectionType


class ValidationError:
    """Ошибка валидации"""
    def __init__(self, message: str, severity: str = "error"):
        self.message = message
        self.severity = severity


class DiagramEngine:
    """Движок для работы с диаграммами"""

    def __init__(self):
        self.diagram: Optional[UMLDiagram] = None

    def load_diagram(self, diagram: UMLDiagram):
        """Загрузить диаграмму в движок"""
        self.diagram = diagram

    def validate(self) -> List[ValidationError]:
        """Валидация диаграммы"""
        errors = []

        if not self.diagram:
            errors.append(ValidationError("No diagram loaded"))
            return errors

        node_ids = {node.id for node in self.diagram.nodes}

        for conn in self.diagram.connections:
            # Проверяем существование узлов
            if conn.source_id not in node_ids:
                errors.append(ValidationError(
                    f"Connection {conn.id}: source node {conn.source_id} not found"
                ))
            if conn.target_id not in node_ids:
                errors.append(ValidationError(
                    f"Connection {conn.id}: target node {conn.target_id} not found"
                ))

            # Проверяем валидность типа связи
            if conn.type not in ConnectionType:
                errors.append(ValidationError(
                    f"Connection {conn.id}: invalid connection type {conn.type}"
                ))

        # Проверяем циклические зависимости
        cycles = self._detect_cycles()
        for cycle in cycles:
            errors.append(ValidationError(
                f"Cyclic dependency detected: {' -> '.join(cycle)}",
                severity="warning"
            ))

        return errors

    def _detect_cycles(self) -> List[List[str]]:
        """Обнаружение циклических зависимостей"""
        if not self.diagram:
            return []

        # Строим граф зависимостей
        graph = {node.id: [] for node in self.diagram.nodes}
        for conn in self.diagram.connections:
            if conn.type == ConnectionType.inheritance:
                graph[conn.source_id].append(conn.target_id)

        # Поиск циклов (упрощенная версия)
        cycles = []
        visited = set()
        path = []

        def dfs(node):
            if node in path:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            if node in visited:
                return

            visited.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                dfs(neighbor)

            path.pop()

        for node in graph:
            if node not in visited:
                dfs(node)

        return cycles

    def get_node_statistics(self) -> Dict:
        """Получить статистику по узлам"""
        if not self.diagram:
            return {}

        stats = {
            "total_classes": len(self.diagram.nodes),
            "abstract_classes": 0,
            "total_attributes": 0,
            "total_methods": 0,
            "avg_attributes": 0,
            "avg_methods": 0
        }

        for node in self.diagram.nodes:
            if node.is_abstract:
                stats["abstract_classes"] += 1
            stats["total_attributes"] += len(node.properties)
            stats["total_methods"] += len(node.methods)

        if stats["total_classes"] > 0:
            stats["avg_attributes"] = stats["total_attributes"] / stats["total_classes"]
            stats["avg_methods"] = stats["total_methods"] / stats["total_classes"]

        return stats

    def get_connection_statistics(self) -> Dict:
        """Получить статистику по связям"""
        if not self.diagram:
            return {}

        stats = {
            "total_connections": len(self.diagram.connections),
            "by_type": {}
        }

        for conn_type in ConnectionType:
            stats["by_type"][conn_type.value] = 0

        for conn in self.diagram.connections:
            stats["by_type"][conn.type.value] += 1

        return stats