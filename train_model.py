import json
import os

from github3 import login

from trains import Task


def clone_and_queue(template_task: str, queue: str) -> Task:
    payload_fname = os.getenv('GITHUB_EVENT_PATH')
    with open(payload_fname, 'r') as f:
        payload = json.load(f)

    task = Task.get_task(task_id=template_task)
    # Clone the task to pipe to. This creates a task with status Draft whose parameters can be modified.
    gh_issue_number = payload.get("issue", {}).get("number")
    cloned_task = Task.clone(
        source_task=task,
        name=f"{template_task} cloned task for github issue {gh_issue_number}"
    )
    Task.enqueue(cloned_task.id, queue_name=queue)
    owner, repo = payload.get("repository", {}).get("full_name", "").split("/")
    if owner and repo:
        gh = login(token=os.getenv("GITHUB_TOKEN"))
        if gh:
            issue = gh.issue(owner, repo, payload.get("issue", {}).get("number"))
            if issue:
                issue.create_comment(f"New task, id:{cloned_task.id} is in queue {queue_name}")
            else:
                print(f'can not comment issue, {payload.get("issue", {}).get("number")}')
        else:
            print(f"can not log in to gh, {os.getenv('GITHUB_TOKEN')}")
    return cloned_task


if __name__ == "__main__":
    # Get the user input
    base_task_id = os.getenv('INPUT_TASK_ID')
    queue_name = os.getenv('INPUT_QUEUE_NAME')
    cloned_task = clone_and_queue(template_task=base_task_id, queue=queue_name)
    print(f'::set-output name=TASK_STATUS::{cloned_task.get_status()}')
