import hud
from datasets import load_from_disk, Dataset as VerifiersDataset
from hud.datasets import save_tasks

dataset = load_from_disk("./minesweeper_taskset")
verifiers_dataset = VerifiersDataset.from_dict({
    "question": dataset["prompt"],
    "task": dataset["id"],
    "answer": ["" for _ in range(len(dataset))],  # No specific answers for minesweeper
    "info": [
        {
            "mcp_config": dataset[i]["mcp_config"],
            "setup_tool": dataset[i]["setup_tool"],
            "evaluate_tool": dataset[i]["evaluate_tool"],
            "metadata": dataset[i]["metadata"]
        }
        for i in range(len(dataset))
    ]
})

save_tasks(verifiers_dataset, "kizro/minesweeper_taskset")
