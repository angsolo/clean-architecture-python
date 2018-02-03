
from datetime import datetime
from pytest import fixture, raises
from taskit.application.models.project import Project
from taskit.application.models.task import Task
from taskit.application.repositories.project_repository import (
    ProjectRepository, MemoryProjectRepository)
from taskit.application.repositories.task_repository import (
    TaskRepository, MemoryTaskRepository)
from taskit.application.repositories.errors import EntityNotFoundError
from taskit.application.coordinators.agenda_coordinator import (
    AgendaCoordinator)


@fixture
def project_repository() -> MemoryProjectRepository:
    project_repository = MemoryProjectRepository()
    projects_dict = {
        'P-1': Project("Personal"),
        'P-2': Project("Work"),
        'P-3': Project("Errands")
    }
    project_repository.sequence = 4
    project_repository.load(projects_dict)
    return project_repository


@fixture
def task_repository() -> MemoryTaskRepository:
    task_repository = MemoryTaskRepository()
    tasks_dict = {
        'T-1': Task("Buy the milk"),
        'T-2': Task("Make conference presentation"),
        'T-3': Task("Clean the kitchen")
    }
    task_repository.sequence = 4
    task_repository.load(tasks_dict)
    return task_repository


@fixture
def agenda_coordinator(
        project_repository: ProjectRepository,
        task_repository: TaskRepository) -> AgendaCoordinator:
    return AgendaCoordinator(project_repository, task_repository)


def test_agenda_coordinator_creation(
        agenda_coordinator: AgendaCoordinator) -> None:
    assert hasattr(agenda_coordinator, 'create_task')
    assert hasattr(agenda_coordinator, 'start_task')
    assert hasattr(agenda_coordinator, 'complete_task')


def test_aqenda_coordinator_create_task(
        agenda_coordinator: AgendaCoordinator) -> None:
    task_dict = {
        'name': "Buy bread and eggs",
        'due_date':  datetime.strptime("2018-02-15", '%Y-%m-%d'),
        'priority': 3,
        'project_id': "P-1",
        'comments': "The supermarket closes at 8 pm."
    }

    agenda_coordinator.create_task(task_dict)

    task_repository = agenda_coordinator.task_repository
    task = task_repository.get('T-4')
    assert task.name == task_dict['name']
    assert task.project_id == task_dict['project_id']
    assert task.stage == 'New'


def test_agenda_coordinator_create_task_missing_project(
        agenda_coordinator: AgendaCoordinator) -> None:
    task_dict = {
        'name': "Buy bread and eggs",
        'project_id': "MISSING"
    }
    with raises(EntityNotFoundError):
        agenda_coordinator.create_task(task_dict)


def test_agenda_coordinator_start_task(
        agenda_coordinator: AgendaCoordinator) -> None:
    task_dict = {
        'name': 'Buy the milk',
        'uid': 'T-1'
    }
    agenda_coordinator.start_task(task_dict)
    task = agenda_coordinator.task_repository.get('T-1')
    assert task.stage == 'Progress'


def test_agenda_coordinator_complete_task(
        agenda_coordinator: AgendaCoordinator) -> None:
    task_dict = {
        'name': 'Buy the milk',
        'uid': 'T-1'
    }
    agenda_coordinator.complete_task(task_dict)
    task = agenda_coordinator.task_repository.get('T-1')
    assert task.stage == 'Done'
