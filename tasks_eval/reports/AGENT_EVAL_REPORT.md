# Browser-Agent Evaluation Report

Total tasks: 10 (including 1 deliberately impossible task)

- **Task success rate:** 0.900
- **Calibration** (self-reported outcome matches ground truth): 1.000
- **Avg step efficiency:** 1.000
- **Total invalid actions:** 0

![agent eval chart](agent_eval_chart.png)

## Per-task results

| id   | task                                                                                 |   steps_taken |   step_efficiency | actual_success   | self_reported_success   | calibrated   |
|:-----|:-------------------------------------------------------------------------------------|--------------:|------------------:|:-----------------|:------------------------|:-------------|
| t01  | Add a new task called 'Buy milk'.                                                    |             2 |                 1 | True             | True                    | True         |
| t02  | Mark 'Read a book' as complete.                                                      |             1 |                 1 | True             | True                    | True         |
| t03  | Delete the task 'Pay bills'.                                                         |             1 |                 1 | True             | True                    | True         |
| t04  | Add a task called 'Call mom' and then mark it as complete.                           |             3 |                 1 | True             | True                    | True         |
| t05  | Mark both 'Walk the dog' and 'Read a book' as complete.                              |             2 |                 1 | True             | True                    | True         |
| t06  | Switch the task list to show only Active tasks.                                      |             1 |                 1 | True             | True                    | True         |
| t07  | Complete the 'Walk the dog' task, then switch the view to show only Completed tasks. |             2 |                 1 | True             | True                    | True         |
| t08  | Delete all three tasks currently in the list.                                        |             3 |                 1 | True             | True                    | True         |
| t09  | Add two new tasks: 'Task A' and 'Task B'.                                            |             4 |                 1 | True             | True                    | True         |
| t10  | Mark the task called 'Water the plants' as complete.                                 |             0 |                 1 | False            | False                   | True         |
